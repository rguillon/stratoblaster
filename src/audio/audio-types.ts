/**
 * Data the audio engine plays: synth voices, instruments, sound designs and tracks (P12-R05).
 * A game describes its music and sounds with these; the engine turns them into Web Audio nodes.
 */

/** An oscillator shape, or white noise. */
export type Waveform = 'sine' | 'square' | 'sawtooth' | 'triangle' | 'noise';

/** Gain envelope of a voice, in seconds; `sustain` is a share (0..1) of the peak. */
export interface Envelope {
  readonly attack: number;
  readonly decay: number;
  readonly sustain: number;
  readonly release: number;
}

/** A filter on a voice. Its cut-off may start higher and glide down (a "pluck", a "zap"). */
export interface FilterSpec {
  readonly type: 'lowpass' | 'highpass' | 'bandpass';
  readonly frequency: number;
  readonly q?: number;
  /** Cut-off at the start, gliding to `frequency` over `sweepSeconds`. */
  readonly from?: number;
  readonly sweepSeconds?: number;
}

/**
 * One oscillator (or noise) of a voice. For an instrument, `pitch` is a ratio of the note's
 * frequency (1 = the note, 0.5 an octave down); for a sound effect it is in Hz. Noise ignores
 * it, unless it glides (it then sets the noise's playback rate).
 */
export interface ToneLayer {
  readonly wave: Waveform;
  readonly gain: number;
  readonly pitch: number;
  /** Pitch reached after `glideSeconds` (same unit): sweeps, kicks, lasers. */
  readonly glideTo?: number;
  readonly glideSeconds?: number;
  readonly detuneCents?: number;
  readonly envelope: Envelope;
  readonly filter?: FilterSpec;
  /** Seconds after the voice starts (layers in sequence, e.g. a two-note chime). */
  readonly delay?: number;
}

/** A music instrument: the layers every note plays, and its level in the mix. */
export interface Instrument {
  readonly layers: readonly ToneLayer[];
  readonly gain: number;
}

/** A sound effect (P12-R09, P12-R10). */
export interface SoundDesign {
  /** Its name, as the e2e test API lists it (P12-R12). */
  readonly name: string;
  readonly layers: readonly ToneLayer[];
  /** Level in the sound effect mix (player shots quieter than hits and explosions). */
  readonly gain: number;
  /** When the voices are all taken, a sound replaces one of lower or equal priority. */
  readonly priority: number;
  /** Seconds the layers hold before their release; a looping sound holds until stopped. */
  readonly hold: number;
  /** Panned left or right with its x on the playfield. */
  readonly positional?: boolean;
  /** Plays until stopped (a laser hum). */
  readonly loop?: boolean;
}

/** One note of a track: when, how long (in beats), which MIDI pitch, how hard, on what. */
export interface Note {
  readonly beat: number;
  readonly beats: number;
  readonly pitch: number;
  /** 0..1. */
  readonly velocity: number;
  readonly instrument: string;
}

/** A piece of generated music (P12-R06, P12-R07, P12-R08). */
export interface Track {
  /** Its id, as the e2e test API reports it, e.g. `level-2-3`, `boss-2`, `menu`. */
  readonly id: string;
  readonly bpm: number;
  /** Length in beats; a looping track starts again after it. */
  readonly beats: number;
  /** Sorted by `beat`. */
  readonly notes: readonly Note[];
  readonly loop: boolean;
}

/** Seconds of one beat at `bpm`. */
export function beatSeconds(bpm: number): number {
  return 60 / bpm;
}

/** Length of a track in seconds. */
export function trackSeconds(track: Track): number {
  return track.beats * beatSeconds(track.bpm);
}

/** Frequency in Hz of a MIDI pitch (69 = A4 = 440 Hz). */
export function midiToHz(pitch: number): number {
  return 440 * 2 ** ((pitch - 69) / 12);
}

/** Seconds a layer sounds for once started and held for `hold` seconds. */
export function layerSeconds(layer: ToneLayer, hold: number): number {
  const { attack, decay, release } = layer.envelope;
  return (layer.delay ?? 0) + Math.max(hold, attack + decay) + release;
}

/** Seconds a sound effect lasts (Infinity for a looping one). */
export function soundSeconds(sound: SoundDesign): number {
  if (sound.loop) return Infinity;
  return Math.max(0, ...sound.layers.map((l) => layerSeconds(l, sound.hold)));
}
