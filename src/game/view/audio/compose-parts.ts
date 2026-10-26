import type { Note } from '../../../audio/audio-types';
import { pick, type Random } from '../../../core/math/rng';
import { DRUM_PITCH } from './instruments';
import { BEATS_PER_BAR, type MusicStyle } from './music-styles';

/** What a bar is made from: its chord (scale-tone pitches) and how intense the section is. */
export interface BarContext {
  /** First beat of the bar. */
  readonly beat: number;
  /** The chord's pitches in the bass register, root first. */
  readonly chord: readonly number[];
  /** The scale's pitches over the lead's range, low to high. */
  readonly scale: readonly number[];
  /** 0 calm (an intro, a break) … 2 full (a boss fight). */
  readonly energy: number;
  /** Last bar of a section: the drums fill. */
  readonly fill: boolean;
}

/** A note of `instrument` at `beat` (beats), `beats` long. */
export function note(
  instrument: string,
  beat: number,
  beats: number,
  pitch: number,
  velocity: number,
): Note {
  return { instrument, beat, beats, pitch, velocity };
}

const DRUM_STEPS = 16;

/** A drum machine pattern: the steps (of 16 per bar) each drum plays at. */
interface DrumPattern {
  readonly kick: readonly number[];
  readonly snare: readonly number[];
  /** Closed hats every this many steps (16ths: 1, eighths: 2), every step when intense. */
  readonly hatEvery: number;
  /** Open hats (on the off-beats) or, with tribal drums, the extra percussion. */
  readonly open: readonly number[];
}

/**
 * Synthwave drum patterns by feel (synthwave review): four on the floor with off-beat open hats
 * (outrun), a laid-back backbeat, half time (dreamwave), tom-heavy tribal, heavy darksynth.
 */
const PATTERNS: Readonly<Record<MusicStyle['drums'], DrumPattern>> = {
  four: { kick: [0, 4, 8, 12], snare: [4, 12], hatEvery: 2, open: [2, 6, 10, 14] },
  backbeat: { kick: [0, 8, 10], snare: [4, 12], hatEvery: 2, open: [6, 14] },
  half: { kick: [0, 10], snare: [8], hatEvery: 2, open: [14] },
  tribal: { kick: [0, 6, 10], snare: [4, 12], hatEvery: 1, open: [3, 7, 11, 15] },
  heavy: { kick: [0, 3, 8, 11], snare: [8], hatEvery: 2, open: [] },
};

/** Gated snares ring for an eighth, so their gate shows. */
const SNARE_BEATS = 0.5;

/** One bar of drums (P12-R06): the style's pattern, hats by energy, a tom fill at section ends. */
export function drumBar(
  style: MusicStyle,
  bar: BarContext,
  random: Random,
  extraKicks: readonly number[],
): Note[] {
  const { kick, snare, hat, perc } = style.instruments;
  const pattern = PATTERNS[style.drums];
  const step = BEATS_PER_BAR / DRUM_STEPS;
  const at = (i: number): number => bar.beat + i * step;
  const notes = [...pattern.kick, ...extraKicks].map((i) => note(kick, at(i), step, DRUM_PITCH, 1));
  if (bar.energy === 0) return notes;
  for (const i of pattern.snare) notes.push(note(snare, at(i), SNARE_BEATS, DRUM_PITCH, 0.9));
  const every = bar.energy >= 2 ? 1 : pattern.hatEvery;
  for (let i = 0; i < DRUM_STEPS; i += every) {
    if (pattern.open.includes(i) && perc !== hat) continue;
    notes.push(note(hat, at(i), step, DRUM_PITCH, i % 4 === 0 ? 0.85 : 0.5 + random() * 0.2));
  }
  for (const i of pattern.open) notes.push(note(perc, at(i), step * 2, DRUM_PITCH, 0.6));
  if (bar.fill) notes.push(...drumFill(bar, random));
  return notes;
}

/** Pitches of a tom fill, high to low (semitones above the drum pitch). */
const TOM_FILL = [14, 10, 7, 3, 0, -4];

/** The end of a section: a descending synth-tom fill over the last beat or two. */
function drumFill(bar: BarContext, random: Random): Note[] {
  const step = BEATS_PER_BAR / DRUM_STEPS;
  const count = bar.energy >= 2 ? 6 : pick(random, [3, 4]);
  return TOM_FILL.slice(TOM_FILL.length - count).map((pitch, i) =>
    note('tom', bar.beat + (DRUM_STEPS - count + i) * step, step * 2, DRUM_PITCH + pitch, 0.75),
  );
}

/** Steps (of 16 per bar) the bass plays at, by feel; a held note lasts until the next one. */
const BASS_STEPS: Readonly<Record<MusicStyle['bass'], readonly (readonly number[])[]>> = {
  eighths: [[0, 2, 4, 6, 8, 10, 12, 14]],
  long: [[0, 8], [0, 6, 12], [0]],
  syncopated: [
    [0, 6, 8, 12],
    [0, 4, 6, 12],
    [0, 6, 10, 12],
  ],
  rolling: [Array.from({ length: 16 }, (_, i) => i)],
};

/** Bass steps when intense: rolling sixteenths (driving eighths for the long basses). */
const BUSY_BASS = Array.from({ length: 16 }, (_, i) => i);

/**
 * One bar of bass: the chord's root, the octave pumping on the off-beat eighths (outrun), a
 * passing fifth near the bar's end.
 */
export function bassBar(style: MusicStyle, bar: BarContext, steps: readonly number[]): Note[] {
  const [root = 36, , fifth = root + 7] = bar.chord;
  const sixteenth = BEATS_PER_BAR / DRUM_STEPS;
  const hits = bar.energy >= 2 && style.bass !== 'long' ? BUSY_BASS : steps;
  return hits.map((s, i) => {
    const next = hits[i + 1] ?? DRUM_STEPS;
    let pitch = s >= 12 && s < 14 && style.bass !== 'long' ? fifth : root;
    if (style.bass === 'eighths' && s % 4 === 2) pitch += 12;
    const accent = s % 4 === 0 ? 1 : 0.75;
    return note(
      style.instruments.bass,
      bar.beat + s * sixteenth,
      (next - s) * sixteenth * 0.9,
      pitch,
      accent,
    );
  });
}

/** The bass steps of a track: one rhythm of the style, picked for the level. */
export function bassSteps(style: MusicStyle, random: Random): readonly number[] {
  return pick(random, BASS_STEPS[style.bass]);
}

/** The pad holds the chord over the bar, voiced up `octaves`. */
export function padBar(style: MusicStyle, bar: BarContext): Note[] {
  const shift = 12 * style.octaves.pad;
  return bar.chord.map((pitch) =>
    note(style.instruments.pad, bar.beat, BEATS_PER_BAR, pitch + shift, 0.7),
  );
}

/** Arpeggio shapes: indices into the chord tones, over two octaves. */
const ARP_SHAPES: readonly (readonly number[])[] = [
  [0, 1, 2, 3],
  [0, 2, 1, 3],
  [3, 2, 1, 0],
  [0, 1, 2, 1],
  [0, 2, 3, 5],
  [0, 3, 1, 4],
];

/** The arpeggio shape of a track. */
export function arpShape(random: Random): readonly number[] {
  return pick(random, ARP_SHAPES);
}

/**
 * One bar of arpeggio over the chord, `rate` notes per beat (sixteenths when intense); it goes on
 * alone in the breaks, as synthwave breakdowns do.
 */
export function arpBar(style: MusicStyle, bar: BarContext, shape: readonly number[]): Note[] {
  const rate = bar.energy >= 2 ? Math.max(4, style.arpRate) : style.arpRate;
  const shift = 12 * style.octaves.arp;
  const tones = [...bar.chord, ...bar.chord.map((p) => p + 12)];
  const length = 1 / rate;
  const notes: Note[] = [];
  for (let i = 0; i < BEATS_PER_BAR * rate; i++) {
    const tone = tones[(shape[i % shape.length] ?? 0) % tones.length] ?? 0;
    notes.push(
      note(
        style.instruments.arp,
        bar.beat + i * length,
        length * 0.9,
        tone + shift,
        i % rate === 0 ? 0.9 : 0.65,
      ),
    );
  }
  return notes;
}
