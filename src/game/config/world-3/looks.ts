import type { SkyLook, SkyScript } from '../../../core/scenery/sky-look';
import { LEVEL_ZERO_LOOK, texture } from '../scenery-look';

/*
 * How the World 3 levels look (P09-R04, R06): dark wet jungle soil, moss-green slopes, red-brown
 * mud banks by the water (the `low` ground), grey-green cliff rock, old paved stone round the
 * ruins, muddy sandbanks (the `sand` cover), muddy green-brown water flowing down the screen, red
 * dirt roads; and for each level its time of day, clouds and weather along its length.
 * Gamma-space RGB, 0..1.
 */

type Rgb = readonly [number, number, number];

/** Dark, wet jungle soil under the trees. */
const JUNGLE_SOIL = texture(
  [
    [0.13, 0.12, 0.08],
    [0.19, 0.17, 0.11],
    [0.25, 0.22, 0.14],
  ],
  12,
  { speckle: 0.04, speckleColor: [0.12, 0.2, 0.08] },
);

/** Moss on the slopes and the forest floor. */
const MOSS = texture(
  [
    [0.12, 0.2, 0.08],
    [0.18, 0.29, 0.11],
    [0.25, 0.37, 0.15],
  ],
  14,
  { speckle: 0.04, speckleColor: [0.3, 0.26, 0.12] },
);

/** Red-brown mud banks along the water. */
const MUD = texture(
  [
    [0.3, 0.17, 0.1],
    [0.39, 0.23, 0.13],
    [0.47, 0.3, 0.18],
  ],
  14,
  { speckle: 0.03, speckleColor: [0.22, 0.13, 0.08] },
);

/** Grey-green cliff rock, layered. */
const CLIFF_ROCK = texture(
  [
    [0.2, 0.22, 0.19],
    [0.29, 0.31, 0.27],
    [0.38, 0.4, 0.35],
  ],
  8,
  { strata: 0.35, speckle: 0.03, speckleColor: [0.16, 0.26, 0.1] },
);

/** Old paved stone round the ruins, cracked, moss in the joints. */
const OLD_PAVING = texture(
  [
    [0.36, 0.34, 0.27],
    [0.45, 0.43, 0.35],
    [0.54, 0.52, 0.43],
  ],
  9,
  { cracks: 0.6, speckle: 0.03, speckleColor: [0.2, 0.3, 0.12] },
);

/** Muddy sandbanks of the delta. */
const SANDBANK = texture(
  [
    [0.4, 0.34, 0.24],
    [0.49, 0.42, 0.3],
    [0.57, 0.5, 0.37],
  ],
  16,
  { speckle: 0.02, speckleColor: [0.3, 0.24, 0.16] },
);

/** Muddy green-brown water: the sea of 3-1, the rivers, swamps and lakes. */
const WATER: Rgb = [0.09, 0.12, 0.07];

/** The ground of World 3. */
const JUNGLE_TERRAIN = {
  ...LEVEL_ZERO_LOOK.terrain,
  low: MUD,
  ground: JUNGLE_SOIL,
  steep: CLIFF_ROCK,
  high: MOSS,
  lush: MOSS,
  paved: OLD_PAVING,
  sand: SANDBANK,
  lowHeight: 3,
  heightBlend: 3,
  highHeight: 95,
  steepSlope: [0.3, 0.62],
  tints: [
    [1.04, 1.06, 0.96],
    [0.86, 0.9, 0.82],
  ],
  shore: {
    ...LEVEL_ZERO_LOOK.terrain.shore,
    sand: [0.42, 0.3, 0.2],
    beach: 2,
    shallow: [0.27, 0.27, 0.15],
    deep: WATER,
    foam: { ...LEVEL_ZERO_LOOK.terrain.shore.foam, color: [0.78, 0.8, 0.7] },
  },
} as const;

/** Red dirt tracks, darker ruts along their lanes. */
const DIRT_ROADS = {
  ...LEVEL_ZERO_LOOK.roads,
  main: [0.46, 0.24, 0.14],
  cross: [0.52, 0.29, 0.17],
  wear: 0.4,
  centreLine: {
    color: [0.3, 0.16, 0.1],
    laneColor: [0.34, 0.18, 0.11],
    width: 0.9,
    dash: 6,
    lift: 0.05,
  },
} as const;

/** The water flows down the screen, the way the player came from (P09-R06). */
const RIVER_FLOW = [0, 16] as const;

/** A World 3 look: the jungle ground, `water` and the sky script (P09-R04). */
const jungle = (atmosphere: SkyScript, water: Rgb = WATER) =>
  ({
    ...LEVEL_ZERO_LOOK,
    terrain: { ...JUNGLE_TERRAIN, shore: { ...JUNGLE_TERRAIN.shore, deep: water } },
    sea: { ...LEVEL_ZERO_LOOK.sea, color: water, alpha: 0.6, sunGlint: 1.2, drift: RIVER_FLOW },
    roads: DIRT_ROADS,
    glow: { intensity: 0.45, blurKernelSize: 16 },
    atmosphere,
  }) as const;

const rain = (strength: number) => ({ kind: 'rain', strength }) as const;

/** The 3-1 morning: white clouds, a low warm sun. */
const MORNING: SkyLook = { timeOfDay: 'morning', clouds: [0.3, 0.2] };
/** The morning mist of 3-1 (`morning_mist`): the haze close and white over the water. */
export const MORNING_MIST = { fog: 0.4, white: 0.8 } as const;

/** 3-1: a morning mist over the delta, lifting over the first half. */
export const LEVEL_3_1_LOOK = jungle({
  start: { ...MORNING, mist: MORNING_MIST },
  changes: [{ from: 0, to: 150, look: MORNING }],
});

/** Bright, humid midday light, green under the canopy. */
const MIDDAY: SkyLook = { timeOfDay: 'midday', clouds: [0.5, 0.3], tint: [0.92, 1.08, 0.9] };

/** 3-2: a rain shower over the middle third, then clearing. */
export const LEVEL_3_2_LOOK = jungle({
  start: MIDDAY,
  changes: [
    { from: 92, to: 108, look: { ...MIDDAY, weather: rain(0.4) } },
    { from: 192, to: 208, look: MIDDAY },
  ],
});

/** The 3-3 thunderstorm: dark blue-grey clouds, heavy rain, lightning. */
const THUNDERSTORM: SkyLook = {
  timeOfDay: 'afternoon',
  clouds: [0.9, 0.9],
  storm: 1,
  weather: rain(0.8),
  lightning: 1,
};

/** 3-3: the storm builds over the first quarter, from half-covered skies without rain. */
export const LEVEL_3_3_LOOK = jungle({
  start: { timeOfDay: 'afternoon', clouds: [0.5, 0.5], storm: 0.3 },
  changes: [{ from: 0, to: 75, look: THUNDERSTORM }],
});

/** 3-4: a rainy dusk over the swamp, the labs, pumping stations and dam lit. */
export const LEVEL_3_4_LOOK = jungle(
  { start: { timeOfDay: 'dusk', clouds: [0.6, 0.4], weather: rain(0.3) } },
  [0.05, 0.07, 0.04],
);

/** 3-5: a rainy night over the lit city, the rain stopping and the clouds opening before the final boss. */
export const LEVEL_3_5_LOOK = jungle({
  start: { timeOfDay: 'night', clouds: [0.6, 0.4], weather: rain(0.5) },
  changes: [{ from: 250, to: 275, look: { timeOfDay: 'night', clouds: [0.2, 0.1] } }],
});
