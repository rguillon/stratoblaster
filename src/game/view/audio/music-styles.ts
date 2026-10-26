/** Scales, as semitones above their root. */
export const SCALES = {
  minor: [0, 2, 3, 5, 7, 8, 10],
  phrygian: [0, 1, 3, 5, 7, 8, 10],
  harmonicMinor: [0, 2, 3, 5, 7, 8, 11],
} as const;

/** How the drums go: four on the floor, a driving backbeat, tribal (shakers and toms), heavy. */
export type DrumFeel = 'four' | 'backbeat' | 'tribal' | 'heavy';

/** How the bass goes: pumping octave eighths, syncopated plucks, rolling sixteenths. */
export type BassFeel = 'eighths' | 'syncopated' | 'rolling';

/** The instrument of each part (keys of `INSTRUMENTS`). */
export interface StyleInstruments {
  readonly kick: string;
  readonly snare: string;
  readonly hat: string;
  /** The off-beat open hat, or the tribal toms. */
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
  /** The boss track's scale: darker and tenser (its chords: `BOSS_PROGRESSIONS`). */
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
  /**
   * Energy shapes its tracks pick from (0 a breakdown … 2 full), one value per 8-bar section;
   * the composer's own when omitted.
   */
  readonly energies?: readonly (readonly number[])[];
  /** Octaves above the bass the pad, arpeggio and lead play at. */
  readonly octaves: { readonly pad: number; readonly arp: number; readonly lead: number };
}

/**
 * The four worlds' styles (P12-R06, tempo ranges from the phase's tunables), all energetic
 * darksynth (reviewer, 2026-10-26): minor and phrygian keys, heavy kicks, growling basses, dark
 * pads. World 1 (desert and sea) the outrun drive (four on the floor, pumping bass, supersaw lead);
 * World 2 (Frozen North) cold, with glassy bells on a driving beat; World 3 (Jungle) on toms and
 * shakers; World 4 (Volcanic Lands) the heaviest.
 */
export const WORLD_STYLES: Readonly<Record<number, MusicStyle>> = {
  1: {
    tempo: [128, 140],
    bossBoost: [20, 30],
    scales: [SCALES.minor, SCALES.harmonicMinor, SCALES.phrygian],
    bossScale: SCALES.harmonicMinor,
    roots: [38, 40, 41, 43, 45],
    progressions: [
      [0, 4, 5, 3],
      [5, 3, 0, 4],
      [0, 6, 3, 0],
      [0, 5, 2, 6],
      [5, 4, 3, 4],
    ],
    instruments: {
      kick: 'kick-heavy',
      snare: 'snare-gated',
      hat: 'hat',
      perc: 'open-hat',
      bass: 'bass-heavy',
      pad: 'pad-dark',
      arp: 'arp-pluck',
      lead: 'lead-saw',
    },
    drums: 'four',
    bass: 'eighths',
    arpRate: 4,
    octaves: { pad: 2, arp: 3, lead: 2 },
  },
  2: {
    tempo: [112, 124],
    bossBoost: [20, 30],
    scales: [SCALES.minor, SCALES.harmonicMinor, SCALES.phrygian],
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
      kick: 'kick-heavy',
      snare: 'snare-gated',
      hat: 'hat',
      perc: 'open-hat',
      bass: 'bass-dream',
      pad: 'pad-dream',
      arp: 'arp-glass',
      lead: 'bell',
    },
    drums: 'backbeat',
    bass: 'eighths',
    arpRate: 4,
    octaves: { pad: 2, arp: 3, lead: 2 },
  },
  3: {
    tempo: [120, 132],
    bossBoost: [20, 30],
    scales: [SCALES.phrygian, SCALES.minor, SCALES.harmonicMinor],
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
      kick: 'kick-heavy',
      snare: 'snare-gated',
      hat: 'shaker',
      perc: 'tom',
      bass: 'bass-pluck',
      pad: 'pad-dark',
      arp: 'arp-square',
      lead: 'lead-square',
    },
    drums: 'tribal',
    bass: 'syncopated',
    arpRate: 4,
    octaves: { pad: 2, arp: 2, lead: 2 },
  },
  4: {
    tempo: [104, 116],
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
      snare: 'snare-gated',
      hat: 'hat',
      perc: 'open-hat',
      bass: 'bass-heavy',
      pad: 'pad-dark',
      arp: 'arp-pluck',
      lead: 'lead-brass',
    },
    drums: 'heavy',
    bass: 'rolling',
    arpRate: 4,
    octaves: { pad: 2, arp: 2, lead: 2 },
  },
};

/**
 * The menu theme's style (P12-R08, synthwave reviews): mid-tempo darksynth in a minor key, with
 * the classic i–VI–III–VII chords, a backbeat, a pumping octave bass, a plucked arpeggio and a
 * supersaw lead; slower than every level.
 */
export const MENU_STYLE: MusicStyle = {
  tempo: [100, 100],
  bossBoost: [0, 0],
  scales: [SCALES.minor],
  bossScale: SCALES.minor,
  roots: [40],
  progressions: [
    [0, 5, 2, 6],
    [0, 5, 3, 4],
    [5, 3, 0, 6],
  ],
  instruments: {
    kick: 'kick-heavy',
    snare: 'snare-gated',
    hat: 'hat',
    perc: 'open-hat',
    bass: 'bass-heavy',
    pad: 'pad-dark',
    arp: 'arp-pluck',
    lead: 'lead-saw',
  },
  drums: 'backbeat',
  bass: 'eighths',
  arpRate: 4,
  // Never a bare breakdown: the menus always have a full track (synthwave review).
  energies: [[1, 2, 1, 2, 2]],
  octaves: { pad: 2, arp: 3, lead: 2 },
};

/** `music_loop_min`: a track lasts at least this long before it repeats. */
export const MUSIC_LOOP_MIN_SECONDS = 60;

/** Bars of a section: tracks are made of whole sections. */
export const SECTION_BARS = 8;

/** Beats in a bar (4/4). */
export const BEATS_PER_BAR = 4;
