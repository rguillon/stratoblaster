import { beatSeconds, type Instrument, type MusicEffects } from './audio-types';

/** Where the music goes, once the audio context exists. */
export interface MusicBus {
  readonly context: BaseAudioContext;
  readonly music: AudioNode;
  /** The music reverb's input, if there is one. */
  readonly reverb?: AudioNode;
}

const SILENT = 0.0001;

/** Fades `param` from where it is to `value` over `seconds` from `now`. */
function fade(param: AudioParam, value: number, now: number, seconds: number): void {
  param.cancelScheduledValues(now);
  param.setValueAtTime(Math.max(SILENT, param.value), now);
  param.exponentialRampToValueAtTime(Math.max(SILENT, value), now + Math.max(0.01, seconds));
}

/**
 * The mixer of one playing track: an input per instrument into the track's fader, with sends to
 * its tempo-synced echo (a dotted eighth by default) and to the shared music reverb, so a track
 * fades in and out with its echoes and reverb (P12-R06, synthwave review).
 */
export class TrackMixer {
  /** The track's fader, into the music bus. */
  readonly output: GainNode;
  readonly #reverb: GainNode | undefined;
  #echo: GainNode | undefined;
  readonly #inputs = new Map<string, GainNode>();

  constructor(
    private readonly bus: MusicBus,
    private readonly effects: MusicEffects | undefined,
    private readonly bpm: number,
  ) {
    const { context } = bus;
    this.output = context.createGain();
    this.output.connect(bus.music);
    if (bus.reverb && effects) {
      this.#reverb = context.createGain();
      this.#reverb.connect(bus.reverb);
    }
  }

  /** Fades the track (and its effects) to `level` over `seconds`; at once when 0. */
  fadeTo(level: number, now: number, seconds: number): void {
    for (const param of this.#faders()) {
      if (seconds > 0) fade(param, level, now, seconds);
      else param.setValueAtTime(level, now);
    }
  }

  /** Starts silent, then fades in over `seconds` (at once when 0). */
  fadeIn(now: number, seconds: number): void {
    if (seconds <= 0) {
      this.fadeTo(1, now, 0);
      return;
    }
    for (const param of this.#faders()) param.setValueAtTime(SILENT, now);
    this.fadeTo(1, now, seconds);
  }

  /** Where the notes of `instrument` go: its own gain, with its echo and reverb sends. */
  input(name: string, instrument: Instrument): AudioNode {
    let input = this.#inputs.get(name);
    if (input) return input;
    const { context } = this.bus;
    input = context.createGain();
    input.connect(this.output);
    if (instrument.echo && this.effects) this.#send(input, this.#echoInput(), instrument.echo);
    if (instrument.reverb && this.#reverb) this.#send(input, this.#reverb, instrument.reverb);
    this.#inputs.set(name, input);
    return input;
  }

  disconnect(): void {
    this.output.disconnect();
    this.#reverb?.disconnect();
    this.#echo?.disconnect();
  }

  #faders(): AudioParam[] {
    return this.#reverb ? [this.output.gain, this.#reverb.gain] : [this.output.gain];
  }

  #send(from: AudioNode, to: AudioNode, amount: number): void {
    const send = this.bus.context.createGain();
    send.gain.value = amount;
    from.connect(send);
    send.connect(to);
  }

  /** The echo: a delay of `echoBeats` at the track's tempo, fed back, into the fader. */
  #echoInput(): GainNode {
    if (this.#echo) return this.#echo;
    const { context } = this.bus;
    const effects = this.effects;
    const seconds = (effects?.echoBeats ?? 0.75) * beatSeconds(this.bpm);
    const input = context.createGain();
    const delay = context.createDelay(Math.max(1, seconds));
    delay.delayTime.value = seconds;
    const feedback = context.createGain();
    feedback.gain.value = effects?.echoFeedback ?? 0.3;
    input.connect(delay);
    delay.connect(feedback);
    feedback.connect(delay);
    delay.connect(this.output);
    this.#echo = input;
    return input;
  }
}
