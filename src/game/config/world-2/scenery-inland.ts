import type {
  Crevasses,
  Lakes,
  SceneryLevel,
  TerrainSection,
} from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import {
  POLAR_PLANTS as PL,
  TUNDRA_PIPELINE,
  WORLD_2_GROUPS as G,
  WORLD_2_PROPS,
  WORLD_2_ROADS,
} from './props';

/*
 * The inland levels of World 2 (P08-R03, R07): 2-3, a flat snowy tundra with frozen lakes and
 * research outposts along a pipeline; 2-4, a glacier with crevasses and ice cliffs, mining
 * outposts and a mining complex; 2-5, a mining town, its suburbs and a polar city. No sea. The
 * frozen lakes lie under the looks' `lowHeight`, so they get the lake ice; glacier ice is the
 * looks' `sand` cover. Each level's `seconds` add up to 300 (P08-R02).
 */

/** Frozen lakes scattered over the tundra. */
const LAKES: Lakes = { spacing: 260, chance: 0.55, radius: [38, 85], level: 2, edge: 30 };
/** Crevasses across the glacier. */
const CREVASSES: Crevasses = {
  spacing: 70,
  width: 9,
  depth: 16,
  angleDeg: 75,
  warp: 0.5,
  share: 0.45,
};

/** A dense maze of straight streets, as in World 1's districts. */
const STREETS = { rows: [45, 90], columns: [50, 110], links: 0.6 } as const;
/** Streets of the suburbs and the mining town: wider blocks. */
const SUBURB_STREETS = { rows: [60, 110], columns: [70, 130], links: 0.55 } as const;

const tundra = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: smooth(22, 8, 600, 4),
  buildingDensity: 0.25,
  treeDensity: 0.45,
  trees: PL.tundra,
  groups: [G.research],
  ...extra,
});

/** The snowy hills 2-2 ended on. */
const HILLS = smooth(26, 10, 560);

/** 2-3, Tundra: flat snow, frozen lakes, pine patches and low ridges, research outposts. */
const TUNDRA: readonly TerrainSection[] = [
  tundra('tundra edge', 45, { relief: HILLS, groups: [G.homes, G.research] }),
  tundra('frozen lakes', 60, { lakes: LAKES, buildingDensity: 0.2 }),
  tundra('research outposts', 50, { buildingDensity: 0.6 }),
  tundra('pine patches', 45, { treeDensity: 0.9, trees: PL.forest, groups: [G.research, G.homes] }),
  tundra('rock ridges', 40, {
    relief: {
      base: 18,
      amplitude: 40,
      frequency: 1 / 380,
      octaves: 4,
      style: 'ridged',
      maxHeight: 70,
    },
    buildingDensity: 0.35,
  }),
  tundra('lake settlements', 60, {
    lakes: LAKES,
    buildingDensity: 0.7,
    groups: [G.homes, G.research],
  }),
];

/** The glacier: a wide flat ice tongue between ridges of bare dark rock, crossed by crevasses. */
const glacier = (
  name: string,
  seconds: number,
  extra: Partial<TerrainSection>,
): TerrainSection => ({
  name,
  seconds,
  relief: {
    base: 60,
    amplitude: 120,
    frequency: 1 / 520,
    octaves: 5,
    style: 'ridged',
    maxHeight: 180,
  },
  flatten: {
    path: { x: 0, amplitude: 90, wavelength: 2400 },
    halfWidth: 150,
    edge: 90,
    height: 36,
    roughness: 3,
  },
  crevasses: CREVASSES,
  surface: { sandy: 0.85 },
  buildingDensity: 0.15,
  treeDensity: 0.15,
  trees: PL.glacier,
  groups: [G.mining],
  ...extra,
});

/** Flat snowy ground at the foot of the mines. */
const MINE_FIELDS = smooth(30, 6, 560, 3);

/** 2-4, Glacier: from the lakes 2-3 ended on to the glacier, its mining outposts and complex. */
const GLACIER: readonly TerrainSection[] = [
  tundra('moraine lakes', 40, { lakes: LAKES, buildingDensity: 0.5, groups: [G.homes, G.mining] }),
  glacier('glacier tongue', 50, {}),
  glacier('mining outposts', 50, { buildingDensity: 0.55 }),
  glacier('ice cliffs', 40, {
    relief: {
      base: 70,
      amplitude: 140,
      frequency: 1 / 360,
      octaves: 5,
      style: 'ridged',
      maxHeight: 190,
    },
  }),
  {
    name: 'mining complex',
    seconds: 70,
    relief: smooth(32, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { paved: 0.55 },
    streets: STREETS,
    trees: PL.glacier,
    groups: [G.heavyMining],
  },
  {
    name: 'mine fields',
    seconds: 50,
    relief: MINE_FIELDS,
    buildingDensity: 0.6,
    treeDensity: 0.3,
    trees: PL.town,
    groups: [G.mining, G.heavyMining],
  },
];

/** 2-5, Polar city: snowy land where 2-4 ended, a mining town, suburbs, a dense city centre. */
const POLAR_CITY: readonly TerrainSection[] = [
  {
    name: 'mine fields',
    seconds: 40,
    relief: MINE_FIELDS,
    buildingDensity: 0.6,
    treeDensity: 0.3,
    trees: PL.town,
    groups: [G.mining, G.homes],
  },
  {
    name: 'mining town',
    seconds: 60,
    relief: smooth(30, 4, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.3,
    surface: { paved: 0.3 },
    streets: SUBURB_STREETS,
    trees: PL.town,
    groups: [G.polarTown, G.mining],
  },
  {
    name: 'suburbs',
    seconds: 70,
    relief: smooth(30, 3, 600, 3),
    buildingDensity: 1,
    treeDensity: 0.25,
    surface: { paved: 0.45 },
    streets: SUBURB_STREETS,
    trees: PL.town,
    groups: [G.polarTown],
  },
  {
    name: 'city centre',
    seconds: 130,
    relief: smooth(32, 2, 600, 2),
    buildingDensity: 1,
    treeDensity: 0.05,
    surface: { paved: 1 },
    streets: STREETS,
    trees: [PL.town[0]],
    groups: [G.polarCity],
    blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
  },
];

const level = (
  [id, name, seed]: readonly [string, string, number],
  scrollSpeed: number,
  sections: readonly TerrainSection[],
  props = WORLD_2_PROPS,
) =>
  ({
    id,
    name,
    seed,
    scrollSpeed,
    transition: 420,
    sections,
    roads: WORLD_2_ROADS,
    props,
  }) satisfies SceneryLevel;

/** 2-3 (P08-R03): the tundra, a pipeline on stilts running along the whole level. */
export const LEVEL_2_3: SceneryLevel = level(['world-2-3', '2-3 Tundra', 2301], 60, TUNDRA, {
  ...WORLD_2_PROPS,
  lines: [TUNDRA_PIPELINE],
});
/** 2-4: the glacier, slower in the blizzard. */
export const LEVEL_2_4: SceneryLevel = level(['world-2-4', '2-4 Glacier', 2401], 55, GLACIER);
/** 2-5: the polar city. */
export const LEVEL_2_5: SceneryLevel = level(['world-2-5', '2-5 Polar city', 2501], 60, POLAR_CITY);
