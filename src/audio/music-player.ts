import { midiToHz, type Instrument, type MusicEffects, type Track } from './audio-types';
import { Sequencer } from './sequencer';
import { playVoice, type Voice } from './synth';
import { TrackMixer, type MusicBus } from './track-mixer';

export type { MusicBus } from './track-mixer';

/** Timings of a {@link MusicPlayer} (`config/audio.ts`). */
export interface MusicTimings {
  readonly lookaheadSeconds: number;
  /** How fast the notes still sounding go quiet when the game pauses. */
  readonly pauseFadeSeconds: number;
}

/** A track playing (or fading out), on its own mixer into the music bus. */
interface Slot {
  readonly track: Track;
  readonly sequencer: Sequencer;
  mixer: TrackMixer | undefined;
  /** Audio time of the track's start; undefined until the context exists. */
  anchor: number | undefined;
  voices: Voice[];
  /** Fades to this level (1 in, 0 out) over `fade` seconds once it starts. */
  target: number;
  fade: number;
  /** Audio time it is over (faded out), if it is fading out. */
  until: number | undefined;
}

/**
 * Plays the generated music (P12-R05..R08, P12-R11): one track at a time, cross-fading into the
 * next or fading out, plus one-shot jingles over it. Notes are scheduled ahead on the audio clock
 * by {@link update}, so the music keeps time when frames are slow. Pausing keeps each track's
 * position; resuming goes on from there.
 */
export class MusicPlayer {
  #current: Slot | undefined;
  #others: Slot[] = [];
  #paused = false;
  /** Seconds into each track where it was paused. */
  readonly #pausedAt = new Map<Slot, number>();

  constructor(
    private readonly bus: () => MusicBus | undefined,
    private readonly instruments: Readonly<Record<string, Instrument>>,
    private readonly timings: MusicTimings,
    /** The tracks' echo and reverb; dry when omitted. */
    private readonly effects?: MusicEffects,
  ) {}

  /** The track playing (not a jingle), if any. */
  get track(): Track | undefined {
    return this.#current?.track;
  }

  /** Seconds into the current track, counting loops (0 before the context exists). */
  get position(): number {
    const slot = this.#current;
    if (!slot) return 0;
    const paused = this.#pausedAt.get(slot);
    if (paused !== undefined) return paused;
    const bus = this.bus();
    return bus && slot.anchor !== undefined ? bus.context.currentTime - slot.anchor : 0;
  }

  /**
   * Plays `track` from its start, cross-fading from the current one over `fade` seconds; `null`
   * fades the music out.
   */
  play(track: Track | null, fade: number): void {
    const previous = this.#current;
    if (previous) this.#fadeOut(previous, fade);
    this.#current = track ? this.#slot(track, fade) : undefined;
  }

  /** Plays `track` once over the music (a jingle). */
  jingle(track: Track): void {
    this.#others.push(this.#slot(track, 0));
  }

  /** Pauses the music where it is (P12-R11): the notes sounding stop. */
  pause(): void {
    if (this.#paused) return;
    this.#paused = true;
    const bus = this.bus();
    for (const slot of this.#slots()) {
      if (!bus || slot.anchor === undefined) continue;
      const now = bus.context.currentTime;
      const at = now - slot.anchor;
      this.#pausedAt.set(slot, at);
      slot.sequencer.seek(at);
      for (const voice of slot.voices) voice.stop(now, this.timings.pauseFadeSeconds);
      slot.voices = [];
    }
  }

  /** Goes on from where the music was paused. */
  resume(): void {
    if (!this.#paused) return;
    this.#paused = false;
    const now = this.bus()?.context.currentTime ?? 0;
    for (const [slot, at] of this.#pausedAt) slot.anchor = now - at;
    this.#pausedAt.clear();
  }

  /** Stops everything at once. */
  stop(): void {
    const now = this.bus()?.context.currentTime ?? 0;
    for (const slot of this.#slots()) this.#silence(slot, now);
    this.#current = undefined;
    this.#others = [];
    this.#pausedAt.clear();
  }

  /**
   * Schedules the notes due within the lookahead (or `ahead` seconds, before a long frame), and
   * drops the tracks that are over.
   */
  update(ahead = this.timings.lookaheadSeconds): void {
    const bus = this.bus();
    if (!bus || this.#paused) return;
    const now = bus.context.currentTime;
    for (const slot of this.#slots()) this.#schedule(slot, bus, now, ahead);
    this.#others = this.#others.filter((slot) => !this.#over(slot, now));
  }

  #slots(): Slot[] {
    return this.#current ? [this.#current, ...this.#others] : [...this.#others];
  }

  #slot(track: Track, fade: number): Slot {
    return {
      track,
      sequencer: new Sequencer(track),
      mixer: undefined,
      anchor: undefined,
      voices: [],
      target: 1,
      fade,
      until: undefined,
    };
  }

  #fadeOut(slot: Slot, fade: number): void {
    slot.target = 0;
    slot.fade = fade;
    this.#others.push(slot);
    const bus = this.bus();
    if (!bus || !slot.mixer) {
      slot.until = -Infinity;
      return;
    }
    const now = bus.context.currentTime;
    slot.until = now + fade;
    slot.mixer.fadeTo(0, now, Math.max(0.01, fade));
  }

  /** Starts the slot on the bus if needed, then schedules its notes up to the lookahead. */
  #schedule(slot: Slot, bus: MusicBus, now: number, ahead: number): void {
    // A track fading out goes on playing until it is silent; one never started stays so.
    if (slot.until !== undefined && !slot.mixer) return;
    if (!slot.mixer || slot.anchor === undefined) this.#start(slot, bus, now);
    const { mixer, anchor } = slot;
    if (!mixer || anchor === undefined) return;
    slot.voices = slot.voices.filter((v) => v.end > now);
    for (const { note, at, seconds } of slot.sequencer.advance(now + ahead - anchor)) {
      const instrument = this.#playable(slot, note.instrument, anchor + at);
      if (!instrument) continue;
      slot.voices.push(
        playVoice(bus.context, mixer.input(note.instrument, instrument), instrument.layers, {
          when: Math.max(now, anchor + at),
          noteHz: midiToHz(note.pitch),
          hold: seconds,
          gain: note.velocity * instrument.gain,
        }),
      );
    }
  }

  /** The instrument of a note, unless it is unknown or starts once the fade-out is over. */
  #playable(slot: Slot, name: string, start: number): Instrument | undefined {
    if (slot.until !== undefined && start >= slot.until) return undefined;
    return this.instruments[name];
  }

  #start(slot: Slot, bus: MusicBus, now: number): void {
    const mixer = new TrackMixer(bus, this.effects, slot.track.bpm);
    mixer.fadeIn(now, slot.fade);
    slot.mixer = mixer;
    slot.anchor = now;
  }

  /** A slot is over once faded out, or once a jingle has played all its notes. */
  #over(slot: Slot, now: number): boolean {
    if (slot.until !== undefined && now >= slot.until) {
      this.#silence(slot, now);
      return true;
    }
    return slot.sequencer.done && slot.voices.every((v) => v.end <= now);
  }

  #silence(slot: Slot, now: number): void {
    for (const voice of slot.voices) voice.stop(now, this.timings.pauseFadeSeconds);
    slot.voices = [];
    slot.mixer?.disconnect();
  }
}
