import type { SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { PLANTS, WORLD_1_GROUPS as G, WORLD_1_PROPS, WORLD_1_ROADS } from './props';

/*
 * The first two levels of World 1 (P06-R05, reworked at the reviewer's request, 2026-10-26):
 * open sea with small green islands and reefs, then a green coast that gives way to meadows,
 * groves and farmland. Heights in world units above the sea level (0). Each section's `seconds`
 * add up to 240 (P06-R04).
 */

/** Rolling relief: `base` ± `amplitude`, features about `wavelength` across. */
export const smooth = (base: number, amplitude: number, wavelength: number, octaves = 4) =>
  ({ base, amplitude, frequency: 1 / wavelength, octaves, style: 'smooth' }) as const;

/** The coast where the land starts: sea on the left (`landSide` 1) along a winding line. */
const shore = (x: number, amplitude: number, wavelength: number) =>
  ({ path: { x, amplitude, wavelength }, landSide: 1, width: 240, seabed: -55 }) as const;

/** Open water: deep sea bed, nothing stands on it but the islands, green with palms. */
const water = (name: string, seconds: number, base: number, amplitude: number): TerrainSection => ({
  name,
  seconds,
  relief: smooth(base, amplitude, 520, 5),
  buildingDensity: 0,
  treeDensity: 0.6,
  surface: { lush: 0.7 },
  trees: PLANTS.islands,
  groups: [G.fishing],
});

/** The green coast where 1-1 ends and 1-2 begins: a sandy shore, then grass. */
const GREEN_COAST: TerrainSection = {
  name: 'green coast',
  seconds: 30,
  relief: smooth(16, 10, 480),
  shore: shore(-40, 90, 1800),
  buildingDensity: 0.5,
  treeDensity: 0.55,
  surface: { lush: 0.8, sandy: 0.2 },
  trees: PLANTS.coast,
  groups: [G.fishing, G.coastHomes],
};

/** The green land: grass all over, its trees and buildings. */
const green = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: smooth(24, 10, 600),
  buildingDensity: 0.5,
  treeDensity: 0.5,
  surface: { lush: 1 },
  trees: PLANTS.meadow,
  groups: [G.villages, G.farms],
  ...extra,
});

/** Farmland, where 1-2 ends and 1-3 begins. */
export const FARMLAND = green('farmland', 45, {
  relief: smooth(26, 8, 620),
  buildingDensity: 0.6,
  groups: [G.farms, G.villages],
});

/** 1-1, Open sea: sea almost all the way, small green islands and reefs, a coast at the end. */
const OPEN_SEA: readonly TerrainSection[] = [
  water('open sea', 35, -70, 30),
  water('reefs', 40, -24, 48),
  water('islands', 45, -12, 50),
  water('deep water', 30, -70, 30),
  water('archipelago', 60, -10, 50),
  // The first coast comes in the last 30 s: a green shore with a fishing village.
  GREEN_COAST,
];

/** 1-2, Green coast: beaches and bays along a coast road, then meadows, groves and farms. */
const GREEN_COAST_LEVEL: readonly TerrainSection[] = [
  { ...GREEN_COAST, name: 'coast road', seconds: 40 },
  {
    ...GREEN_COAST,
    name: 'bays',
    seconds: 40,
    relief: smooth(22, 14, 460),
    shore: shore(-90, 170, 1500),
    buildingDensity: 0.55,
    treeDensity: 0.6,
    groups: [G.coastHomes, G.villages],
  },
  green('coast farms', 30, {
    relief: smooth(24, 14, 460),
    shore: shore(-230, 110, 1700),
    surface: { lush: 0.9, sandy: 0.1 },
    trees: PLANTS.coast,
    groups: [G.coastHomes, G.farms],
  }),
  green('meadows', 45, { buildingDensity: 0.5, treeDensity: 0.55 }),
  green('groves', 40, {
    relief: smooth(30, 16, 480),
    buildingDensity: 0.45,
    treeDensity: 0.75,
    trees: PLANTS.woods,
    groups: [G.farms],
  }),
  FARMLAND,
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

/** 1-2 (P06-R05): starts on the green coast where 1-1 ended; the sea is gone after 110 s. */
export const LEVEL_1_2: SceneryLevel = {
  id: 'world-1-2',
  name: '1-2 Green coast',
  seed: 1201,
  scrollSpeed: 65,
  transition: 420,
  sections: GREEN_COAST_LEVEL,
  sea: { level: 0 },
  roads: WORLD_1_ROADS,
  props: WORLD_1_PROPS,
};
