import type { SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { PLANTS, WORLD_1_GROUPS as G, WORLD_1_PROPS, WORLD_1_ROADS } from './props';

/*
 * The first two levels of World 1 (P06-R05): open sea with islands and reefs, then a dry coast
 * that gives way to sand and rock. Heights in world units above the sea level (0). Each
 * section's `seconds` add up to 240 (P06-R04).
 */

/** Rolling relief: `base` ± `amplitude`, features about `wavelength` across. */
export const smooth = (base: number, amplitude: number, wavelength: number, octaves = 4) =>
  ({ base, amplitude, frequency: 1 / wavelength, octaves, style: 'smooth' }) as const;

/** The coast where the land starts: sea on the left (`landSide` 1) along a winding line. */
const shore = (x: number, amplitude: number, wavelength: number) =>
  ({ path: { x, amplitude, wavelength }, landSide: 1, width: 240, seabed: -55 }) as const;

/** Open water: deep sea bed, nothing stands on it. */
const water = (name: string, seconds: number, base: number, amplitude: number): TerrainSection => ({
  name,
  seconds,
  relief: smooth(base, amplitude, 520, 5),
  buildingDensity: 0,
  treeDensity: 0.6,
  trees: PLANTS.islands,
  groups: [G.fishing],
});

/** 1-1, Open sea: sea almost all the way, small rocky islands and reefs, a coast at the end. */
const OPEN_SEA: readonly TerrainSection[] = [
  water('open sea', 35, -70, 30),
  water('reefs', 40, -24, 48),
  water('islands', 45, -12, 50),
  water('deep water', 30, -70, 30),
  water('archipelago', 60, -10, 50),
  {
    // The first coast comes in the last 30 s: a sandy shore with dry scrub and a fishing village.
    name: 'fishing coast',
    seconds: 30,
    relief: smooth(16, 10, 480),
    shore: shore(-40, 90, 1800),
    buildingDensity: 0.5,
    treeDensity: 0.5,
    surface: { sandy: 0.6 },
    trees: PLANTS.coast,
    groups: [G.fishing, G.coastHomes],
  },
];

/** 1-2, Dry coast: bays and beaches along a coast road, then dry hills, sand and rock. */
const DRY_COAST: readonly TerrainSection[] = [
  {
    name: 'coast road',
    seconds: 40,
    relief: smooth(18, 12, 480),
    shore: shore(-40, 90, 1800),
    buildingDensity: 0.35,
    treeDensity: 0.5,
    surface: { sandy: 0.5 },
    trees: PLANTS.coast,
    groups: [G.coastHomes, G.fishing],
  },
  {
    name: 'bays',
    seconds: 40,
    relief: smooth(22, 16, 460),
    shore: shore(-90, 170, 1500),
    buildingDensity: 0.3,
    treeDensity: 0.5,
    surface: { sandy: 0.4 },
    trees: PLANTS.coast,
    groups: [G.coastHomes],
  },
  {
    name: 'beaches',
    seconds: 40,
    relief: smooth(24, 16, 460),
    shore: shore(-230, 110, 1700),
    buildingDensity: 0.3,
    treeDensity: 0.5,
    surface: { sandy: 0.5 },
    trees: PLANTS.coast,
    groups: [G.coastHomes, G.desertHomes],
  },
  {
    name: 'dry hills',
    seconds: 40,
    relief: smooth(46, 48, 420, 5),
    buildingDensity: 0.15,
    treeDensity: 0.7,
    trees: PLANTS.dry,
    groups: [G.desertHomes, G.outposts],
  },
  {
    name: 'scrubland',
    seconds: 40,
    relief: smooth(30, 14, 520),
    buildingDensity: 0.3,
    treeDensity: 0.6,
    surface: { sandy: 0.5 },
    trees: PLANTS.dry,
    groups: [G.desertHomes, G.outposts, G.industrial],
  },
  {
    name: 'sand and rock',
    seconds: 40,
    relief: {
      base: 20,
      amplitude: 90,
      frequency: 1 / 520,
      octaves: 5,
      style: 'ridged',
      maxHeight: 120,
    },
    buildingDensity: 0.1,
    treeDensity: 0.4,
    surface: { sandy: 1 },
    trees: PLANTS.desert,
    groups: [G.outposts],
  },
];

/** 1-1 (P06-R05): open sea, the first coast in the last 30 s. */
export const LEVEL_1_1: SceneryLevel = {
  id: 'world-1-1',
  name: '1-1 Open sea',
  seed: 1101,
  scrollSpeed: 70,
  transition: 420,
  sections: OPEN_SEA,
  sea: { level: 0 },
  roads: { ...WORLD_1_ROADS, mainRoads: 1 },
  props: WORLD_1_PROPS,
};

/** 1-2 (P06-R05): starts on the coast where 1-1 ended; the sea is gone after the first half. */
export const LEVEL_1_2: SceneryLevel = {
  id: 'world-1-2',
  name: '1-2 Dry coast',
  seed: 1201,
  scrollSpeed: 65,
  transition: 420,
  sections: DRY_COAST,
  sea: { level: 0 },
  roads: WORLD_1_ROADS,
  props: WORLD_1_PROPS,
};
