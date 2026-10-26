import type {
  Landmark,
  PropLine,
  Relief,
  SceneryLevel,
  TerrainSection,
} from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import {
  pipelineLine,
  VOLCANIC_SCATTER as SC,
  WORLD_4_GROUPS as G,
  WORLD_4_PROP_IDS as W,
  WORLD_4_PROPS,
  WORLD_4_ROADS,
} from './props';

/*
 * The first two levels of World 4 (P10-R03): 4-1, a dark steaming sea between black rock
 * volcanic islands, then a black-sand coast in the last 30 s; 4-2, flat grey ash plains, dead
 * burnt forests, low cinder cones, geothermal plants and ash-covered towns along a road. Heights
 * in world units above the sea level (0); 4-2 has no sea. Each level's `seconds` add up to 300
 * (P10-R02).
 */

/** Black rock islands: sharp crests rising out of the sea bed, most of them under the sea. */
const islands = (base: number, amplitude: number): Relief => ({
  base,
  amplitude,
  frequency: 1 / 360,
  octaves: 4,
  style: 'ridged',
  maxHeight: 40,
});

/** Open water between the islands: nothing stands on it but the steam. */
const sea = (
  name: string,
  seconds: number,
  relief: Relief,
  extra: Partial<TerrainSection> = {},
): TerrainSection => ({
  name,
  seconds,
  relief,
  surface: { sandy: 0.6 },
  buildingDensity: 0.25,
  treeDensity: 0.5,
  trees: SC.islands,
  groups: [G.fishing, G.wells],
  floatDensity: 0.4,
  ...extra,
});

/** The low black-sand shore where 4-1 ends and 4-2 begins. */
export const BLACK_SANDS = smooth(10, 5, 480);

/** The coast of 4-1's last 30 s: the sea on the left of a winding line. */
const BLACK_COAST = {
  path: { x: -70, amplitude: 70, wavelength: 1800 },
  landSide: 1,
  width: 220,
  seabed: -50,
} as const;

/** 4-1, Black sands: the steaming sea and its islands, then the black-sand coast. */
const BLACK_SEA: readonly TerrainSection[] = [
  sea('steaming sea', 40, smooth(-60, 20, 520, 5), { buildingDensity: 0, treeDensity: 0 }),
  sea('black reefs', 45, islands(-46, 62), { buildingDensity: 0.1 }),
  sea('vent islands', 50, islands(-45, 70)),
  sea('deep water', 35, smooth(-60, 20, 520, 5), { buildingDensity: 0, treeDensity: 0 }),
  sea('fishing isles', 55, islands(-44, 70), { buildingDensity: 0.4 }),
  sea('island chain', 45, islands(-46, 70), { buildingDensity: 0.3, floatDensity: 0.5 }),
  {
    name: 'black-sand coast',
    seconds: 30,
    relief: BLACK_SANDS,
    shore: BLACK_COAST,
    surface: { sandy: 0.8 },
    buildingDensity: 0.5,
    treeDensity: 0.4,
    trees: SC.coast,
    groups: [G.harbour, G.fishing, G.wells],
    floatDensity: 0.5,
  },
];

/** Ash plains: flat grey ground under drifts of ash. */
const ash = (
  name: string,
  seconds: number,
  relief: Relief,
  extra: Partial<TerrainSection> = {},
): TerrainSection => ({
  name,
  seconds,
  relief,
  surface: { lush: 0.6 },
  buildingDensity: 0.2,
  treeDensity: 0.4,
  trees: SC.ashPlains,
  groups: [G.ashTowns, G.wells],
  ...extra,
});

/** Low cinder cones scattered over the plains. */
const CINDER_CONES: Relief = {
  base: 10,
  amplitude: 32,
  frequency: 1 / 300,
  octaves: 3,
  style: 'ridged',
  maxHeight: 45,
};

/** The scorched rock where 4-2 ends and 4-3 begins. */
export const SCORCHED_ROCK = smooth(14, 8, 460);

/** The flat ground of the geothermal plants, along the pipeline. */
const PLANT_PATH = { x: 120, amplitude: 50, wavelength: 2400 } as const;
const PLANT_GROUND = { path: PLANT_PATH, halfWidth: 110, edge: 60, height: 12, roughness: 1 };

/** 4-2, Ash plains: from 4-1's black sands over the ash, the dead forests and the plants. */
const ASH_PLAINS: readonly TerrainSection[] = [
  ash('black-sand flats', 40, BLACK_SANDS, { surface: { sandy: 0.5, lush: 0.2 } }),
  ash('ash plains', 55, smooth(12, 4, 600, 3), { buildingDensity: 0.25 }),
  ash('dead forest', 50, smooth(13, 6, 480), { treeDensity: 0.9, trees: SC.deadForest }),
  ash('cinder cones', 45, CINDER_CONES, { buildingDensity: 0.15, trees: SC.scorched }),
  ash('geothermal field', 60, smooth(12, 5, 520), {
    flatten: PLANT_GROUND,
    surface: { lush: 0.4, paved: 0.2 },
    buildingDensity: 0.4,
    groups: [G.powerPlants, G.ashTowns],
  }),
  ash('scorched edge', 50, SCORCHED_ROCK, {
    surface: { lush: 0.3 },
    buildingDensity: 0.3,
    trees: SC.scorched,
    groups: [G.ashTowns, G.powerPlants],
  }),
];

/** Seconds of the sections before `name` starts, at `speed`: a distance along the level. */
export function distanceTo(sections: readonly TerrainSection[], name: string, speed: number) {
  const index = sections.findIndex((s) => s.name === name);
  return sections.slice(0, Math.max(0, index)).reduce((sum, s) => sum + s.seconds, 0) * speed;
}

const ASH_SPEED = 65;

/** The pipelines of 4-2, from the geothermal plants across the plains. */
const ASH_PIPELINES: readonly PropLine[] = [
  pipelineLine(PLANT_PATH, ['geothermal field', 'scorched edge']),
  pipelineLine({ x: -150, amplitude: 60, wavelength: 2800 }, ['ash plains', 'dead forest']),
];

/** A few hot springs steaming on the plains. */
const HOT_SPRINGS: readonly Landmark[] = [
  ['ash plains', 12, -60],
  ['ash plains', 38, 170],
  ['dead forest', 30, -190],
  ['cinder cones', 20, 60],
].map(([name, seconds, x]) => ({
  kind: W.hotSpring,
  z: distanceTo(ASH_PLAINS, String(name), ASH_SPEED) + Number(seconds) * ASH_SPEED,
  x: Number(x),
  footprint: 14,
}));

/** 4-1 (P10-R03): the steaming sea and its islands, a black-sand coast at the end. */
export const LEVEL_4_1: SceneryLevel = {
  id: 'world-4-1',
  name: '4-1 Black sands',
  seed: 4101,
  scrollSpeed: 70,
  transition: 420,
  sections: BLACK_SEA,
  sea: { level: 0 },
  roads: { ...WORLD_4_ROADS, mainRoads: 1 },
  props: WORLD_4_PROPS,
};

/** 4-2 (P10-R03): starts on 4-1's black sands; no sea, no lava. */
export const LEVEL_4_2: SceneryLevel = {
  id: 'world-4-2',
  name: '4-2 Ash plains',
  seed: 4201,
  scrollSpeed: ASH_SPEED,
  transition: 420,
  sections: ASH_PLAINS,
  roads: WORLD_4_ROADS,
  props: { ...WORLD_4_PROPS, lines: ASH_PIPELINES, landmarks: HOT_SPRINGS },
};
