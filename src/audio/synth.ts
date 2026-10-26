import type { ToneLayer, Waveform } from './audio-types';

/** The parts of a Web Audio context the synth uses (a fake one in the unit tests). */
export type SynthContext = Pick<
  BaseAudioContext,
  | 'createOscillator'
  | 'createGain'
  | 'createBiquadFilter'
  | 'createBuffer'
  | 'createBufferSource'
  | 'sampleRate'
  | 'currentTime'
>;

/** How one voice is played. */
export interface VoiceOptions {
  /** Audio time it starts at. */
  readonly when: number;
  /** The note's frequency for an instrument (layer pitches are ratios); none for a sound. */
  readonly noteHz?: number;
  /** Seconds the layers hold before their release; Infinity until {@link Voice.stop}. */
  readonly hold: number;
  /** Gain on every layer (velocity × mix level). */
  readonly gain: number;
}

/** A voice playing (or scheduled). */
export interface Voice {
  /** Audio time it is over (Infinity while a looping voice holds). */
  readonly end: number;
  /** Fades it out over `fade` seconds from `at`, then stops it. */
  stop(at: number, fade: number): void;
}

/** Seconds of white noise, looped by the noise layers. */
const NOISE_SECONDS = 1;
/** Gain values ramp from and to this instead of 0, which exponential ramps cannot reach. */
const SILENT = 0.0001;
/** Sources stop a little after their release, so nothing clicks. */
const STOP_MARGIN = 0.02;

const noiseBuffers = new WeakMap<SynthContext, AudioBuffer>();

/** One second of white noise per context, made once. */
function noiseBuffer(ctx: SynthContext): AudioBuffer {
  let buffer = noiseBuffers.get(ctx);
  if (buffer) return buffer;
  buffer = ctx.createBuffer(1, Math.round(ctx.sampleRate * NOISE_SECONDS), ctx.sampleRate);
  const data = buffer.getChannelData(0);
  // A fixed sequence (no Math.random): the noise sounds the same on every run.
  let seed = 0x9e3779b9;
  for (let i = 0; i < data.length; i++) {
    seed ^= seed << 13;
    seed ^= seed >>> 17;
    seed ^= seed << 5;
    data[i] = ((seed >>> 0) / 0xffffffff) * 2 - 1;
  }
  noiseBuffers.set(ctx, buffer);
  return buffer;
}

type Source = OscillatorNode | AudioBufferSourceNode;

/** The layer's source: an oscillator at its pitch (gliding), or looped noise. */
function source(ctx: SynthContext, layer: ToneLayer, start: number, base: number): Source {
  const pitch = layer.pitch * base;
  const glide = layer.glideTo !== undefined ? layer.glideTo * base : undefined;
  const seconds = layer.glideSeconds ?? 0;
  if (layer.wave === 'noise') {
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuffer(ctx);
    noise.loop = true;
    if (glide !== undefined && pitch > 0) {
      noise.playbackRate.setValueAtTime(1, start);
      noise.playbackRate.exponentialRampToValueAtTime(
        Math.max(SILENT, glide / pitch),
        start + seconds,
      );
    }
    return noise;
  }
  const osc = ctx.createOscillator();
  osc.type = layer.wave satisfies Exclude<Waveform, 'noise'>;
  osc.frequency.setValueAtTime(pitch, start);
  if (glide !== undefined) {
    osc.frequency.exponentialRampToValueAtTime(Math.max(1, glide), start + seconds);
  }
  if (layer.detuneCents) osc.detune.setValueAtTime(layer.detuneCents, start);
  return osc;
}

/** The layer's filter, its cut-off gliding from `from` to `frequency`. */
function filter(ctx: SynthContext, layer: ToneLayer, start: number): BiquadFilterNode | undefined {
  const spec = layer.filter;
  if (!spec) return undefined;
  const node = ctx.createBiquadFilter();
  node.type = spec.type;
  node.Q.setValueAtTime(spec.q ?? 1, start);
  node.frequency.setValueAtTime(spec.from ?? spec.frequency, start);
  if (spec.from !== undefined) {
    node.frequency.exponentialRampToValueAtTime(spec.frequency, start + (spec.sweepSeconds ?? 0.1));
  }
  return node;
}

/** Shapes `gain` with the layer's envelope; returns when its release ends (Infinity if held). */
function envelope(
  param: AudioParam,
  layer: ToneLayer,
  start: number,
  peak: number,
  hold: number,
): number {
  const { attack, decay, sustain, release } = layer.envelope;
  const level = Math.max(SILENT, peak * sustain);
  param.setValueAtTime(SILENT, start);
  param.linearRampToValueAtTime(peak, start + attack);
  param.linearRampToValueAtTime(level, start + attack + decay);
  if (!Number.isFinite(hold)) return Infinity;
  const releaseAt = start + Math.max(hold, attack + decay);
  param.setValueAtTime(level, releaseAt);
  param.linearRampToValueAtTime(SILENT, releaseAt + release);
  return releaseAt + release;
}

/**
 * Plays the `layers` of one voice into `destination` (P12-R05): each layer is an oscillator or
 * noise, through its filter and envelope. Returns a handle to stop it early.
 */
export function playVoice(
  ctx: SynthContext,
  destination: AudioNode,
  layers: readonly ToneLayer[],
  options: VoiceOptions,
): Voice {
  const parts: { readonly source: Source; readonly gain: GainNode }[] = [];
  let end = 0;
  for (const layer of layers) {
    const start = options.when + (layer.delay ?? 0);
    const src = source(ctx, layer, start, options.noteHz ?? 1);
    const gain = ctx.createGain();
    const shaped = filter(ctx, layer, start);
    if (shaped) src.connect(shaped).connect(gain);
    else src.connect(gain);
    gain.connect(destination);
    const over = envelope(gain.gain, layer, start, layer.gain * options.gain, options.hold);
    src.start(start);
    if (Number.isFinite(over)) src.stop(over + STOP_MARGIN);
    end = Math.max(end, over);
    parts.push({ source: src, gain });
  }
  return {
    end,
    stop: (at, fade) => {
      for (const { source: src, gain } of parts) {
        gain.gain.cancelScheduledValues(at);
        gain.gain.setTargetAtTime(SILENT, at, Math.max(0.001, fade / 4));
        try {
          src.stop(at + fade + STOP_MARGIN);
        } catch {
          // Already stopped earlier than that: nothing to do.
        }
      }
    },
  };
}
