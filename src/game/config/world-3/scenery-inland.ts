import type {
  Landmark,
  Lakes,
  PropLine,
  Relief,
  SceneryLevel,
  TerrainSection,
} from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import {
  JUNGLE_PLANTS as PL,
  WORLD_3_GROUPS as G,
  WORLD_3_PROP_IDS as W,
  WORLD_3_PROPS,
  WORLD_3_ROADS,
} from './props';
import { GREAT_RIVER, JUNGLE_HILLS, river } from './scenery-river';

/*
 * The inland levels of World 3 (P09-R03): 3-3, steep jungle hills and cliffs broken by temple
 * ruins, the river narrowing with waterfalls; 3-4, a dark swamp with bio-labs and pipelines, then
 * a big lake held by a giant dam; 3-5, rainforest, tree-top outposts, towers linked by sky
 * bridges and a dense city centre with trees on the roofs. No sea: the rivers, swamps, lakes and
 * pools hold water at the water level (0). Each level's `seconds` add up to 300 (P09-R02).
 */

/** Steep jungle cliffs: sharp crests over the river gorge. */
const CLIFFS: Relief = {
  base: 30,
  amplitude: 70,
  frequency: 1 / 400,
  octaves: 5,
  style: 'ridged',
  maxHeight: 130,
};

/** The band of old paved ground the temples stand on, beside the river. */
const TEMPLE_PATH = { x: -90, amplitude: 60, wavelength: 1900 } as const;
const TEMPLE_GROUND = { path: TEMPLE_PATH, halfWidth: 125, edge: 70, height: 22, roughness: 2 };

const ruins = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: CLIFFS,
  channel: river(28, 22),
  surface: { paved: 0.3, lush: 0.3 },
  buildingDensity: 0.45,
  treeDensity: 0.85,
  trees: PL.hills,
  groups: [G.ruins, G.outposts],
  ...extra,
});

/** The swamp where 3-3 ends and 3-4 begins: low ground around the water level. */
const SWAMP = smooth(1.5, 4, 320);

const swamp = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: SWAMP,
  surface: { lush: 0.4, sandy: 0.2 },
  buildingDensity: 0.3,
  treeDensity: 0.6,
  trees: PL.swamp,
  groups: [G.swampLabs],
  floatDensity: 0.5,
  ...extra,
});

/** 3-3, Lost temples: from 3-2's hills into the gorge, the temples, the falls, then the swamp. */
const TEMPLES: readonly TerrainSection[] = [
  {
    name: 'jungle hills',
    seconds: 40,
    relief: JUNGLE_HILLS,
    channel: river(40, 30),
    buildingDensity: 0.5,
    treeDensity: 1,
    trees: PL.hills,
    groups: [G.villages, G.outposts],
    floatDensity: 0.05,
  },
  ruins('river gorge', 50, { flatten: TEMPLE_GROUND, buildingDensity: 0.5, groups: [G.outposts] }),
  ruins('temple valley', 60, { flatten: TEMPLE_GROUND, buildingDensity: 0.7 }),
  ruins('sacred plateau', 50, {
    flatten: { ...TEMPLE_GROUND, halfWidth: 170, edge: 80 },
    surface: { paved: 0.45, lush: 0.25 },
    buildingDensity: 0.8,
  }),
  ruins('cliff falls', 50, { flatten: TEMPLE_GROUND, buildingDensity: 0.5, groups: [G.outposts] }),
  swamp('swamp edge', 50, { groups: [G.outposts, G.swampLabs], buildingDensity: 0.45 }),
];

/** The big lake of 3-4, held by the dam, between wooded hills. */
const LAKE_HILLS = smooth(26, 20, 460);
const LAKE_PATH = { x: 0, amplitude: 40, wavelength: 3000 } as const;

/** 3-4, Swamp works: swamp, bio-labs and pumping stations, then the lake and the dam. */
const SWAMP_WORKS: readonly TerrainSection[] = [
  swamp('swamp edge', 45, { groups: [G.outposts, G.swampLabs], buildingDensity: 0.2 }),
  swamp('reed marsh', 55, { relief: smooth(0.8, 4, 260), floatDensity: 0.65 }),
  swamp('bio-lab stilts', 55, { buildingDensity: 0.5, floatDensity: 0.4 }),
  swamp('pumping works', 50, {
    relief: smooth(3, 5, 360),
    buildingDensity: 0.65,
    floatDensity: 0.3,
    surface: { lush: 0.3, paved: 0.2 },
  }),
  {
    name: 'lake hills',
    seconds: 50,
    relief: LAKE_HILLS,
    channel: { path: LAKE_PATH, halfWidth: 150, wall: 70, floor: -12 },
    buildingDensity: 0.35,
    treeDensity: 0.85,
    trees: PL.hills,
    groups: [G.swampLabs, G.villages],
    floatDensity: 0.05,
  },
  {
    name: 'dam lake',
    seconds: 45,
    relief: LAKE_HILLS,
    channel: { path: LAKE_PATH, halfWidth: 150, wall: 70, floor: -12 },
    buildingDensity: 0.3,
    treeDensity: 0.85,
    trees: PL.hills,
    groups: [G.swampLabs],
  },
];

/** Pools of water between the towers of 3-5. */
const POOLS: Lakes = { spacing: 240, chance: 0.45, radius: [26, 55], level: -5, edge: 18 };
/** Streets of the canopy city: wide blocks at its edge, a dense maze at its centre. */
const TOWER_STREETS = { rows: [60, 110], columns: [70, 130], links: 0.55 } as const;
const CENTRE_STREETS = { rows: [45, 90], columns: [50, 110], links: 0.6 } as const;

/** 3-5, Canopy city: below the dam, tree-top outposts, sky bridges, then the city centre. */
const CANOPY_CITY: readonly TerrainSection[] = [
  {
    name: 'below the dam',
    seconds: 45,
    relief: LAKE_HILLS,
    channel: river(50, 40),
    buildingDensity: 0.2,
    treeDensity: 1,
    trees: PL.rainforest,
    groups: [G.treetop],
    floatDensity: 0.05,
  },
  {
    name: 'treetop outposts',
    seconds: 55,
    relief: smooth(16, 10, 420),
    channel: river(45, 30),
    lakes: POOLS,
    buildingDensity: 0.45,
    treeDensity: 1,
    trees: PL.rainforest,
    groups: [G.treetop],
  },
  {
    name: 'sky bridges',
    seconds: 60,
    relief: smooth(12, 6, 520),
    channel: river(40, 30),
    lakes: POOLS,
    buildingDensity: 0.65,
    treeDensity: 0.8,
    trees: PL.rainforest,
    groups: [G.canopyCity, G.treetop],
  },
  {
    name: 'tower district',
    seconds: 60,
    relief: smooth(10, 4, 600, 3),
    lakes: POOLS,
    buildingDensity: 1,
    treeDensity: 0.55,
    surface: { paved: 0.3, lush: 0.3 },
    streets: TOWER_STREETS,
    trees: PL.town,
    groups: [G.canopyCity],
  },
  {
    name: 'city centre',
    seconds: 80,
    relief: smooth(10, 2, 600, 2),
    lakes: POOLS,
    buildingDensity: 1,
    treeDensity: 0.35,
    surface: { paved: 0.7, lush: 0.2 },
    streets: CENTRE_STREETS,
    trees: PL.town,
    groups: [G.canopyCentre],
    blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
  },
];

/** Seconds of each level's sections before `name` starts, at `speed`: a distance along it. */
function distanceTo(sections: readonly TerrainSection[], name: string, speed: number): number {
  const index = sections.findIndex((s) => s.name === name);
  return sections.slice(0, Math.max(0, index)).reduce((sum, s) => sum + s.seconds, 0) * speed;
}

const TEMPLE_SPEED = 55;
const SWAMP_SPEED = 60;

/**
 * The set pieces of 3-3: waterfalls where the river drops over the cliffs, and the great
 * pyramid the Stone Idol stops over (the ground stops at the mini boss, half way).
 */
const TEMPLE_LANDMARKS: readonly Landmark[] = [
  ...[10, 32].map((s) => distanceTo(TEMPLES, 'river gorge', TEMPLE_SPEED) + s * TEMPLE_SPEED),
  ...[12, 34].map((s) => distanceTo(TEMPLES, 'cliff falls', TEMPLE_SPEED) + s * TEMPLE_SPEED),
].map((z) => ({ kind: W.waterfall, z, path: GREAT_RIVER, footprint: [44, 19], onWater: true }));

const GREAT_PYRAMID: Landmark = {
  kind: W.stepPyramid,
  z: 150 * TEMPLE_SPEED + 320,
  path: TEMPLE_PATH,
  scale: 1.1,
  footprint: 26,
};

/** The stone causeway of 3-3, along the band of old paving the temples stand on. */
const CAUSEWAY: PropLine = {
  kind: W.causeway,
  path: TEMPLE_PATH,
  spacing: 15,
  footprint: 8,
  maxSlope: 0.3,
  sections: ['river gorge', 'temple valley', 'sacred plateau', 'cliff falls'],
};

/** The giant dam across the end of 3-4's lake, its power plant on the bank beside it. */
const DAM_Z = distanceTo(SWAMP_WORKS, 'dam lake', SWAMP_SPEED) + 38 * SWAMP_SPEED;
const DAM: readonly Landmark[] = [
  { kind: W.dam, z: DAM_Z, path: LAKE_PATH, footprint: [235, 19], onWater: true },
  { kind: W.powerPlant, z: DAM_Z - 60, x: 205, footprint: 20 },
];

/** The pipelines on stilts across the swamp of 3-4. */
const SWAMP_PIPELINES: readonly PropLine[] = [
  { x: -120, amplitude: 60, wavelength: 2600 },
  { x: 150, amplitude: 50, wavelength: 3100 },
].map((path) => ({
  kind: W.swampPipeline,
  path,
  spacing: 15,
  footprint: 8,
  maxSlope: 0.6,
  sections: ['reed marsh', 'bio-lab stilts', 'pumping works'],
  overWater: true,
}));

const level = (
  [id, name, seed]: readonly [string, string, number],
  scrollSpeed: number,
  sections: readonly TerrainSection[],
  props = WORLD_3_PROPS,
) =>
  ({
    id,
    name,
    seed,
    scrollSpeed,
    transition: 420,
    sections,
    sea: { level: 0 },
    roads: WORLD_3_ROADS,
    props,
  }) satisfies SceneryLevel;

/** 3-3 (P09-R03): the lost temples, slower in the storm. */
export const LEVEL_3_3: SceneryLevel = level(
  ['world-3-3', '3-3 Lost temples', 3301],
  TEMPLE_SPEED,
  TEMPLES,
  { ...WORLD_3_PROPS, lines: [CAUSEWAY], landmarks: [...TEMPLE_LANDMARKS, GREAT_PYRAMID] },
);
/** 3-4 (P09-R03): the swamp works and the dam. */
export const LEVEL_3_4: SceneryLevel = level(
  ['world-3-4', '3-4 Swamp works', 3401],
  SWAMP_SPEED,
  SWAMP_WORKS,
  { ...WORLD_3_PROPS, lines: SWAMP_PIPELINES, landmarks: DAM },
);
/** 3-5 (P09-R03): the canopy city. */
export const LEVEL_3_5: SceneryLevel = level(
  ['world-3-5', '3-5 Canopy city', 3501],
  60,
  CANOPY_CITY,
);
