import type { SkyScript } from '../../../core/scenery/sky-look';
import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';

/*
 * How the World 2 levels look (P08-R04, R06, R07): snow and snow-covered rock that shows dark
 * rock on its cliffs, blue-white glacier ice (the `sand` cover), flat cracked lake ice (the `low`
 * ground), a dark cold sea, snowy roads with dark wheel tracks; and for each level its time of
 * day, clouds and weather along its length. Gamma-space RGB, 0..1.
 */

type Rgb = readonly [number, number, number];

/** Snow: bright, with a faint blue shade. */
const SNOW = texture(
  [
    [0.78, 0.82, 0.9],
    [0.87, 0.9, 0.95],
    [0.95, 0.96, 0.99],
  ],
  10,
  { speckle: 0.012, speckleColor: [0.7, 0.76, 0.86] },
);

/** Dark rock under the snow, layered: the cliffs and steep slopes. */
const DARK_ROCK = texture(
  [
    [0.15, 0.15, 0.17],
    [0.23, 0.23, 0.26],
    [0.32, 0.32, 0.35],
  ],
  8,
  { strata: 0.35 },
);

/** Frozen lakes: flat, shiny ice with crack lines. */
const LAKE_ICE = texture(
  [
    [0.5, 0.64, 0.76],
    [0.64, 0.78, 0.88],
    [0.78, 0.88, 0.95],
  ],
  6,
  { octaves: 3, cracks: 0.75 },
);

/** Glacier ice: blue-white, streaked. */
const GLACIER_ICE = texture(
  [
    [0.56, 0.7, 0.84],
    [0.7, 0.82, 0.92],
    [0.84, 0.91, 0.97],
  ],
  9,
  { strata: 0.25, cracks: 0.35 },
);

/** Tundra moss showing through thin snow. */
const TUNDRA = texture(
  [
    [0.5, 0.54, 0.52],
    [0.66, 0.7, 0.7],
    [0.82, 0.85, 0.88],
  ],
  14,
  { speckle: 0.04, speckleColor: [0.4, 0.42, 0.34] },
);

/** Trodden snow over concrete in the towns and the mines. */
const SNOWY_PAVING = texture(
  [
    [0.5, 0.52, 0.56],
    [0.62, 0.64, 0.68],
    [0.74, 0.76, 0.8],
  ],
  10,
  { speckle: 0.03, speckleColor: [0.36, 0.37, 0.4] },
);

const SEA: Rgb = [0.02, 0.07, 0.11];

/** The frozen ground of World 2. */
const FROZEN_TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  low: LAKE_ICE,
  ground: SNOW,
  steep: DARK_ROCK,
  high: SNOW,
  lush: TUNDRA,
  paved: SNOWY_PAVING,
  sand: GLACIER_ICE,
  lowHeight: 6,
  heightBlend: 4,
  // Snow stays on all but the cliffs.
  steepSlope: [0.4, 0.75],
  tints: [
    [1.02, 1.02, 1.04],
    [0.92, 0.94, 0.98],
  ],
  shore: {
    ...LEVEL_ZERO_LOOK.terrain.shore,
    sand: [0.62, 0.64, 0.68],
    beach: 3,
    shallow: [0.08, 0.24, 0.3],
    deep: SEA,
    foam: { ...LEVEL_ZERO_LOOK.terrain.shore.foam, color: [0.94, 0.96, 1] },
  },
} as const;

/** Snowy roads: packed snow, dark wheel tracks along their lanes. */
const SNOWY_ROADS = {
  ...LEVEL_ZERO_LOOK.roads,
  main: [0.6, 0.62, 0.66],
  cross: [0.8, 0.82, 0.87],
  wear: 0.35,
  centreLine: {
    color: [0.3, 0.31, 0.34],
    laneColor: [0.34, 0.35, 0.38],
    width: 0.9,
    dash: 6,
    lift: 0.05,
  },
} as const;

/** A World 2 look: the frozen ground and its sky script (P08-R06). */
const polar = (atmosphere: SkyScript) =>
  ({
    ...LEVEL_ZERO_LOOK,
    terrain: FROZEN_TERRAIN,
    sea: { ...LEVEL_ZERO_LOOK.sea, color: SEA, alpha: 0.5 },
    roads: SNOWY_ROADS,
    glow: { intensity: 0.4, blurKernelSize: 16 },
    atmosphere,
  }) as const;

const snow = (strength: number) => ({ kind: 'snow', strength }) as const;

/** 2-1: dawn over a dark sea, pink-orange clouds, no weather. */
export const LEVEL_2_1_LOOK = polar({ start: { timeOfDay: 'dawn', clouds: [0.25, 0.15] } });

/** 2-2: a crisp clear morning; light snow over the second half. */
export const LEVEL_2_2_LOOK = polar({
  start: { timeOfDay: 'morning', clouds: [0.2, 0.3] },
  changes: [
    {
      from: 150,
      to: 170,
      look: { timeOfDay: 'morning', clouds: [0.3, 0.35], weather: snow(0.2) },
    },
  ],
});

/** 2-3: an overcast midday, light grey clouds, snow falling; flat soft light. */
export const LEVEL_2_3_LOOK = polar({
  start: { timeOfDay: 'midday', clouds: [0.8, 0.6], storm: 0.3, weather: snow(0.4) },
});

/** The 2-4 afternoon under dark storm clouds, with snow of `strength`. */
const storm = (strength: number) =>
  ({ timeOfDay: 'afternoon', clouds: [0.9, 0.8], storm: 0.85, weather: snow(strength) }) as const;

/** 2-4: snow growing into a blizzard in the second half, clearing for the final boss. */
export const LEVEL_2_4_LOOK = polar({
  start: storm(0.5),
  changes: [
    // A full blizzard from the second half (2:30, the mini boss) on.
    { from: 125, to: 150, look: storm(1) },
    { from: 270, to: 292, look: storm(0.3) },
  ],
});

/** 2-5: dusk turning to night over the first third, then an aurora over the lit city. */
export const LEVEL_2_5_LOOK = polar({
  start: { timeOfDay: 'dusk', clouds: [0.3, 0.2] },
  changes: [{ from: 0, to: 100, look: { timeOfDay: 'night', clouds: [0.1, 0.05], aurora: 1 } }],
});
