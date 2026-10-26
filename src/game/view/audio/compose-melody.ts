import type { Note } from '../../../audio/audio-types';
import { pick, type Random } from '../../../core/math/rng';
import { note, type BarContext } from './compose-parts';
import { BEATS_PER_BAR, type MusicStyle } from './music-styles';

/** One note of a motif: when (eighths into its two bars), how long, and a scale step. */
interface MotifNote {
  readonly step: number;
  readonly length: number;
  /** Scale steps above the chord's root. */
  readonly degree: number;
}

/** A two-bar melodic idea, repeated and varied over a section. */
export type Motif = readonly MotifNote[];

/** Rhythms of a two-bar motif: [eighth, length in eighths] pairs. */
const RHYTHMS: readonly (readonly (readonly [number, number])[])[] = [
  [
    [0, 2],
    [2, 2],
    [4, 1],
    [5, 3],
    [8, 2],
    [10, 2],
    [12, 4],
  ],
  [
    [0, 3],
    [3, 1],
    [4, 2],
    [6, 2],
    [8, 3],
    [11, 1],
    [12, 2],
    [14, 2],
  ],
  [
    [0, 1],
    [1, 1],
    [2, 2],
    [4, 4],
    [8, 1],
    [9, 1],
    [10, 2],
    [12, 4],
  ],
  [
    [0, 4],
    [4, 2],
    [6, 2],
    [8, 6],
    [14, 2],
  ],
  [
    [1, 1],
    [2, 2],
    [4, 1],
    [5, 1],
    [6, 2],
    [9, 1],
    [10, 2],
    [12, 3],
  ],
  [
    [0, 2],
    [3, 2],
    [6, 2],
    [8, 2],
    [11, 2],
    [14, 2],
  ],
];

/** Chord tones (scale steps above the chord's root) a motif lands on. */
const CHORD_STEPS = [0, 2, 4, 7];

/**
 * A motif for a section (P12-R06): one of the rhythms, its pitches a walk on the scale that starts
 * and ends on chord tones, so every level gets its own melody.
 */
export function makeMotif(random: Random): Motif {
  const rhythm = pick(random, RHYTHMS);
  let degree = pick(random, CHORD_STEPS);
  return rhythm.map(([step, length], i) => {
    if (i > 0) {
      const strong = step % 4 === 0;
      degree = strong
        ? nearestChordStep(degree + pick(random, [-2, -1, 1, 2]))
        : degree + pick(random, [-2, -1, 1, 1, 2]);
      degree = Math.max(-3, Math.min(9, degree));
    }
    return { step, length, degree };
  });
}

function nearestChordStep(degree: number): number {
  let best = 0;
  for (const step of [-7, -5, -3, ...CHORD_STEPS, 9]) {
    if (Math.abs(step - degree) < Math.abs(best - degree)) best = step;
  }
  return best;
}

/**
 * Plays two bars of a motif from `bar`, on the chord of the bar (its scale step `chordDegree`),
 * `shift` scale steps up for a variation.
 */
export function motifBars(
  style: MusicStyle,
  motif: Motif,
  bar: BarContext,
  chordDegree: number,
  shift: number,
): Note[] {
  if (bar.energy === 0) return [];
  const eighth = BEATS_PER_BAR / 8;
  const octave = 12 * style.octaves.lead;
  return motif.map((m) => {
    const index = chordDegree + m.degree + shift;
    const pitch = scalePitch(bar.scale, index) + octave;
    return note(
      style.instruments.lead,
      bar.beat + m.step * eighth,
      m.length * eighth * 0.92,
      pitch,
      0.8,
    );
  });
}

/** The pitch of scale step `index` (any integer: it wraps by octaves). */
export function scalePitch(scale: readonly number[], index: number): number {
  const size = scale.length;
  if (size === 0) return 0;
  const octave = Math.floor(index / size);
  return (scale[index - octave * size] ?? 0) + 12 * octave;
}
