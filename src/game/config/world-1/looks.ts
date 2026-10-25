import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';

/*
 * How the World 1 levels look (P06-R05, R06): a clear sky over a turquoise sea for 1-1, warm
 * dry light on the coast, then the desert under a hot haze, and the city at dusk with its lights
 * on. Every look starts from Level Zero's and changes the sky, the light and the ground.
 * Gamma-space RGB, 0..1.
 */

type Rgb = readonly [number, number, number];

/** Desert sand (P06-R06): warm, fine-grained, with dark grains. */
const SAND = texture(
  [
    [0.76, 0.6, 0.4],
    [0.81, 0.66, 0.45],
    [0.86, 0.72, 0.5],
  ],
  18,
  { speckle: 0.025, speckleColor: [0.52, 0.38, 0.24] },
);

/** Dry earth and scrub of the coast. */
const DRY_EARTH = texture(
  [
    [0.5, 0.42, 0.3],
    [0.6, 0.51, 0.37],
    [0.68, 0.6, 0.45],
  ],
  12,
  { speckle: 0.04, speckleColor: [0.38, 0.38, 0.22] },
);

/** Red-brown desert rock, layered: what the sand gives way to on slopes. */
const DESERT_ROCK = texture(
  [
    [0.42, 0.28, 0.2],
    [0.56, 0.38, 0.27],
    [0.66, 0.48, 0.35],
  ],
  8,
  { strata: 0.45 },
);

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

/** The two cloud layers of Level Zero, with another coverage each. */
const clouds = (low: number, high: number) => {
  const [a, b] = LEVEL_ZERO_LOOK.clouds;
  return [
    { ...a, coverage: low },
    { ...b, coverage: high },
  ];
};

/** 1-1: midday over a clear turquoise sea, white sand, scattered clouds. */
export const LEVEL_1_1_LOOK = {
  ...LEVEL_ZERO_LOOK,
  sky: sky([0.7, 0.8, 0.9], [0.86, 0.9, 0.95], [0.25, 0.48, 0.82], 0.7),
  sun: sun(55, 20, [1, 0.95, 0.85], 1.6),
  ambient: { sky: [0.66, 0.76, 0.9], ground: [0.32, 0.34, 0.32], intensity: 0.65 },
  terrain: {
    ...LEVEL_ZERO_LOOK.terrain,
    ground: DRY_EARTH,
    sand: SAND,
    shore: {
      ...LEVEL_ZERO_LOOK.terrain.shore,
      sand: [0.86, 0.78, 0.6],
      shallow: [0.1, 0.62, 0.6],
      deep: [0.02, 0.2, 0.32],
    },
  },
  sea: { ...LEVEL_ZERO_LOOK.sea, color: [0.02, 0.2, 0.32] },
  clouds: clouds(0.35, 0.2),
} as const;

/** 1-2: warm afternoon light on a dry coast. */
export const LEVEL_1_2_LOOK = {
  ...LEVEL_1_1_LOOK,
  sky: sky([0.8, 0.74, 0.62], [0.94, 0.82, 0.62], [0.32, 0.48, 0.74], 0.65),
  sun: sun(40, 30, [1, 0.88, 0.7], 1.6),
  ambient: { sky: [0.7, 0.7, 0.75], ground: [0.4, 0.33, 0.25], intensity: 0.6 },
  terrain: { ...LEVEL_1_1_LOOK.terrain, steep: DESERT_ROCK },
  clouds: clouds(0.2, 0.12),
} as const;

/** The desert: sand everywhere, red rock on the slopes, a hot pale haze, few clouds. */
const DESERT_TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  low: SAND,
  ground: SAND,
  sand: SAND,
  steep: DESERT_ROCK,
  // Only cliffs (mesas, canyon walls) are bare rock: the lee sides of the dunes stay sand.
  steepSlope: [0.95, 1.35],
  tints: [
    [1.05, 0.98, 0.9],
    [0.9, 0.84, 0.78],
  ],
} as const;

/** 1-3: the open desert at noon. */
export const LEVEL_1_3_LOOK = {
  ...LEVEL_ZERO_LOOK,
  sky: sky([0.88, 0.8, 0.66], [0.96, 0.86, 0.68], [0.36, 0.52, 0.76], 0.7),
  fog: { start: 1100, end: 2800 },
  // A sun from the side, not too high, so the dunes cast shadows and show their shapes.
  sun: sun(30, 70, [1, 0.93, 0.78], 2),
  ambient: { sky: [0.75, 0.74, 0.76], ground: [0.48, 0.38, 0.26], intensity: 0.45 },
  terrain: DESERT_TERRAIN,
  clouds: clouds(0.08, 0.06),
} as const;

/** 1-4: late afternoon over the desert towns, longer shadows. */
export const LEVEL_1_4_LOOK = {
  ...LEVEL_1_3_LOOK,
  sky: sky([0.86, 0.72, 0.56], [0.98, 0.76, 0.5], [0.3, 0.42, 0.7], 0.65),
  sun: sun(34, 35, [1, 0.8, 0.58], 1.6),
  ambient: { sky: [0.66, 0.64, 0.7], ground: [0.46, 0.34, 0.22], intensity: 0.6 },
  clouds: clouds(0.12, 0.08),
} as const;

/** 1-5: the city in the golden evening light, its windows and neon on. */
export const LEVEL_1_5_LOOK = {
  ...LEVEL_1_3_LOOK,
  sky: sky([0.78, 0.62, 0.55], [0.98, 0.68, 0.48], [0.24, 0.32, 0.6], 0.6),
  fog: { start: 1000, end: 2600 },
  sun: sun(30, 35, [1, 0.74, 0.52], 1.7),
  ambient: { sky: [0.62, 0.6, 0.72], ground: [0.4, 0.3, 0.24], intensity: 0.65 },
  props: { ...LEVEL_ZERO_LOOK.props, lightIntensity: 1.3 },
  glow: { intensity: 0.4, blurKernelSize: 16 },
  clouds: clouds(0.15, 0.1),
} as const;
