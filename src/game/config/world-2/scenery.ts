import type { Dunes, SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import { DESERT_PLANTS as PL, WORLD_2_GROUPS as G, WORLD_2_PROPS, WORLD_2_ROADS } from './props';

/*
 * World 2, the Industrial Desert (P08-R03; reworked at the reviewer's request, 2026-10-27): the
 * five levels are one journey from the deep desert, where World 1 ended, to dense factories.
 * The changes are slow: the sand gives way to concrete in small steps, the sections blend over a
 * long stretch (`TRANSITION`), and each new building group first comes in mixed with the one
 * before it. Each level starts on the very section the previous one ended on. No sea. Each
 * level's `seconds` add up to 300 (P08-R02).
 */

/** Sections blend over this many units: about 15 s of scrolling, World 1's 420 doubled. */
export const TRANSITION = 900;

/** Sand dunes: crests every `wavelength`, `height` high. */
const dunes = (height: number, wavelength: number, angleDeg = 60): Dunes => ({
  height,
  wavelength,
  angleDeg,
  warp: 0.6,
});

/** Flat ground for towns and plants. */
const FLAT = smooth(30, 4, 600, 3);
/** A dense maze of straight streets, as in World 1's towns and Level Zero's industrial zone. */
const STREETS = { rows: [45, 90], columns: [50, 110], links: 0.6 } as const;
/** Wider blocks of the mining and company towns, and of the suburbs. */
const SUBURB_STREETS = { rows: [60, 110], columns: [70, 130], links: 0.55 } as const;

const section = (
  name: string,
  seconds: number,
  extra: Partial<TerrainSection>,
): TerrainSection => ({
  name,
  seconds,
  relief: smooth(28, 10, 520),
  buildingDensity: 0.6,
  treeDensity: 0.35,
  surface: { sandy: 1 },
  trees: PL.desert,
  groups: [G.outposts],
  ...extra,
});

/** The first mines, where 2-1 ends and 2-2 begins. */
const PROSPECT_MINES = section('prospect mines', 30, {
  relief: smooth(30, 10, 520, 3),
  buildingDensity: 1,
  surface: { sandy: 0.8, paved: 0.05 },
  trees: PL.rock,
  groups: [G.outposts, G.mines],
});

/** The first oil wells among the last mines, where 2-2 ends and 2-3 begins. */
const OIL_EDGE = section('oil edge', 35, {
  relief: smooth(28, 5, 600, 3),
  buildingDensity: 1,
  treeDensity: 0.25,
  surface: { sandy: 0.55, paved: 0.25 },
  groups: [G.oil, G.mines],
});

/** Refineries giving way to the first factories, where 2-3 ends and 2-4 begins. */
const INDUSTRIAL_EDGE = section('industrial edge', 45, {
  relief: FLAT,
  buildingDensity: 1,
  treeDensity: 0.15,
  surface: { sandy: 0.25, paved: 0.55 },
  streets: STREETS,
  trees: PL.industry,
  groups: [G.refinery, G.industrial],
});

/** The factory district, where 2-4 ends and 2-5 begins. */
const FACTORY_DISTRICT = section('factory district', 55, {
  relief: smooth(32, 3, 600, 3),
  buildingDensity: 1,
  treeDensity: 0.08,
  surface: { sandy: 0.1, paved: 0.78 },
  streets: STREETS,
  trees: PL.industry,
  groups: [G.heavyIndustry, G.industrial],
});

/**
 * 2-1, Sand sea: from an oasis on the sand World 1 ended on, across great dunes and a sea of
 * sand, caravan posts and rocky desert, to the first mines in the last 30 s.
 */
const SAND_SEA: readonly TerrainSection[] = [
  section('oasis edge', 40, {
    relief: FLAT,
    buildingDensity: 0.3,
    treeDensity: 0.35,
    surface: { sandy: 0.85, lush: 0.1 },
    trees: PL.oasis,
    groups: [G.desertHomes, G.outposts],
  }),
  section('great dunes', 50, { dunes: dunes(60, 300), buildingDensity: 0.3, treeDensity: 0.2 }),
  section('caravan posts', 45, { groups: [G.outposts, G.desertHomes] }),
  section('sand sea', 45, { dunes: dunes(45, 240, 70), buildingDensity: 0.45, treeDensity: 0.2 }),
  section('rocky desert', 50, {
    relief: {
      base: 22,
      amplitude: 80,
      frequency: 1 / 500,
      octaves: 5,
      style: 'ridged',
      maxHeight: 110,
    },
    buildingDensity: 0.8,
    surface: { sandy: 0.7 },
    trees: PL.rock,
  }),
  section('desert outposts', 40, {
    relief: smooth(30, 8, 560, 3),
    buildingDensity: 1,
    surface: { sandy: 0.85 },
    groups: [G.outposts, G.desertHomes],
  }),
  PROSPECT_MINES,
];

/**
 * 2-2, Mining mesas: the mines spread over mesas and along a canyon, a mining town with
 * streets, open pits, then the first oil wells among the mines.
 */
const MINING_MESAS: readonly TerrainSection[] = [
  { ...PROSPECT_MINES, seconds: 40 },
  section('mesa mines', 50, {
    relief: {
      base: 30,
      amplitude: 150,
      frequency: 1 / 560,
      octaves: 5,
      style: 'smooth',
      maxHeight: 100,
    },
    buildingDensity: 0.9,
    surface: { sandy: 0.75, paved: 0.05 },
    trees: PL.rock,
    groups: [G.mines, G.outposts],
  }),
  section('canyon', 35, {
    relief: smooth(95, 22, 380, 5),
    channel: {
      path: { x: 0, amplitude: 140, wavelength: 1900 },
      halfWidth: 40,
      wall: 110,
      floor: 10,
    },
    buildingDensity: 0.8,
    surface: { sandy: 0.7, paved: 0.05 },
    trees: PL.rock,
    groups: [G.mines],
  }),
  section('mining town', 55, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.45,
    surface: { sandy: 0.6, paved: 0.2 },
    streets: SUBURB_STREETS,
    trees: PL.town,
    groups: [G.workerHomes, G.mines],
  }),
  section('open pits', 45, {
    relief: smooth(26, 12, 480, 4),
    buildingDensity: 1,
    surface: { sandy: 0.65, paved: 0.15 },
    trees: PL.rock,
    groups: [G.mines, G.outposts],
  }),
  section('first wells', 40, {
    relief: smooth(28, 6, 560, 3),
    buildingDensity: 1,
    treeDensity: 0.3,
    surface: { sandy: 0.6, paved: 0.2 },
    groups: [G.mines, G.oil],
  }),
  OIL_EDGE,
];

/**
 * 2-3, Oil fields: pumpjacks and tanks, a company town, refineries and tank farms, the first
 * factories at the end.
 */
const OIL_FIELDS: readonly TerrainSection[] = [
  { ...OIL_EDGE, seconds: 40 },
  section('oil fields', 60, {
    relief: smooth(26, 5, 620, 3),
    buildingDensity: 1,
    treeDensity: 0.25,
    surface: { sandy: 0.5, paved: 0.25 },
    groups: [G.oil],
  }),
  section('company town', 50, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.35,
    surface: { sandy: 0.4, paved: 0.4 },
    streets: SUBURB_STREETS,
    trees: PL.town,
    groups: [G.workerHomes, G.oil],
  }),
  section('refineries', 55, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.2,
    surface: { sandy: 0.35, paved: 0.45 },
    trees: PL.industry,
    groups: [G.refinery, G.oil],
  }),
  section('tank farms', 50, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.15,
    surface: { sandy: 0.3, paved: 0.5 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.refinery],
  }),
  INDUSTRIAL_EDGE,
];

/**
 * 2-4, Industrial belt: workers' suburbs, warehouses and yards, a power plant, factory yards,
 * then the factory district.
 */
const INDUSTRIAL_BELT: readonly TerrainSection[] = [
  { ...INDUSTRIAL_EDGE, seconds: 40 },
  section("workers' suburbs", 50, {
    relief: FLAT,
    buildingDensity: 0.6,
    treeDensity: 0.3,
    surface: { sandy: 0.22, paved: 0.6 },
    streets: SUBURB_STREETS,
    trees: PL.town,
    groups: [G.workerHomes, G.industrial],
  }),
  section('warehouses', 55, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.12,
    surface: { sandy: 0.18, paved: 0.65 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.industrial],
  }),
  section('power plant', 45, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.12,
    surface: { sandy: 0.15, paved: 0.68 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.industrial, G.refinery],
  }),
  section('factory yards', 55, {
    relief: FLAT,
    buildingDensity: 1,
    treeDensity: 0.1,
    surface: { sandy: 0.12, paved: 0.72 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.industrial, G.heavyIndustry],
  }),
  FACTORY_DISTRICT,
];

/**
 * 2-5, Factory district: foundries, rail yards, heavy industry, then great works filling every
 * block to the end.
 */
const FACTORIES: readonly TerrainSection[] = [
  { ...FACTORY_DISTRICT, seconds: 40 },
  section('foundries', 60, {
    relief: smooth(32, 3, 600, 3),
    buildingDensity: 0.8,
    treeDensity: 0.06,
    surface: { sandy: 0.08, paved: 0.82 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.heavyIndustry, G.industrial],
  }),
  section('rail yards', 50, {
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 0.85,
    treeDensity: 0.05,
    surface: { sandy: 0.06, paved: 0.86 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.industrial],
  }),
  section('heavy industry', 70, {
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 1,
    treeDensity: 0.04,
    surface: { sandy: 0.04, paved: 0.92 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.heavyIndustry],
  }),
  section('great works', 80, {
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 1,
    treeDensity: 0.02,
    surface: { paved: 1 },
    streets: STREETS,
    trees: PL.industry,
    groups: [G.heavyIndustry],
    // Every part of every block gets a plant or works, side by side, as in Level Zero's city.
    blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
  }),
];

const level = (
  [id, name, seed]: readonly [string, string, number],
  scrollSpeed: number,
  sections: readonly TerrainSection[],
) =>
  ({
    id,
    name,
    seed,
    scrollSpeed,
    transition: TRANSITION,
    sections,
    roads: WORLD_2_ROADS,
    props: WORLD_2_PROPS,
  }) satisfies SceneryLevel;

/** 2-1 (P08-R03): the sand sea, from an oasis to the first mines. */
export const LEVEL_2_1: SceneryLevel = level(['world-2-1', '2-1 Sand sea', 2101], 70, SAND_SEA);
/** 2-2: the mining mesas, starting on the mines 2-1 ended on. */
export const LEVEL_2_2: SceneryLevel = level(
  ['world-2-2', '2-2 Mining mesas', 2201],
  65,
  MINING_MESAS,
);
/** 2-3: the oil fields, starting on the first wells 2-2 ended on. */
export const LEVEL_2_3: SceneryLevel = level(['world-2-3', '2-3 Oil fields', 2301], 60, OIL_FIELDS);
/** 2-4: the industrial belt, starting on the refineries' edge 2-3 ended on. */
export const LEVEL_2_4: SceneryLevel = level(
  ['world-2-4', '2-4 Industrial belt', 2401],
  55,
  INDUSTRIAL_BELT,
);
/** 2-5: the factory district, starting on the factories 2-4 ended on. */
export const LEVEL_2_5: SceneryLevel = level(
  ['world-2-5', '2-5 Factory district', 2501],
  60,
  FACTORIES,
);
