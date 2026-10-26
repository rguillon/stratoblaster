import type { Note, Track } from '../../../audio/audio-types';
import type { Jingle } from '../../../audio/audio-bindings';
import { DRUM_PITCH } from './instruments';

/** [beat, beats, pitch] of a jingle's lead, pad chords at its start and end. */
type Line = readonly (readonly [number, number, number])[];

function line(instrument: string, notes: Line, velocity: number): Note[] {
  return notes.map(([beat, beats, pitch]) => ({ instrument, beat, beats, pitch, velocity }));
}

/** A short fanfare played once (P12-R07). */
function jingle(id: string, bpm: number, beats: number, notes: Note[]): Track {
  return { id, bpm, beats, notes: [...notes].sort((a, b) => a.beat - b.beat), loop: false };
}

/** "Level complete": a rising major fanfare. */
const COMPLETE = jingle('jingle-complete', 132, 8, [
  ...line(
    'lead-square',
    [
      [0, 0.5, 72],
      [0.5, 0.5, 76],
      [1, 0.5, 79],
      [1.5, 1.5, 84],
      [3.5, 0.5, 83],
      [4, 3, 84],
    ],
    0.9,
  ),
  ...line(
    'pad-warm',
    [
      [0, 3.5, 60],
      [0, 3.5, 64],
      [0, 3.5, 67],
      [3.5, 4, 65],
      [3.5, 4, 69],
      [3.5, 4, 72],
    ],
    0.8,
  ),
  ...line(
    'bass-saw',
    [
      [0, 3, 48],
      [3.5, 4, 53],
    ],
    0.9,
  ),
  ...line(
    'snare',
    [
      [3, 0.25, DRUM_PITCH],
      [3.25, 0.25, DRUM_PITCH],
    ],
    0.8,
  ),
  ...line('kick', [[4, 0.5, DRUM_PITCH]], 1),
]);

/** "Game over": a slow, falling minor line. */
const OVER = jingle('jingle-over', 84, 8, [
  ...line(
    'lead-brass',
    [
      [0, 1, 67],
      [1, 1, 66],
      [2, 1, 65],
      [3, 4, 64],
    ],
    0.85,
  ),
  ...line(
    'pad-dark',
    [
      [0, 3, 52],
      [0, 3, 55],
      [0, 3, 60],
      [3, 4.5, 48],
      [3, 4.5, 51],
      [3, 4.5, 55],
    ],
    0.8,
  ),
  ...line('bass-heavy', [[0, 7, 36]], 0.8),
]);

/** "Checkpoint reached": a short bright chime over the music. */
const CHECKPOINT = jingle('jingle-checkpoint', 120, 3, [
  ...line(
    'bell',
    [
      [0, 0.5, 79],
      [0.5, 0.5, 84],
      [1, 1.5, 88],
    ],
    1,
  ),
]);

/** The game's three jingles. */
export const JINGLES: Readonly<Record<Jingle, Track>> = {
  complete: COMPLETE,
  over: OVER,
  checkpoint: CHECKPOINT,
};
