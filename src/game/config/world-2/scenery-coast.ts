import type { SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import { POLAR_PLANTS as PL, WORLD_2_GROUPS as G, WORLD_2_PROPS, WORLD_2_ROADS } from './props';

/*
 * The cold-sea levels of World 2 (P08-R03): 2-1, a dark sea with drifting ice floes and rocky
 * islands, a snowy coast at the end; 2-2, fjords cut into steep snowy land, the sea gone after
 * the first half. Heights in world units above the sea level (0). Each level's `seconds` add up
 * to 300 (P08-R02).
 */

/** The snowy coast where the land starts: sea on the left along a winding line. */
export const POLAR_SHORE = {
  path: { x: -40, amplitude: 90, wavelength: 1800 },
  landSide: 1,
  width: 240,
  seabed: -55,
} as const;

/** Open cold water with ice floating on it (`float` = share of cells with floes). */
const water = (name: string, seconds: number, [base, amplitude, float]: readonly number[]) =>
  ({
    name,
    seconds,
    relief: smooth(base ?? -70, amplitude ?? 30, 520, 5),
    buildingDensity: 0,
    treeDensity: 0.5,
    trees: PL.islands,
    groups: [G.coastPosts],
    floatDensity: float ?? 0,
  }) satisfies TerrainSection;

/** 2-1, Ice floes: almost all sea, floes and icebergs, small snowy rock islands, then a coast. */
const ICE_FLOES: readonly TerrainSection[] = [
  water('cold sea', 45, [-70, 30, 0.3]),
  water('ice floes', 50, [-62, 28, 0.6]),
  water('rock islets', 55, [-14, 48, 0.25]),
  water('iceberg field', 45, [-70, 30, 0.45]),
  water('snowy archipelago', 75, [-10, 50, 0.2]),
  {
    // The first snowy coast comes in the last 30 s, with a small harbour.
    name: 'harbour coast',
    seconds: 30,
    relief: smooth(18, 10, 480),
    shore: POLAR_SHORE,
    buildingDensity: 0.5,
    treeDensity: 0.4,
    trees: PL.coast,
    groups: [G.harbour, G.fishing, G.coastPosts],
    floatDensity: 0.2,
  },
];

/**
 * A fjord: steep snowy cliffs (`cliff` high) cut by a winding arm of the sea `floor` deep, with
 * flat shelves along its shores for the villages and the coast road.
 */
function fjord(name: string, seconds: number, cliff: number, floor: number): TerrainSection {
  const path = { x: -30, amplitude: 120, wavelength: 1700 };
  return {
    name,
    seconds,
    relief: {
      base: cliff,
      amplitude: 70,
      frequency: 1 / 420,
      octaves: 5,
      style: 'ridged',
      maxHeight: 200,
    },
    flatten: { path, halfWidth: 95, edge: 70, height: 14, roughness: 3 },
    channel: { path, halfWidth: 42, wall: 28, floor },
    buildingDensity: 0.45,
    treeDensity: 0.6,
    trees: PL.forest,
    groups: [G.fishing, G.homes],
    floatDensity: 0.12,
  };
}

/** 2-2, Fjords: from the harbour coast 2-1 ended on into the fjords, then pine valleys and hills. */
const FJORDS: readonly TerrainSection[] = [
  {
    name: 'harbour coast',
    seconds: 40,
    relief: smooth(18, 10, 480),
    shore: POLAR_SHORE,
    buildingDensity: 0.5,
    treeDensity: 0.4,
    trees: PL.coast,
    groups: [G.harbour, G.fishing],
    floatDensity: 0.15,
  },
  fjord('fjord mouth', 45, 60, -40),
  fjord('fjords', 50, 75, -35),
  fjord('fjord head', 20, 80, -20),
  {
    name: 'pine valleys',
    seconds: 50,
    relief: {
      base: 40,
      amplitude: 90,
      frequency: 1 / 480,
      octaves: 5,
      style: 'ridged',
      maxHeight: 160,
    },
    flatten: {
      path: { x: 40, amplitude: 110, wavelength: 1900 },
      halfWidth: 80,
      edge: 80,
      height: 22,
      roughness: 4,
    },
    buildingDensity: 0.4,
    treeDensity: 0.9,
    trees: PL.forest,
    groups: [G.homes],
  },
  {
    name: 'snowy hills',
    seconds: 50,
    relief: smooth(44, 40, 460, 5),
    buildingDensity: 0.35,
    treeDensity: 0.6,
    trees: PL.forest,
    groups: [G.homes, G.research],
  },
  {
    name: 'inland hamlets',
    seconds: 45,
    relief: smooth(26, 10, 560),
    buildingDensity: 0.6,
    treeDensity: 0.5,
    trees: PL.tundra,
    groups: [G.homes],
  },
];

/** 2-1 (P08-R03): the cold sea, the first snowy coast in the last 30 s. */
export const LEVEL_2_1: SceneryLevel = {
  id: 'world-2-1',
  name: '2-1 Ice floes',
  seed: 2101,
  scrollSpeed: 70,
  transition: 420,
  sections: ICE_FLOES,
  sea: { level: 0 },
  roads: { ...WORLD_2_ROADS, mainRoads: 1 },
  props: WORLD_2_PROPS,
};

/** 2-2 (P08-R03): starts on the coast where 2-1 ended; the sea is gone after the first half. */
export const LEVEL_2_2: SceneryLevel = {
  id: 'world-2-2',
  name: '2-2 Fjords',
  seed: 2201,
  scrollSpeed: 65,
  transition: 420,
  sections: FJORDS,
  sea: { level: 0 },
  roads: WORLD_2_ROADS,
  props: WORLD_2_PROPS,
};
