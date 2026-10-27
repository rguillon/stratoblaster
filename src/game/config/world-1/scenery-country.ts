import type { SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { PLANTS, WORLD_1_GROUPS as G, WORLD_1_PROPS, WORLD_1_ROADS } from './props';
import { FARMLAND, smooth } from './scenery-coast';

/*
 * 1-3, the green country of World 1 (P06-R05, reviewer, 2026-10-26): from the farmland 1-2
 * ended on, through woods, green hills and a market town, to where the grass turns dry and
 * yellow. No sea. Its `seconds` add up to 240 (P06-R04).
 */

/** Streets of a market town: wide blocks, few crossings. */
export const TOWN_STREETS = { rows: [60, 110], columns: [70, 130], links: 0.55 } as const;

/** Dry grassland, where 1-3 ends and 1-4 begins: a little grass left on the dry earth. */
export const DRY_GRASSLAND: TerrainSection = {
  name: 'dry grassland',
  seconds: 30,
  relief: smooth(28, 10, 560),
  buildingDensity: 0.75,
  treeDensity: 0.5,
  surface: { lush: 0.2 },
  trees: PLANTS.dryGrass,
  groups: [G.villages, G.outposts],
};

const COUNTRY: readonly TerrainSection[] = [
  { ...FARMLAND, seconds: 30 },
  {
    ...FARMLAND,
    name: 'woods',
    seconds: 35,
    relief: smooth(34, 18, 460, 5),
    buildingDensity: 0.4,
    treeDensity: 0.65,
    trees: PLANTS.woods,
    groups: [G.farms],
  },
  {
    ...FARMLAND,
    name: 'green hills',
    seconds: 35,
    relief: smooth(46, 36, 420, 5),
    buildingDensity: 0.5,
    treeDensity: 0.5,
    trees: PLANTS.woods,
    groups: [G.villages],
  },
  { ...FARMLAND, seconds: 50, buildingDensity: 0.75 },
  {
    ...FARMLAND,
    name: 'market town',
    seconds: 30,
    relief: smooth(28, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.45,
    surface: { lush: 0.65, paved: 0.3 },
    streets: TOWN_STREETS,
    groups: [G.villages],
  },
  {
    ...DRY_GRASSLAND,
    name: 'yellowing grass',
    surface: { lush: 0.5 },
    buildingDensity: 0.7,
    groups: [G.villages, G.farms],
  },
  DRY_GRASSLAND,
];

/** 1-3 (P06-R05): the green country, starting on the farmland 1-2 ended on. */
export const LEVEL_1_3: SceneryLevel = {
  id: 'world-1-3',
  name: '1-3 Green country',
  seed: 1301,
  scrollSpeed: 60,
  transition: 420,
  sections: COUNTRY,
  roads: WORLD_1_ROADS,
  props: WORLD_1_PROPS,
};
