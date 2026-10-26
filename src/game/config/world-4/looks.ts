import { ENEMY_LOOK } from '../enemy-look';
import type { SkyScript } from '../../../core/scenery/sky-look';
import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';

/*
 * How the World 4 levels look (P10-R04, R05, R08): black volcanic sand on the beaches and by the
 * water (the `sand` cover and the `low` ground), black and dark grey cracked basalt, grey ash in
 * drifts (the `lush` cover, and the tops of the cones), rust-red and sulphur-yellow mineral
 * stains, a dark sea in 4-1 and lava in 4-3 to 4-5, dark cracked ash-dusted roads; and for each
 * level its time of day, clouds, weather and the glow of the fire from below along its length.
 * Every look draws the enemy shots with a contrast core (P10-R07). Gamma-space RGB, 0..1.
 */

type Rgb = readonly [number, number, number];

const RUST: Rgb = [0.42, 0.18, 0.08];
const SULPHUR: Rgb = [0.62, 0.56, 0.14];

/** Black volcanic sand, glinting with grains of rock. */
const BLACK_SAND = texture(
  [
    [0.06, 0.06, 0.065],
    [0.1, 0.095, 0.1],
    [0.15, 0.14, 0.14],
  ],
  18,
  { speckle: 0.03, speckleColor: [0.3, 0.28, 0.26] },
);

/** Dark grey basalt with cracks, rust stains in them. */
const BASALT = texture(
  [
    [0.1, 0.1, 0.1],
    [0.16, 0.155, 0.15],
    [0.23, 0.22, 0.21],
  ],
  10,
  { cracks: 0.5, speckle: 0.03, speckleColor: RUST },
);

/** Black rock on the slopes, layered and cracked, sulphur stains round the vents. */
const BLACK_ROCK = texture(
  [
    [0.05, 0.05, 0.055],
    [0.11, 0.105, 0.105],
    [0.18, 0.17, 0.17],
  ],
  8,
  { strata: 0.3, cracks: 0.4, speckle: 0.025, speckleColor: SULPHUR },
);

/** Grey ash lying in drifts. */
const ASH = texture(
  [
    [0.36, 0.35, 0.33],
    [0.45, 0.44, 0.42],
    [0.54, 0.53, 0.5],
  ],
  14,
  { octaves: 4, speckle: 0.03, speckleColor: [0.24, 0.23, 0.22] },
);

/** Scorched industrial concrete, cracked, rust-stained. */
const SCORCHED_PAVING = texture(
  [
    [0.18, 0.17, 0.16],
    [0.25, 0.24, 0.23],
    [0.32, 0.31, 0.29],
  ],
  10,
  { cracks: 0.5, speckle: 0.04, speckleColor: RUST },
);

/** The dark sea of 4-1. */
const DARK_SEA: Rgb = [0.02, 0.035, 0.04];

/** The ground of World 4. */
const VOLCANIC_TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  low: BLACK_SAND,
  ground: BASALT,
  steep: BLACK_ROCK,
  high: ASH,
  lush: ASH,
  paved: SCORCHED_PAVING,
  sand: BLACK_SAND,
  lowHeight: 3,
  heightBlend: 3,
  highHeight: 75,
  steepSlope: [0.3, 0.62],
  // Rust-red and sulphur-yellow stains over wide patches.
  tints: [
    [1.12, 0.95, 0.86],
    [1.05, 1.03, 0.82],
  ],
  shore: {
    ...LEVEL_ZERO_LOOK.terrain.shore,
    sand: [0.09, 0.085, 0.085],
    beach: 2,
    shallow: [0.06, 0.08, 0.08],
    deep: DARK_SEA,
    foam: { ...LEVEL_ZERO_LOOK.terrain.shore.foam, color: [0.66, 0.66, 0.64] },
  },
} as const;

/** Dark cracked asphalt under a dust of ash. */
const ASH_ROADS = {
  ...LEVEL_ZERO_LOOK.roads,
  main: [0.15, 0.145, 0.14],
  cross: [0.24, 0.23, 0.22],
  wear: 0.5,
  centreLine: {
    color: [0.42, 0.41, 0.38],
    laneColor: [0.36, 0.35, 0.33],
    width: 0.35,
    dash: 4,
    lift: 0.05,
  },
} as const;

/** The lava of 4-3 to 4-5 (P10-R05): dark crust plates over a glowing melt. */
export const LAVA = {
  crust: [0.08, 0.03, 0.02],
  plate: [0.2, 0.07, 0.04],
  glow: [1, 0.35, 0.05],
  hot: [1, 0.85, 0.45],
  cell: 26,
  crack: 0.12,
  churn: 0.05,
  intensity: 1.3,
  edge: { color: [1, 0.4, 0.08], width: 1.6, cracks: 6 },
} as const;

/** The lava flows down the screen, the way the player came from; the magma lake slower. */
const LAVA_FLOW = [0, 10] as const;
const LAKE_FLOW = [0, 5] as const;

/** A World 4 look over the dark sea: the volcanic ground and the sky script (P10-R04). */
const volcanic = (atmosphere: SkyScript) =>
  ({
    ...LEVEL_ZERO_LOOK,
    terrain: VOLCANIC_TERRAIN,
    sea: { ...LEVEL_ZERO_LOOK.sea, color: DARK_SEA, alpha: 0.7, sunGlint: 1.2, drift: [2, 6] },
    roads: ASH_ROADS,
    glow: { intensity: 0.45, blurKernelSize: 16 },
    shotStyle: ENEMY_LOOK.contrast.style,
    atmosphere,
  }) as const;

/** A World 4 look over lava (P10-R05), flowing by `drift`. */
const molten = (atmosphere: SkyScript, drift: readonly [number, number] = LAVA_FLOW) =>
  ({
    ...volcanic(atmosphere),
    sea: { ...LEVEL_ZERO_LOOK.sea, color: LAVA.crust, alpha: 1, sunGlint: 0, drift, lava: LAVA },
    glow: { intensity: 0.6, blurKernelSize: 20 },
  }) as const;

const ash = (strength: number) => ({ kind: 'ash', strength }) as const;
const embers = (strength: number) => ({ kind: 'embers', strength }) as const;

/** Ash-tinted pink and grey clouds of the 4-1 dawn. */
export const ASH_PINK: Rgb = [0.95, 0.84, 0.86];
/** The smoke haze and steam of 4-1: the haze close, a little paler. */
export const SMOKE_HAZE = { fog: 0.75, white: 0.2 } as const;

/** 4-1: a red dawn behind a smoke haze, steam over the sea. */
export const LEVEL_4_1_LOOK = volcanic({
  start: { timeOfDay: 'dawn', clouds: [0.4, 0.3], cloudTint: ASH_PINK, mist: SMOKE_HAZE },
});

/** Brown-grey clouds of the ash cloud over 4-2. */
export const ASH_BROWN: Rgb = [0.8, 0.72, 0.62];
/** The dim, flat, yellowish light under the ash cloud. */
export const ASH_LIGHT: Rgb = [1.04, 0.96, 0.74];

/** 4-2: midday under an ash cloud, ash falling. */
export const LEVEL_4_2_LOOK = volcanic({
  start: {
    timeOfDay: 'midday',
    clouds: [0.9, 0.9],
    cloudTint: ASH_BROWN,
    tint: ASH_LIGHT,
    weather: ash(0.5),
  },
});

/** The orange glow of the lava under the clouds of 4-3. */
export const LAVA_GLOW: Rgb = [1, 0.42, 0.12];

/** 4-3: the sunset fades while the lava's glow takes over. */
export const LEVEL_4_3_LOOK = molten({
  start: {
    timeOfDay: 'dusk',
    clouds: [0.5, 0.4],
    storm: 0.5,
    underglow: { color: LAVA_GLOW, strength: 0.25 },
    weather: embers(0.4),
  },
  changes: [
    {
      from: 60,
      to: 280,
      look: {
        timeOfDay: 'night',
        clouds: [0.5, 0.4],
        storm: 0.5,
        underglow: { color: LAVA_GLOW, strength: 0.8 },
        weather: embers(0.4),
      },
    },
  ],
});

/** The furnaces' glow under the smoke of 4-4. */
export const FURNACE_GLOW: Rgb = [1, 0.5, 0.15];

/** 4-4: a night lit by the furnaces, ash and embers falling and rising. */
export const LEVEL_4_4_LOOK = molten({
  start: {
    timeOfDay: 'night',
    clouds: [0.6, 0.5],
    storm: 0.6,
    underglow: { color: FURNACE_GLOW, strength: 0.7 },
    weather: ash(0.3),
    secondWeather: embers(0.3),
  },
});

/** The deep red of the eruption over 4-5. */
export const ERUPTION_RED: Rgb = [1, 0.16, 0.08];

/** 4-5: the volcano erupts, the sky turning deep red and the embers growing to the final boss. */
export const LEVEL_4_5_LOOK = molten(
  {
    start: {
      timeOfDay: 'night',
      clouds: [0.7, 0.6],
      underglow: { color: ERUPTION_RED, strength: 0.6 },
      weather: embers(0.6),
    },
    changes: [
      {
        from: 180,
        to: 300,
        look: {
          timeOfDay: 'night',
          clouds: [0.7, 0.6],
          underglow: { color: ERUPTION_RED, strength: 1 },
          weather: embers(1),
        },
      },
    ],
  },
  LAKE_FLOW,
);
