import type { Dunes, SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { PLANTS, WORLD_1_GROUPS as G, WORLD_1_PROPS, WORLD_1_ROADS } from './props';
import { smooth } from './scenery-coast';
import { DRY_GRASSLAND, TOWN_STREETS } from './scenery-country';

/*
 * The dry levels of World 1 (P06-R05, R06, reworked at the reviewer's request, 2026-10-26):
 * from the dry grassland 1-3 ended on to sand and rock, dunes, an oasis, a canyon and mesas
 * with their mines, then desert towns, an industrial zone and a city built on the desert. No
 * sea. Each level's `seconds` add up to 240 (P06-R04).
 */

/** Sand dunes: crests every `wavelength`, `height` high (P06-R06). */
const dunes = (height: number, wavelength: number, angleDeg = 60): Dunes => ({
  height,
  wavelength,
  angleDeg,
  warp: 0.6,
});

/** Flat-topped mesas: a high relief whose tops are squashed under `top`. */
const mesas = (top: number) =>
  ({
    base: 30,
    amplitude: 150,
    frequency: 1 / 560,
    octaves: 5,
    style: 'smooth',
    maxHeight: top,
  }) as const;

/** A dense maze of straight streets, as in Level Zero's districts. */
const STREETS = { rows: [45, 90], columns: [50, 110], links: 0.6 } as const;

const desert = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: smooth(28, 12, 520),
  buildingDensity: 0,
  treeDensity: 0.35,
  surface: { sandy: 1 },
  trees: PLANTS.desert,
  groups: [G.outposts],
  ...extra,
});

/** The flat ground around the mines, where 1-4 ends and 1-5 begins. */
const MINING_OUTSKIRTS = desert('mining outskirts', 30, {
  relief: smooth(30, 8, 560, 3),
  buildingDensity: 1,
  surface: { sandy: 0.7, paved: 0.2 },
  groups: [G.industrial, G.outposts],
});

/**
 * 1-4, Dry lands: dry grass and scrub, then sand and rock, dunes, an oasis town, a canyon, mesas
 * with their mines and a desert town. The bare stretches (rock, dunes, cliffs) are short, so the
 * props keep growing in number (P06-R05).
 */
const DRY_LANDS: readonly TerrainSection[] = [
  DRY_GRASSLAND,
  desert('scrubland villages', 40, {
    relief: smooth(30, 14, 520),
    buildingDensity: 1,
    treeDensity: 0.6,
    surface: { sandy: 0.35 },
    trees: PLANTS.dry,
    groups: [G.desertHomes, G.outposts],
  }),
  desert('sand and rock', 20, {
    relief: {
      base: 20,
      amplitude: 90,
      frequency: 1 / 520,
      octaves: 5,
      style: 'ridged',
      maxHeight: 120,
    },
    buildingDensity: 0.6,
  }),
  desert('dunes', 20, { dunes: dunes(50, 260), buildingDensity: 0.45, treeDensity: 0.2 }),
  desert('oasis town', 45, {
    buildingDensity: 1,
    treeDensity: 0.7,
    surface: { sandy: 0.75, lush: 0.25 },
    streets: TOWN_STREETS,
    trees: PLANTS.oasis,
    groups: [G.desertHomes],
  }),
  desert('canyon', 20, {
    relief: smooth(95, 22, 380, 5),
    channel: {
      path: { x: 0, amplitude: 140, wavelength: 1900 },
      halfWidth: 40,
      wall: 110,
      floor: 10,
    },
    buildingDensity: 0.5,
  }),
  desert('mesas and mines', 20, {
    relief: mesas(100),
    buildingDensity: 0.9,
    groups: [G.industrial, G.outposts],
  }),
  desert('desert town', 25, {
    relief: smooth(30, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.45,
    surface: { sandy: 0.8, paved: 0.15 },
    streets: TOWN_STREETS,
    trees: PLANTS.town,
    groups: [G.desertHomes],
  }),
  { ...MINING_OUTSKIRTS, seconds: 20 },
];

/** 1-5, Desert city: the mining outskirts, desert towns, suburbs, industry, the city centre. */
const DESERT_CITY: readonly TerrainSection[] = [
  MINING_OUTSKIRTS,
  desert('desert towns', 40, {
    relief: smooth(28, 6, 560, 3),
    buildingDensity: 1,
    treeDensity: 0.45,
    trees: PLANTS.town,
    groups: [G.desertHomes, G.outposts],
  }),
  desert('suburbs', 45, {
    relief: smooth(30, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.3,
    surface: { sandy: 0.6, paved: 0.3 },
    streets: TOWN_STREETS,
    trees: PLANTS.town,
    groups: [G.desertHomes],
  }),
  desert('industrial zone', 50, {
    relief: smooth(32, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { sandy: 0.3, paved: 0.7 },
    streets: STREETS,
    groups: [G.heavyIndustry],
  }),
  desert('city centre', 75, {
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 1,
    treeDensity: 0.1,
    surface: { paved: 1 },
    streets: STREETS,
    trees: [PLANTS.town[0]],
    groups: [G.city],
    blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
  }),
];

const level = (id: string, name: string, seed: number, sections: readonly TerrainSection[]) =>
  ({
    id,
    name,
    seed,
    scrollSpeed: 60,
    transition: 420,
    sections,
    roads: WORLD_1_ROADS,
    props: WORLD_1_PROPS,
  }) satisfies SceneryLevel;

/** 1-4 (P06-R05): the dry lands, starting on the dry grassland 1-3 ended on. */
export const LEVEL_1_4: SceneryLevel = level('world-1-4', '1-4 Dry lands', 1401, DRY_LANDS);
/** 1-5: the desert city, starting on the mining outskirts 1-4 ended on. */
export const LEVEL_1_5: SceneryLevel = level('world-1-5', '1-5 Desert city', 1501, DESERT_CITY);
