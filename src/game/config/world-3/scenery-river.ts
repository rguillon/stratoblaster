import type { Channel, SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import { JUNGLE_PLANTS as PL, WORLD_3_GROUPS as G, WORLD_3_PROPS, WORLD_3_ROADS } from './props';

/*
 * The river levels of World 3 (P09-R03): 3-1, from the sea into a delta of muddy channels and
 * sandbanks, mangroves, then a single wide river into the first rainforest; 3-2, a winding river
 * through a dense rainforest canopy. Heights in world units above the water level (0): the
 * delta's channels, the rivers (channels cut below it) and later the swamps and lakes all hold
 * water at that level, but only 3-1's open sea is sea. Each level's `seconds` add up to 300
 * (P09-R02).
 */

/** The great river the player flies up, from the end of the delta to the temples. */
export const GREAT_RIVER = { x: 0, amplitude: 110, wavelength: 2200 } as const;

/** The great river cut into the ground, `halfWidth` wide at its muddy bed. */
export const river = (halfWidth: number, wall = 40): Channel => ({
  path: GREAT_RIVER,
  halfWidth,
  wall,
  floor: -8,
});

/** The low forested banks where 3-1 ends and 3-2 begins. */
export const RIVER_BANKS = smooth(10, 6, 480);

/** Ground of the delta around the water level: sandbanks, mud flats and channels. */
const delta = (
  name: string,
  seconds: number,
  [base, amplitude, wavelength]: readonly number[],
  extra: Partial<TerrainSection>,
): TerrainSection => ({
  name,
  seconds,
  relief: smooth(base ?? 0, amplitude ?? 6, wavelength ?? 260, 4),
  surface: { sandy: 0.5, lush: 0.2 },
  buildingDensity: 0.15,
  treeDensity: 0.4,
  trees: PL.delta,
  groups: [G.riverHuts],
  floatDensity: 0.35,
  ...extra,
});

/** A small river port at the end of 3-1, on the river 3-2 starts on. */
const RIVER_PORT: TerrainSection = {
  name: 'river port',
  seconds: 55,
  relief: RIVER_BANKS,
  channel: river(80),
  surface: { lush: 0.3, paved: 0.15 },
  buildingDensity: 0.45,
  treeDensity: 0.85,
  trees: PL.rainforest,
  groups: [G.riverPort, G.riverHuts],
  floatDensity: 0.1,
};

/** 3-1, River delta: sea, a delta of channels and sandbanks, then one wide river. */
const RIVER_DELTA: readonly TerrainSection[] = [
  {
    name: 'open sea',
    seconds: 35,
    relief: smooth(-55, 25, 520, 5),
    buildingDensity: 0,
    treeDensity: 0,
  },
  delta('delta mouth', 45, [-1, 6, 240], { treeDensity: 0.25, buildingDensity: 0.05 }),
  delta('mangrove channels', 60, [1.5, 6, 220], {
    surface: { sandy: 0.3, lush: 0.35 },
    treeDensity: 0.75,
    buildingDensity: 0.2,
  }),
  delta('green islands', 55, [3, 7, 300], {
    surface: { sandy: 0.15, lush: 0.5 },
    treeDensity: 0.75,
    trees: PL.forestEdge,
    buildingDensity: 0.25,
    floatDensity: 0.25,
  }),
  {
    name: 'forest edge',
    seconds: 50,
    relief: RIVER_BANKS,
    channel: river(80),
    surface: { lush: 0.4 },
    buildingDensity: 0.3,
    treeDensity: 0.85,
    trees: PL.forestEdge,
    groups: [G.riverHuts],
    floatDensity: 0.15,
  },
  RIVER_PORT,
];

/** A stretch of rainforest along the winding river. */
const forest = (
  name: string,
  seconds: number,
  [base, amplitude, halfWidth]: readonly number[],
  extra: Partial<TerrainSection>,
): TerrainSection => ({
  name,
  seconds,
  relief: smooth(base ?? 14, amplitude ?? 10, 420),
  channel: river(halfWidth ?? 55, 30),
  buildingDensity: 0.3,
  treeDensity: 1,
  trees: PL.rainforest,
  groups: [G.villages],
  floatDensity: 0.05,
  ...extra,
});

/** The steep jungle hills where 3-2 ends and 3-3 begins. */
export const JUNGLE_HILLS = smooth(24, 22, 420);

/** 3-2, Rainforest: from 3-1's river port, a winding river through the canopy, into the hills. */
const RAINFOREST: readonly TerrainSection[] = [
  { ...RIVER_PORT, seconds: 40, groups: [G.riverPort, G.villages] },
  forest('rainforest river', 60, [14, 10, 55], {}),
  forest('logging clearings', 50, [12, 6, 50], {
    relief: smooth(12, 6, 500),
    surface: { lush: 0.45 },
    buildingDensity: 0.4,
    treeDensity: 0.6,
    trees: PL.clearing,
    groups: [G.logging, G.villages],
  }),
  forest('deep rainforest', 60, [18, 14, 45], { buildingDensity: 0.3 }),
  forest('jungle road', 45, [14, 8, 45], { buildingDensity: 0.4, groups: [G.villages, G.logging] }),
  forest('jungle hills', 45, [0, 0, 40], {
    relief: JUNGLE_HILLS,
    trees: PL.hills,
    buildingDensity: 0.3,
  }),
];

/** 3-1 (P09-R03): the sea, the delta, then the great river into the first rainforest. */
export const LEVEL_3_1: SceneryLevel = {
  id: 'world-3-1',
  name: '3-1 River delta',
  seed: 3101,
  scrollSpeed: 70,
  transition: 420,
  sections: RIVER_DELTA,
  sea: { level: 0 },
  roads: { ...WORLD_3_ROADS, mainRoads: 1 },
  props: WORLD_3_PROPS,
};

/** 3-2 (P09-R03): starts on 3-1's river port; the river winds along the whole level. */
export const LEVEL_3_2: SceneryLevel = {
  id: 'world-3-2',
  name: '3-2 Rainforest',
  seed: 3201,
  scrollSpeed: 60,
  transition: 420,
  sections: RAINFOREST,
  sea: { level: 0 },
  roads: WORLD_3_ROADS,
  props: WORLD_3_PROPS,
};
