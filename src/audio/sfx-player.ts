import { soundSeconds, type SoundDesign } from './audio-types';
import { playVoice, type Voice } from './synth';
import { VoicePool } from './voice-pool';

/** Where the sound effects go, once the audio context exists. */
export interface SfxBus {
  readonly context: BaseAudioContext & Pick<AudioContext, 'createStereoPanner'>;
  readonly sfx: AudioNode;
}

/** Mixing settings of a {@link SfxPlayer} (`config/audio.ts`). */
export interface SfxSettings {
  readonly maxVoices: number;
  readonly retriggerSeconds: number;
  /** A sound started again within `retriggerSeconds` is made this much louder instead. */
  readonly retriggerBoost: number;
  /** Pan of a sound at the playfield's edges (−panMax left, +panMax right). */
  readonly panMax: number;
  /** How fast a sound fades when stopped early. */
  readonly stopFadeSeconds: number;
}

/** Pan of a sound at `x` on a playfield `width` wide: −`panMax` at the left edge, 0 in the middle. */
export function panAt(x: number, width: number, panMax: number): number {
  if (!(width > 0)) return 0;
  const share = Math.min(1, Math.max(0, x / width));
  return (share * 2 - 1) * panMax;
}

/** A sound playing, with its voice once the context exists. */
interface Playing {
  readonly id: number;
  readonly voice: Voice | undefined;
  readonly gain: GainNode | undefined;
}

/**
 * Plays the sound effects (P12-R09, P12-R10): each through the {@link VoicePool}'s limits, panned
 * with its position, on the sound effect bus. Without a context the pool still decides, so the
 * game's logic (and the e2e test API) does not depend on audio being available.
 */
export class SfxPlayer {
  readonly #pool: VoicePool;
  readonly #playing = new Map<number, Playing>();
  /** Looping sounds playing, by name. */
  readonly #loops = new Map<string, number>();

  constructor(
    private readonly bus: () => SfxBus | undefined,
    private readonly clock: () => number,
    private readonly settings: SfxSettings,
  ) {
    this.#pool = new VoicePool(settings.maxVoices, settings.retriggerSeconds);
  }

  /** Voices counted by the pool. */
  get voices(): number {
    return this.#pool.voices.length;
  }

  /**
   * Plays `sound`, panned to `pan` (−1..1) when it is positional. Returns whether it plays (the
   * pool may drop it).
   */
  play(sound: SoundDesign, pan = 0): boolean {
    if (sound.loop && this.#loops.has(sound.name)) return false;
    const decision = this.#pool.request(
      sound.name,
      sound.priority,
      this.clock(),
      soundSeconds(sound),
    );
    if (!decision.play) {
      if (decision.retrigger) this.#boost(sound.name);
      return false;
    }
    if (decision.evicted) this.#stopVoice(decision.evicted.id);
    this.#forgetEnded();
    this.#playing.set(decision.id, { id: decision.id, ...this.#start(sound, pan) });
    if (sound.loop) this.#loops.set(sound.name, decision.id);
    return true;
  }

  /** Stops the looping sound `name` (the laser is let go). */
  stopLoop(name: string): void {
    const id = this.#loops.get(name);
    if (id === undefined) return;
    this.#loops.delete(name);
    this.#stopVoice(id);
  }

  /** Whether the looping sound `name` plays. */
  looping(name: string): boolean {
    return this.#loops.has(name);
  }

  /** Stops every sound (the game pauses, P12-R11). */
  stopAll(): void {
    for (const id of [...this.#playing.keys()]) this.#stopVoice(id);
    this.#loops.clear();
    this.#pool.clear();
  }

  #start(sound: SoundDesign, pan: number): Omit<Playing, 'id'> {
    const bus = this.bus();
    if (!bus) return { voice: undefined, gain: undefined };
    const { context } = bus;
    const gain = context.createGain();
    gain.gain.value = 1;
    let out: AudioNode = gain;
    if (sound.positional && pan !== 0) {
      const panner = context.createStereoPanner();
      panner.pan.value = Math.max(-1, Math.min(1, pan));
      gain.connect(panner);
      out = panner;
    }
    out.connect(bus.sfx);
    const voice = playVoice(context, gain, sound.layers, {
      when: context.currentTime,
      hold: sound.loop ? Infinity : sound.hold,
      gain: sound.gain,
    });
    return { voice, gain };
  }

  /** The same sound again too soon: the one playing gets a little louder instead (P12-R10). */
  #boost(name: string): void {
    const voice = this.#pool.voices.findLast((v) => v.name === name);
    const gain = voice && this.#playing.get(voice.id)?.gain;
    const bus = this.bus();
    if (!gain || !bus) return;
    const boosted = Math.min(
      this.settings.retriggerBoost ** 2,
      gain.gain.value * this.settings.retriggerBoost,
    );
    gain.gain.setValueAtTime(boosted, bus.context.currentTime);
  }

  /** Forgets the sounds that are over (the pool let them go). */
  #forgetEnded(): void {
    const alive = new Set(this.#pool.voices.map((v) => v.id));
    for (const id of this.#playing.keys()) if (!alive.has(id)) this.#playing.delete(id);
  }

  #stopVoice(id: number): void {
    const playing = this.#playing.get(id);
    this.#playing.delete(id);
    for (const [name, loop] of this.#loops) if (loop === id) this.#loops.delete(name);
    this.#pool.release(id);
    const bus = this.bus();
    if (playing?.voice && bus)
      playing.voice.stop(bus.context.currentTime, this.settings.stopFadeSeconds);
  }
}
