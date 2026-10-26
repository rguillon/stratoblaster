/** Scales, as semitones above their root. */
export const SCALES = {
  major: [0, 2, 4, 5, 7, 9, 11],
  mixolydian: [0, 2, 4, 5, 7, 9, 10],
  minor: [0, 2, 3, 5, 7, 8, 10],
  dorian: [0, 2, 3, 5, 7, 9, 10],
  phrygian: [0, 1, 3, 5, 7, 8, 10],
  harmonicMinor: [0, 2, 3, 5, 7, 8, 11],
} as const;

/** How the drums go: four on the floor, half time, tribal toms and shakers, heavy and slow. */
export type DrumFeel = 'four' | 'half' | 'tribal' | 'heavy';

/** How the bass goes: pumping eighths, long notes, syncopated plucks, driving pulses. */
export type BassFeel = 'eighths' | 'long' | 'syncopated' | 'pulse';

/** The instrument of each part (keys of `INSTRUMENTS`). */
export interface StyleInstruments {
  readonly kick: string;
  readonly snare: string;
  readonly hat: string;
  /** Extra percussion (open hat, shaker, toms). */
  readonly perc: string;
  readonly bass: string;
  readonly pad: string;
  readonly arp: string;
  readonly lead: string;
}

/**
 * A world's musical style (P12-R06): its levels share it but differ in key, tempo, chords,
 * melody and rhythm.
 */
export interface MusicStyle {
  /** BPM range of its level tracks. */
  readonly tempo: readonly [number, number];
  /** Its boss track is this many BPM faster than its fastest level track. */
  readonly bossBoost: readonly [number, number];
  readonly scales: readonly (readonly number[])[];
  /** The boss track's scale: darker. */
  readonly bossScale: readonly number[];
  /** MIDI pitches the keys' roots are picked from (bass register). */
  readonly roots: readonly number[];
  /** Chord progressions: scale degrees (0 = the root's chord), one chord per two bars. */
  readonly progressions: readonly (readonly number[])[];
  readonly instruments: StyleInstruments;
  readonly drums: DrumFeel;
  readonly bass: BassFeel;
  /** Arpeggio notes per beat. */
  readonly arpRate: number;
  /** Octaves above the bass the pad, arpeggio and lead play at. */
  readonly octaves: { readonly pad: number; readonly arp: number; readonly lead: number };
}

/**
 * The four worlds' styles (P12-R06, tempo ranges from the phase's tunables): World 1 (desert and
 * sea) bright and driving, World 2 (Frozen North) cold and airy, World 3 (Jungle) percussive,
 * World 4 (Volcanic Lands) dark and heavy.
 */
export const WORLD_STYLES: Readonly<Record<number, MusicStyle>> = {
  1: {
    tempo: [120, 132],
    bossBoost: [20, 30],
    scales: [SCALES.major, SCALES.mixolydian, SCALES.dorian],
    bossScale: SCALES.minor,
    roots: [38, 40, 41, 43, 45],
    progressions: [
      [0, 4, 5, 3],
      [5, 3, 0, 4],
      [0, 6, 3, 0],
      [0, 3, 4, 3],
      [5, 4, 3, 4],
    ],
    instruments: {
      kick: 'kick',
      snare: 'snare',
      hat: 'hat',
      perc: 'open-hat',
      bass: 'bass-saw',
      pad: 'pad-warm',
      arp: 'arp-pluck',
      lead: 'lead-square',
    },
    drums: 'four',
    bass: 'eighths',
    arpRate: 4,
    octaves: { pad: 2, arp: 3, lead: 2 },
  },
  2: {
    tempo: [100, 112],
    bossBoost: [20, 30],
    scales: [SCALES.dorian, SCALES.minor, SCALES.major],
    bossScale: SCALES.harmonicMinor,
    roots: [36, 38, 39, 41, 43],
    progressions: [
      [0, 5, 2, 6],
      [0, 3, 0, 4],
      [5, 6, 0, 0],
      [0, 2, 5, 4],
      [3, 0, 6, 4],
    ],
    instruments: {
      kick: 'kick',
      snare: 'clap',
      hat: 'hat',
      perc: 'open-hat',
      bass: 'bass-soft',
      pad: 'pad-cold',
      arp: 'arp-glass',
      lead: 'bell',
    },
    drums: 'half',
    bass: 'long',
    arpRate: 2,
    octaves: { pad: 2, arp: 3, lead: 2 },
  },
  3: {
    tempo: [112, 124],
    bossBoost: [20, 30],
    scales: [SCALES.dorian, SCALES.minor, SCALES.mixolydian],
    bossScale: SCALES.phrygian,
    roots: [38, 40, 41, 43, 45],
    progressions: [
      [0, 6, 5, 6],
      [0, 3, 6, 4],
      [0, 0, 5, 6],
      [3, 4, 0, 0],
      [0, 5, 3, 4],
    ],
    instruments: {
      kick: 'kick',
      snare: 'snare',
      hat: 'shaker',
      perc: 'tom',
      bass: 'bass-pluck',
      pad: 'pad-warm',
      arp: 'marimba',
      lead: 'lead-flute',
    },
    drums: 'tribal',
    bass: 'syncopated',
    arpRate: 2,
    octaves: { pad: 2, arp: 2, lead: 2 },
  },
  4: {
    tempo: [90, 104],
    bossBoost: [20, 30],
    scales: [SCALES.phrygian, SCALES.harmonicMinor, SCALES.minor],
    bossScale: SCALES.phrygian,
    roots: [33, 34, 36, 38, 40],
    progressions: [
      [0, 1, 0, 6],
      [0, 5, 1, 0],
      [0, 3, 1, 4],
      [0, 0, 5, 1],
      [5, 1, 0, 6],
    ],
    instruments: {
      kick: 'kick-heavy',
      snare: 'snare',
      hat: 'hat',
      perc: 'tom-low',
      bass: 'bass-heavy',
      pad: 'pad-dark',
      arp: 'arp-pluck',
      lead: 'lead-brass',
    },
    drums: 'heavy',
    bass: 'pulse',
    arpRate: 2,
    octaves: { pad: 2, arp: 2, lead: 2 },
  },
};

/** The calm menu theme's style (P12-R08). */
export const MENU_STYLE: MusicStyle = {
  tempo: [84, 84],
  bossBoost: [0, 0],
  scales: [SCALES.dorian],
  bossScale: SCALES.dorian,
  roots: [38],
  progressions: [[0, 5, 3, 4]],
  instruments: {
    kick: 'kick',
    snare: 'clap',
    hat: 'shaker',
    perc: 'open-hat',
    bass: 'bass-soft',
    pad: 'pad-warm',
    arp: 'arp-glass',
    lead: 'bell',
  },
  drums: 'half',
  bass: 'long',
  arpRate: 2,
  octaves: { pad: 2, arp: 3, lead: 2 },
};

/** `music_loop_min`: a track lasts at least this long before it repeats. */
export const MUSIC_LOOP_MIN_SECONDS = 60;

/** Bars of a section: tracks are made of whole sections. */
export const SECTION_BARS = 8;

/** Beats in a bar (4/4). */
export const BEATS_PER_BAR = 4;
