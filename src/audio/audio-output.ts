/** The music and sound effect buses (P12-R05). */
export interface AudioBuses {
  readonly context: AudioContext;
  readonly music: GainNode;
  /** The music reverb's input: it comes out on the music bus. None when not asked for. */
  readonly reverb?: AudioNode;
  readonly sfx: GainNode;
}

/** Settings of an {@link AudioOutput}. */
export interface AudioOutputOptions {
  /** Creates the context: `new AudioContext()` in the browser; none without Web Audio. */
  readonly createContext?: () => AudioContext;
  /** Level of each bus at full volume, so loud sounds stay within reach of the music. */
  readonly mix: { readonly music: number; readonly sfx: number };
  /** `master_peak`: the limiter's threshold, in dBFS. */
  readonly peakDb: number;
  readonly limiter: {
    readonly kneeDb: number;
    readonly ratio: number;
    readonly attackSeconds: number;
    readonly releaseSeconds: number;
  };
  /** Length of the music reverb's tail in seconds; no reverb when omitted. */
  readonly reverbSeconds?: number;
}

/** A stereo reverb impulse: decaying noise, the same on every run (no `Math.random`). */
function reverbImpulse(context: BaseAudioContext, seconds: number): AudioBuffer {
  const length = Math.max(1, Math.round(context.sampleRate * seconds));
  const buffer = context.createBuffer(2, length, context.sampleRate);
  let seed = 0x2545f491;
  for (let channel = 0; channel < 2; channel++) {
    const data = buffer.getChannelData(channel);
    for (let i = 0; i < length; i++) {
      seed ^= seed << 13;
      seed ^= seed >>> 17;
      seed ^= seed << 5;
      const noise = ((seed >>> 0) / 0xffffffff) * 2 - 1;
      data[i] = noise * (1 - i / length) ** 3;
    }
  }
  return buffer;
}

/** Bus gain of a volume `step` out of `steps`: (step / steps)², 0 silent (P12-R04). */
export function volumeGain(step: number, steps: number): number {
  if (!(steps > 0)) return 0;
  const share = Math.min(1, Math.max(0, step / steps));
  return share * share;
}

/** Gain ramps on the buses last this long, so a volume change does not click. */
const BUS_RAMP_SECONDS = 0.03;

/**
 * Where all audio goes (P12-R05): a music bus and a sound effect bus, each with its volume,
 * into a master limiter so the output never clips. Browsers only start audio after a user
 * gesture, so the context is created by {@link unlock}, called on the first key press, tap,
 * click or gamepad button: nothing is heard before, and no autoplay warning is shown. Without
 * Web Audio, or if it fails, everything stays silent and nothing throws.
 */
export class AudioOutput {
  #buses: AudioBuses | undefined;
  #failed = false;
  #music = 1;
  #sfx = 1;

  constructor(private readonly options: AudioOutputOptions) {}

  /** The buses, once the context exists. */
  get buses(): AudioBuses | undefined {
    return this.#buses;
  }

  /** The context's state: `none` before it is created (or without Web Audio). */
  get state(): AudioContextState | 'none' {
    return this.#buses?.context.state ?? 'none';
  }

  /** Creates (or resumes) the context, after a user gesture. Returns the buses, if any. */
  unlock(): AudioBuses | undefined {
    if (!this.#buses && !this.#failed) this.#buses = this.#create();
    const context = this.#buses?.context;
    if (context?.state === 'suspended') this.#quietly(context.resume());
    return this.#buses;
  }

  /** Silences everything while the page is hidden (P12-R11), and brings it back. */
  setHidden(hidden: boolean): void {
    const context = this.#buses?.context;
    if (!context || context.state === 'closed') return;
    this.#quietly(hidden ? context.suspend() : context.resume());
  }

  /** Sets the bus gains from 0..1 volume gains (see {@link volumeGain}). */
  setVolumes(music: number, sfx: number): void {
    this.#music = music;
    this.#sfx = sfx;
    const buses = this.#buses;
    if (!buses) return;
    const now = buses.context.currentTime;
    const { mix } = this.options;
    this.#ramp(buses.music.gain, music * mix.music, now);
    this.#ramp(buses.sfx.gain, sfx * mix.sfx, now);
  }

  #ramp(param: AudioParam, value: number, now: number): void {
    param.cancelScheduledValues(now);
    param.setValueAtTime(param.value, now);
    param.linearRampToValueAtTime(value, now + BUS_RAMP_SECONDS);
  }

  #create(): AudioBuses | undefined {
    const { createContext, mix, peakDb, limiter } = this.options;
    if (!createContext) return undefined;
    try {
      const context = createContext();
      const master = context.createDynamicsCompressor();
      master.threshold.value = peakDb;
      master.knee.value = limiter.kneeDb;
      master.ratio.value = limiter.ratio;
      master.attack.value = limiter.attackSeconds;
      master.release.value = limiter.releaseSeconds;
      master.connect(context.destination);
      const music = context.createGain();
      const sfx = context.createGain();
      music.gain.value = this.#music * mix.music;
      sfx.gain.value = this.#sfx * mix.sfx;
      music.connect(master);
      sfx.connect(master);
      const reverb = this.#reverb(context, music);
      return reverb ? { context, music, reverb, sfx } : { context, music, sfx };
    } catch {
      this.#failed = true;
      return undefined;
    }
  }

  /** A convolver into the music bus, so the music volume applies to its tail too. */
  #reverb(context: AudioContext, music: GainNode): ConvolverNode | undefined {
    const { reverbSeconds } = this.options;
    if (reverbSeconds === undefined) return undefined;
    const reverb = context.createConvolver();
    reverb.buffer = reverbImpulse(context, reverbSeconds);
    reverb.connect(music);
    return reverb;
  }

  /** Audio promises that fail (a context closed by the browser) are not errors of the game. */
  #quietly(promise: Promise<void>): void {
    promise.catch(() => undefined);
  }
}
