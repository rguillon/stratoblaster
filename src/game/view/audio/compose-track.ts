import type { Note, Track } from '../../../audio/audio-types';
import { createRng, pick, randomIn, type Random } from '../../../core/math/rng';
import { makeMotif, motifBars, scalePitch, type Motif } from './compose-melody';
import {
  arpBar,
  arpShape,
  bassBar,
  bassSteps,
  drumBar,
  padBar,
  type BarContext,
} from './compose-parts';
import {
  BEATS_PER_BAR,
  MUSIC_LOOP_MIN_SECONDS,
  SECTION_BARS,
  type MusicStyle,
} from './music-styles';

/** What to compose: a level's track, its world's boss track, or the menu theme. */
export interface TrackRequest {
  readonly id: string;
  readonly style: MusicStyle;
  /** Seeds the choices: the same seed always gives the same track (P12-R06). */
  readonly seed: number;
  /** Faster and more intense (P12-R07). */
  readonly boss?: boolean;
}

/** A seed from a text (FNV-1a), so a level's id picks its music. */
export function seedOf(text: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

/** One section of a track: its chords, its melody and how intense it is. */
interface Section {
  readonly progression: readonly number[];
  readonly motif: Motif;
  readonly energy: number;
}

/** The tempo of a track: in its style's range, or 20–30 BPM above it for a boss (P12-R07). */
function tempoOf(request: TrackRequest, random: Random): number {
  const { tempo, bossBoost } = request.style;
  if (request.boss) return Math.round(tempo[1] + randomIn(random, bossBoost));
  return Math.round(randomIn(random, [tempo[0], tempo[1] + 1]) - 0.5);
}

/** Whole sections, enough for the track to last at least `music_loop_min` (P12-R06). */
function sectionCount(bpm: number): number {
  const bars = (MUSIC_LOOP_MIN_SECONDS * bpm) / 60 / BEATS_PER_BAR;
  return Math.ceil(bars / SECTION_BARS);
}

/**
 * The energy of each section: a level builds up, breaks down and comes back; a boss fight is
 * intense all along, with one shorter breath.
 */
/** A level's energy shapes: it builds up, breaks down to its arpeggio and pads, comes back. */
const LEVEL_ENERGIES: readonly (readonly number[])[] = [
  [1, 2, 1, 0, 2],
  [1, 1, 2, 0, 2],
  [1, 2, 0, 2, 1],
];

function energies(request: TrackRequest, count: number, random: Random): number[] {
  if (request.boss) return Array.from({ length: count }, (_, i) => (i === count - 2 ? 1 : 2));
  const shape = pick(random, request.style.energies ?? LEVEL_ENERGIES);
  return Array.from({ length: count }, (_, i) => shape[i % shape.length] ?? 1);
}

/** Two or three different sections (verse, chorus, bridge), repeated in the track's order. */
function sections(request: TrackRequest, count: number, random: Random): Section[] {
  const { progressions } = request.style;
  const themes = Array.from({ length: Math.min(3, progressions.length) }, (_, i) => ({
    progression: progressions[
      (Math.floor(random() * progressions.length) + i) % progressions.length
    ] ?? [0],
    motif: makeMotif(random),
  }));
  const order = pick(random, [
    [0, 1, 0, 2, 1],
    [0, 0, 1, 2, 1],
    [0, 1, 2, 1, 0],
  ]);
  return energies(request, count, random).map((energy, i) => {
    const theme = themes[(order[i % order.length] ?? 0) % themes.length] ?? themes[0];
    return { progression: theme?.progression ?? [0], motif: theme?.motif ?? [], energy };
  });
}

/** The chord of scale step `degree`: a triad in the bass register. */
function chord(scale: readonly number[], degree: number): number[] {
  return [0, 2, 4].map((third) => scalePitch(scale, degree + third));
}

/** The notes of one section, bar by bar. */
function sectionNotes(
  request: TrackRequest,
  section: Section,
  start: number,
  parts: {
    scale: readonly number[];
    random: Random;
    bass: readonly number[];
    arp: readonly number[];
  },
): Note[] {
  const { style } = request;
  const notes: Note[] = [];
  for (let b = 0; b < SECTION_BARS; b++) {
    const degree = section.progression[Math.floor(b / 2) % section.progression.length] ?? 0;
    const bar: BarContext = {
      beat: (start + b) * BEATS_PER_BAR,
      chord: chord(parts.scale, degree),
      scale: parts.scale,
      energy: section.energy,
      fill: b === SECTION_BARS - 1,
    };
    const kicks = request.boss && b % 2 === 1 ? [14] : [];
    notes.push(...drumBar(style, bar, parts.random, kicks), ...bassBar(style, bar, parts.bass));
    notes.push(...padBar(style, bar), ...arpBar(style, bar, parts.arp));
    if (b % 2 === 0) notes.push(...motifBars(style, section.motif, bar, degree, b === 6 ? 1 : 0));
  }
  return notes;
}

/**
 * Composes a looping track (P12-R06..R08): a key, a tempo and sections picked from the style by a
 * seeded generator, each section's bars made of drums, bass, pad, arpeggio and melody. Pure: the
 * same request always gives the same notes.
 */
export function composeTrack(request: TrackRequest): Track {
  const random = createRng(request.seed);
  const { style } = request;
  const bpm = tempoOf(request, random);
  const steps = request.boss ? style.bossScale : pick(random, style.scales);
  const root = pick(random, style.roots);
  const scale = steps.map((s) => root + s);
  const parts = { scale, random, bass: bassSteps(style, random), arp: arpShape(random) };
  const list = sections(request, sectionCount(bpm), random);
  const notes = list.flatMap((section, i) =>
    sectionNotes(request, section, i * SECTION_BARS, parts),
  );
  notes.sort((a, b) => a.beat - b.beat);
  return {
    id: request.id,
    bpm,
    beats: list.length * SECTION_BARS * BEATS_PER_BAR,
    notes,
    loop: true,
  };
}
