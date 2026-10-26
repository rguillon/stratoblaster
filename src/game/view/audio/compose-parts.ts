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

/** Which of the 16 steps of a bar each drum plays, by feel. */
const PATTERNS: Readonly<Record<MusicStyle['drums'], { kick: number[]; snare: number[] }>> = {
  four: { kick: [0, 4, 8, 12], snare: [4, 12] },
  half: { kick: [0, 10], snare: [8] },
  tribal: { kick: [0, 6, 10], snare: [4, 12] },
  heavy: { kick: [0, 3, 8, 11], snare: [8] },
};

/** One bar of drums (P12-R06): the style's pattern, hats by energy, a fill at section ends. */
export function drumBar(
  style: MusicStyle,
  bar: BarContext,
  random: Random,
  extraKicks: number[],
): Note[] {
  const { kick, snare, hat, perc } = style.instruments;
  const pattern = PATTERNS[style.drums];
  const step = BEATS_PER_BAR / DRUM_STEPS;
  const notes: Note[] = [];
  const at = (i: number): number => bar.beat + i * step;
  for (const i of [...pattern.kick, ...extraKicks])
    notes.push(note(kick, at(i), step, DRUM_PITCH, 1));
  if (bar.energy > 0) {
    for (const i of pattern.snare) notes.push(note(snare, at(i), step, DRUM_PITCH, 0.9));
  }
  const hatEvery = bar.energy >= 2 ? 1 : 2;
  for (let i = 0; i < DRUM_STEPS; i += hatEvery) {
    const accent = i % 4 === 2 ? 0.9 : 0.55 + random() * 0.2;
    notes.push(note(hat, at(i), step, DRUM_PITCH, accent));
  }
  if (bar.energy > 0 && style.drums !== 'heavy')
    notes.push(note(perc, at(14), step * 2, DRUM_PITCH, 0.6));
  if (bar.fill) notes.push(...drumFill(style, bar, random));
  return notes;
}

/** The last beat of a section: a roll of snares or toms. */
function drumFill(style: MusicStyle, bar: BarContext, random: Random): Note[] {
  const tom = style.drums === 'tribal' || style.drums === 'heavy';
  const instrument = tom ? style.instruments.perc : style.instruments.snare;
  const step = BEATS_PER_BAR / DRUM_STEPS;
  const count = bar.energy >= 2 ? 4 : pick(random, [2, 3, 4]);
  const notes: Note[] = [];
  for (let i = 0; i < count; i++) {
    notes.push(
      note(instrument, bar.beat + (DRUM_STEPS - count + i) * step, step, DRUM_PITCH, 0.6 + 0.1 * i),
    );
  }
  return notes;
}

/** Steps (of 8 per bar) the bass plays at, by feel; a held note lasts until the next one. */
const BASS_STEPS: Readonly<Record<MusicStyle['bass'], readonly (readonly number[])[]>> = {
  eighths: [[0, 1, 2, 3, 4, 5, 6, 7]],
  long: [[0, 4], [0, 3, 6], [0]],
  syncopated: [
    [0, 3, 4, 6],
    [0, 2, 3, 6],
    [0, 3, 5, 6],
  ],
  pulse: [
    [0, 1, 2, 4, 5, 6],
    [0, 2, 3, 4, 6, 7],
  ],
};

/** One bar of bass: the chord's root, with octave jumps and passing fifths for movement. */
export function bassBar(style: MusicStyle, bar: BarContext, steps: readonly number[]): Note[] {
  const [root = 36, , fifth = root + 7] = bar.chord;
  const eighth = BEATS_PER_BAR / 8;
  const busy = bar.energy >= 2 && style.bass !== 'long';
  const hits = busy ? [0, 1, 2, 3, 4, 5, 6, 7] : steps;
  return hits.map((s, i) => {
    const next = hits[i + 1] ?? 8;
    const pitch =
      style.bass === 'eighths' && s % 2 === 1
        ? root + 12
        : s === 6 && style.bass !== 'long'
          ? fifth
          : root;
    return note(
      style.instruments.bass,
      bar.beat + s * eighth,
      (next - s) * eighth * 0.9,
      pitch,
      s === 0 ? 1 : 0.8,
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

/** One bar of arpeggio over the chord, `rate` notes per beat (twice as fast when intense). */
export function arpBar(style: MusicStyle, bar: BarContext, shape: readonly number[]): Note[] {
  if (bar.energy === 0) return [];
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
