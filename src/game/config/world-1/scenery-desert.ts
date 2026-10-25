import type { Dunes, SceneryLevel, TerrainSection } from '../../../core/scenery/scenery-level';
import { PLANTS, WORLD_1_GROUPS as G, WORLD_1_PROPS, WORLD_1_ROADS } from './props';
import { smooth } from './scenery-coast';

/*
 * The desert levels of World 1 (P06-R05, R06): open desert with dunes, mesas and a canyon,
 * then desert towns and their industry, then a city built on the desert. No sea. Each level's
 * `seconds` add up to 240 (P06-R04).
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
/** Streets of the suburbs: wider blocks, fewer crossings. */
const SUBURB_STREETS = { rows: [60, 110], columns: [70, 130], links: 0.55 } as const;

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

/** 1-3, Desert: sand and rock where 1-2 ended, dunes, towns, mesas, a canyon, an oasis. */
const DESERT: readonly TerrainSection[] = [
  desert('sand and rock', 25, {
    relief: {
      base: 20,
      amplitude: 90,
      frequency: 1 / 520,
      octaves: 5,
      style: 'ridged',
      maxHeight: 120,
    },
    buildingDensity: 0.25,
  }),
  desert('dunes', 35, { dunes: dunes(50, 260), buildingDensity: 0.15, treeDensity: 0.15 }),
  desert('desert road towns', 40, {
    buildingDensity: 0.7,
    groups: [G.desertHomes, G.outposts],
  }),
  desert('mesas', 35, { relief: mesas(110), buildingDensity: 0.3 }),
  desert('canyon', 35, {
    relief: smooth(95, 22, 380, 5),
    channel: {
      path: { x: 0, amplitude: 140, wavelength: 1900 },
      halfWidth: 40,
      wall: 110,
      floor: 10,
    },
    buildingDensity: 0.15,
  }),
  desert('oasis town', 35, {
    buildingDensity: 0.85,
    treeDensity: 0.7,
    surface: { sandy: 0.8, lush: 0.25 },
    trees: PLANTS.oasis,
    groups: [G.desertHomes],
  }),
  desert('open dunes', 35, { dunes: dunes(50, 280, -50), treeDensity: 0.1 }),
];

/** 1-4, Desert towns: from the open desert to denser towns, then mines and an industrial zone. */
const DESERT_TOWNS: readonly TerrainSection[] = [
  desert('open dunes', 30, { dunes: dunes(50, 280, -50), treeDensity: 0.1, buildingDensity: 0.15 }),
  desert('desert towns', 45, {
    buildingDensity: 0.7,
    treeDensity: 0.4,
    trees: PLANTS.town,
    groups: [G.desertHomes, G.outposts],
  }),
  desert('mesas and mines', 35, {
    relief: mesas(100),
    buildingDensity: 0.5,
    groups: [G.industrial, G.outposts],
  }),
  desert('town', 40, {
    buildingDensity: 0.9,
    treeDensity: 0.4,
    trees: PLANTS.town,
    groups: [G.desertHomes],
  }),
  desert('mining outskirts', 40, {
    relief: smooth(30, 8, 560, 3),
    buildingDensity: 0.8,
    surface: { sandy: 0.7, paved: 0.2 },
    groups: [G.industrial, G.outposts],
  }),
  desert('industrial zone', 50, {
    relief: smooth(32, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { sandy: 0.35, paved: 0.6 },
    streets: STREETS,
    groups: [G.heavyIndustry],
  }),
];

/** 1-5, Desert city: the desert edge of the industry, suburbs, an industrial zone, the city. */
const DESERT_CITY: readonly TerrainSection[] = [
  desert('desert edge', 25, { relief: smooth(30, 8, 560, 3), buildingDensity: 0.5 }),
  desert('suburbs', 50, {
    relief: smooth(30, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.3,
    surface: { sandy: 0.6, paved: 0.3 },
    streets: SUBURB_STREETS,
    trees: PLANTS.town,
    groups: [G.desertHomes],
  }),
  desert('industrial zone', 55, {
    relief: smooth(32, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { sandy: 0.3, paved: 0.7 },
    streets: STREETS,
    groups: [G.heavyIndustry],
  }),
  desert('city centre', 110, {
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

/** 1-3 (P06-R05): open desert, starting on the sand and rock 1-2 ended on. */
export const LEVEL_1_3: SceneryLevel = level('world-1-3', '1-3 Desert', 1301, DESERT);
/** 1-4: desert towns, starting in the open desert 1-3 ended on. */
export const LEVEL_1_4: SceneryLevel = level('world-1-4', '1-4 Desert towns', 1401, DESERT_TOWNS);
/** 1-5: the desert city, starting on the desert edge of the industry 1-4 ended on. */
export const LEVEL_1_5: SceneryLevel = level('world-1-5', '1-5 Desert city', 1501, DESERT_CITY);
