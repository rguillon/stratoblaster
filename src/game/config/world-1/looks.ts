import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';

/*
 * How the World 1 levels look (P06-R05, R06, R10; reworked at the reviewer's request,
 * 2026-10-26): one ground for the whole world, from a turquoise sea over green grass and dry
 * earth to the sand, and a time of day per level, later and later: midday over the sea (1-1),
 * early afternoon on the green coast (1-2), late afternoon in the green country (1-3), sunset
 * over the dry lands (1-4) and dusk over the deep desert, its towns' lights on (1-5). Every look
 * starts from Level Zero's. Gamma-space RGB, 0..1.
 */

type Rgb = readonly [number, number, number];

/** Desert sand (P06-R06): warm, fine-grained, with dark grains. World 2 starts on it too. */
export const SAND = texture(
  [
    [0.76, 0.6, 0.4],
    [0.81, 0.66, 0.45],
    [0.86, 0.72, 0.5],
  ],
  18,
  { speckle: 0.025, speckleColor: [0.52, 0.38, 0.24] },
);

/** Dry earth: the ground where the grass turns dry, between the green land and the sand. */
export const DRY_EARTH = texture(
  [
    [0.5, 0.42, 0.3],
    [0.6, 0.51, 0.37],
    [0.68, 0.6, 0.45],
  ],
  12,
  { speckle: 0.04, speckleColor: [0.38, 0.38, 0.22] },
);

/** Fresh green grass of the islands, the coast and the meadows, with a few yellow tufts. */
const GRASS = texture(
  [
    [0.22, 0.34, 0.12],
    [0.3, 0.46, 0.16],
    [0.4, 0.55, 0.22],
  ],
  14,
  { speckle: 0.035, speckleColor: [0.6, 0.56, 0.28] },
);

/** Red-brown desert rock, layered: what the sand gives way to on slopes. */
export const DESERT_ROCK = texture(
  [
    [0.42, 0.28, 0.2],
    [0.56, 0.38, 0.27],
    [0.66, 0.48, 0.35],
  ],
  8,
  { strata: 0.45 },
);

/**
 * The ground of the whole world: dry earth by default, covered with grass, sand or pavement by
 * section (`surface`), so the land fades from green to sand along the levels.
 */
const TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  ground: DRY_EARTH,
  lush: GRASS,
  sand: SAND,
  shore: {
    ...LEVEL_ZERO_LOOK.terrain.shore,
    sand: [0.86, 0.78, 0.6],
    shallow: [0.1, 0.62, 0.6],
    deep: [0.02, 0.2, 0.32],
  },
} as const;

/** The dry levels: sand below, red rock on the cliffs, a warmer tint. */
const DRY_TERRAIN = {
  ...TERRAIN,
  low: SAND,
  steep: DESERT_ROCK,
  // Only cliffs (mesas, canyon walls) are bare rock: the lee sides of the dunes stay sand.
  steepSlope: [0.95, 1.35],
  tints: [
    [1.05, 0.98, 0.9],
    [0.9, 0.84, 0.78],
  ],
} as const;

const sky = (haze: Rgb, horizon: Rgb, zenith: Rgb, intensity: number) => ({
  haze,
  stops: [
    { at: -1, color: [0.25, 0.22, 0.2] as Rgb },
    { at: 0, color: horizon },
    { at: 0.35, color: haze },
    { at: 1, color: zenith },
  ],
  environmentIntensity: intensity,
});

const sun = (elevationDeg: number, azimuthDeg: number, color: Rgb, intensity: number) => ({
  ...LEVEL_ZERO_LOOK.sun,
  elevationDeg,
  azimuthDeg,
  color,
  intensity,
});

/** The two cloud layers of Level Zero, with another coverage and colour each. */
const clouds = (low: number, high: number, color?: Rgb, shade?: Rgb) => {
  const [a, b] = LEVEL_ZERO_LOOK.clouds;
  const tint = color && shade ? { color, shade } : {};
  return [
    { ...a, coverage: low, ...tint },
    { ...b, coverage: high, ...tint },
  ];
};

/** 1-1: midday, the sun high, over a clear turquoise sea, scattered white clouds. */
export const LEVEL_1_1_LOOK = {
  ...LEVEL_ZERO_LOOK,
  sky: sky([0.7, 0.8, 0.9], [0.86, 0.9, 0.95], [0.22, 0.45, 0.82], 0.7),
  sun: sun(72, 20, [1, 0.97, 0.92], 1.7),
  ambient: { sky: [0.66, 0.76, 0.9], ground: [0.32, 0.36, 0.3], intensity: 0.65 },
  terrain: TERRAIN,
  sea: { ...LEVEL_ZERO_LOOK.sea, color: [0.02, 0.2, 0.32] },
  clouds: clouds(0.35, 0.2),
} as const;

/** 1-2: early afternoon on the green coast, a little warmer. */
export const LEVEL_1_2_LOOK = {
  ...LEVEL_1_1_LOOK,
  sky: sky([0.74, 0.8, 0.86], [0.9, 0.88, 0.84], [0.26, 0.46, 0.78], 0.7),
  sun: sun(55, 35, [1, 0.93, 0.82], 1.65),
  ambient: { sky: [0.66, 0.74, 0.86], ground: [0.34, 0.36, 0.28], intensity: 0.62 },
  clouds: clouds(0.3, 0.18),
} as const;

/** 1-3: late afternoon in the green country, golden light and longer shadows. */
export const LEVEL_1_3_LOOK = {
  ...LEVEL_1_1_LOOK,
  sky: sky([0.84, 0.76, 0.64], [0.96, 0.82, 0.6], [0.3, 0.44, 0.74], 0.65),
  sun: sun(35, 45, [1, 0.85, 0.64], 1.65),
  ambient: { sky: [0.68, 0.68, 0.76], ground: [0.4, 0.34, 0.24], intensity: 0.6 },
  clouds: clouds(0.22, 0.14, [1, 0.94, 0.84], [0.76, 0.68, 0.68]),
} as const;

/** 1-4: sunset over the dry lands: a low orange sun, a magenta haze, long shadows. */
export const LEVEL_1_4_LOOK = {
  ...LEVEL_ZERO_LOOK,
  sky: sky([0.86, 0.56, 0.52], [1, 0.62, 0.36], [0.26, 0.24, 0.52], 0.6),
  fog: { start: 1100, end: 2800 },
  sun: sun(14, 40, [1, 0.64, 0.38], 1.6),
  ambient: { sky: [0.66, 0.56, 0.72], ground: [0.46, 0.32, 0.24], intensity: 0.7 },
  terrain: DRY_TERRAIN,
  props: { ...LEVEL_ZERO_LOOK.props, lightIntensity: 1.15 },
  clouds: clouds(0.14, 0.1, [1, 0.72, 0.56], [0.62, 0.4, 0.5]),
} as const;

/** 1-5: dusk over the deep desert: the sun on the horizon, a violet sky, the town lights on. */
export const LEVEL_1_5_LOOK = {
  ...LEVEL_1_4_LOOK,
  sky: sky([0.7, 0.48, 0.6], [0.96, 0.5, 0.42], [0.2, 0.16, 0.4], 0.6),
  fog: { start: 1000, end: 2600 },
  // Low but still lighting the ground: in a darker dusk the ship was lost over the towns.
  sun: sun(8, 30, [1, 0.56, 0.4], 1.6),
  ambient: { sky: [0.66, 0.58, 0.82], ground: [0.44, 0.34, 0.34], intensity: 1 },
  props: { ...LEVEL_ZERO_LOOK.props, lightIntensity: 1.3 },
  glow: { intensity: 0.4, blurKernelSize: 16 },
  clouds: clouds(0.15, 0.1, [0.9, 0.56, 0.6], [0.46, 0.3, 0.46]),
} as const;
