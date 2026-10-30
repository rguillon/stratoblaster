import type { Note } from '../../../audio/audio-types';
import { note, type BarContext } from './compose-parts';
import { DRUM_PITCH } from './instruments';
import { BEATS_PER_BAR, type MusicStyle } from './music-styles';

/**
 * The boss tracks' parts (P12-R07, GD-70 "a more stressful music"; reviewer, 2026-10-26): a
 * driving drum machine with pushed kicks and snare rolls, a rolling octave bass, chord stabs on a
 * 3-3-2 rhythm and a noise riser into every section.
 */

const STEPS = 16;
const STEP = BEATS_PER_BAR / STEPS;

/**
 * Boss chord progressions (scale degrees, one chord per two bars): tense, around the root, with
 * the flat second (phrygian) or the diminished second and major fifth (harmonic minor).
 */
export const BOSS_PROGRESSIONS: readonly (readonly number[])[] = [
  [0, 1, 0, 1],
  [0, 5, 1, 4],
  [0, 0, 5, 4],
  [0, 6, 5, 1],
];

/** Four on the floor, pushed by off-beat sixteenths. */
const KICKS = [0, 4, 7, 8, 12, 14];
const SNARES = [4, 12];
/** The off-beat eighths: open hats, or toms (World 3). */
const OFF_BEATS = [2, 6, 10, 14];

/** A snare roll over the last `count` sixteenths of the bar, growing louder. */
function snareRoll(snare: string, bar: BarContext, count: number): Note[] {
  return Array.from({ length: count }, (_, i) =>
    note(snare, bar.beat + (STEPS - count + i) * STEP, STEP, DRUM_PITCH, 0.35 + (0.6 * i) / count),
  );
}

/** Every other bar of four ends on a short roll; the section's last bar rolls for half a bar. */
function rollLength(bar: BarContext): number {
  if (bar.fill) return 8;
  return (bar.beat / BEATS_PER_BAR) % 4 === 3 ? 4 : 0;
}

/** One bar of boss drums: sixteenth hats, pushed kicks, the backbeat and snare rolls. */
export function bossDrumBar(style: MusicStyle, bar: BarContext): Note[] {
  const { kick, snare, hat, perc } = style.instruments;
  const at = (i: number): number => bar.beat + i * STEP;
  const roll = rollLength(bar);
  const notes = KICKS.map((i) => note(kick, at(i), STEP, DRUM_PITCH, 1));
  for (const i of SNARES) {
    if (i < STEPS - roll) notes.push(note(snare, at(i), 0.5, DRUM_PITCH, 0.95));
  }
  for (let i = 0; i < STEPS; i++) {
    if (!OFF_BEATS.includes(i)) notes.push(note(hat, at(i), STEP, DRUM_PITCH, i % 4 ? 0.55 : 0.85));
  }
  for (const i of OFF_BEATS) notes.push(note(perc, at(i), STEP * 2, DRUM_PITCH, 0.7));
  notes.push(...snareRoll(snare, bar, roll));
  return notes;
}

/** One bar of boss bass: rolling sixteenths jumping between the root and its octave. */
export function bossBassBar(style: MusicStyle, bar: BarContext): Note[] {
  const [root = 36] = bar.chord;
  return Array.from({ length: STEPS }, (_, s) =>
    note(
      style.instruments.bass,
      bar.beat + s * STEP,
      STEP * 0.85,
      s % 2 ? root + 12 : root,
      s % 4 ? 0.75 : 1,
    ),
  );
}

/** The stabs' steps: 3-3-2, twice a bar. */
const STAB_STEPS = [0, 3, 6, 8, 11, 14];

/** Chord stabs (root, fifth, octave, an octave over the bass) on a restless 3-3-2 rhythm. */
export function stabBar(bar: BarContext): Note[] {
  if (bar.energy < 2) return [];
  const [root = 36, , fifth = root + 7] = bar.chord;
  const voicing = [root + 12, fifth + 12, root + 24];
  return STAB_STEPS.flatMap((s) =>
    voicing.map((pitch) =>
      note('stab', bar.beat + s * STEP, STEP * 1.5, pitch, s % 8 ? 0.65 : 0.85),
    ),
  );
}

/** A rising noise sweep over a section's last bar, into the next section. */
export function riserBar(bar: BarContext): Note[] {
  return bar.fill ? [note('riser', bar.beat, BEATS_PER_BAR, DRUM_PITCH, 0.8)] : [];
}
