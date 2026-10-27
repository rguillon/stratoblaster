import type { PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import { INDUSTRIAL_VARIANTS, familyRules, type PartFamily } from '../building-families';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../level-zero';
import { WORLD_1_PROP_IDS, WORLD_1_ROADS } from '../world-1/props';

/**
 * Ids of the props added for World 2 (P08-R07). The frozen ones were made for the first World 2,
 * the Frozen North; since the reviewer's rework (2026-10-27) no level places them, only the
 * oil pumpjack.
 */
export const WORLD_2_PROP_IDS = {
  /** The oil fields of 2-2 and 2-3 (reviewer, 2026-10-27). */
  pumpjack: 'oil-pumpjack',
  // Plants.
  snowPine: 'snow-pine',
  frostedTree: 'frosted-tree',
  snowyBush: 'snowy-bush',
  // Homes.
  chalet: 'polar-chalet',
  longChalet: 'long-chalet',
  hut: 'ice-hut',
  heatedDome: 'heated-dome',
  // The coast and the harbours.
  lighthouse: 'lighthouse',
  harbourCrane: 'harbour-crane',
  fishStore: 'fish-store',
  // Research outposts and the tundra.
  radarDome: 'radar-dome',
  antennaArray: 'antenna-array',
  windTurbine: 'wind-turbine',
  pipeline: 'pipeline',
  // Mining.
  drillTower: 'drill-tower',
  conveyor: 'conveyor',
  oreSilo: 'ore-silo',
  miningCrane: 'mining-crane',
  // On the sea.
  floeSmall: 'ice-floe-small',
  floeLarge: 'ice-floe-large',
  iceberg: 'iceberg',
  weatherBuoy: 'weather-buoy',
} as const;

const P = PROP_IDS;
const W = WORLD_2_PROP_IDS;
const W1 = WORLD_1_PROP_IDS;

/** Building groups of World 2; each section lists the ones that stand on it. */
export const WORLD_2_GROUPS = {
  /** Oasis and desert homes: World 1's flat-roofed homes and wind catchers. */
  desertHomes: 'w2-desert-homes',
  /** Caravan and desert outposts: water towers, solar farms, antennas, radars. */
  outposts: 'w2-outposts',
  /** Mines: headframes, their tanks and sheds. */
  mines: 'w2-mines',
  /** Mining and company towns: homes of the workers between mine and oil buildings. */
  workerHomes: 'w2-worker-homes',
  /** Oil fields: pumpjacks and storage tanks. */
  oil: 'w2-oil',
  /** Refineries and tank farms. */
  refinery: 'w2-refinery',
  /** The industrial belt: factories, warehouses, yards, cooling towers. */
  industrial: 'w2-industrial',
  /** Dense heavy industry: large plants and works made of parts. */
  heavyIndustry: 'w2-heavy-industry',
} as const;

const G = WORLD_2_GROUPS;

/** Props are drawn small next to the ships, as in World 1. */
const BUILDING_SCALE = [0.5, 0.65] as const;
const TREE_SCALE = [0.45, 0.75] as const;

/** The variants of `family`, sharing `weight` between them (not `weight` each). */
const variants = (family: PartFamily, weight: number) =>
  familyRules(family, INDUSTRIAL_VARIANTS, weight / INDUSTRIAL_VARIANTS, BUILDING_SCALE);

/** A building of `id` taking `footprint` of ground (its model radius at the largest scale). */
const building = (id: string, weight: number, footprint: number) => ({
  id,
  weight,
  footprint,
  scale: BUILDING_SCALE,
});

const tree = (id: string, weight: number, footprint: number) => ({
  id,
  weight,
  footprint,
  scale: TREE_SCALE,
});

/** Model radius of the pumpjack (world units, at scale 1): its model stays inside it. */
export const PUMPJACK_RADIUS = 7;

/**
 * The props of World 2 (P08-R03, R07; reworked at the reviewer's request, 2026-10-27): World 1's
 * desert homes, outposts and plants, Level Zero's industrial buildings, the industrial buildings
 * made of parts, and the oil pumpjacks; each section picks the groups that stand on it, so the
 * industry slowly takes over the desert.
 */
export const WORLD_2_PROPS: PropRules = {
  cellSize: 50,
  treeClearance: 3,
  maxSlope: 0.12,
  treeMaxSlope: 0.45,
  minHeight: 4,
  zoneFrequency: 1 / 700,
  groups: [
    {
      id: G.desertHomes,
      weight: 3,
      kinds: [
        building(W1.desertHome, 3, 7.5),
        building(W1.windcatcherHome, 2, 7),
        building(W1.waterTower, 0.7, 5),
        building(P.domeHome, 0.4, 7),
      ],
    },
    {
      id: G.outposts,
      weight: 2,
      kinds: [
        building(W1.waterTower, 2, 5),
        building(W1.solarFarm, 2, 9.5),
        building(P.antenna, 1, 6),
        building(P.radar, 1, 7),
        building(P.tanks, 0.5, 10),
      ],
    },
    {
      id: G.mines,
      weight: 2,
      kinds: [
        building(W1.mineHeadframe, 4, 7),
        building(P.tanks, 1, 10),
        building(P.warehouse, 0.6, 15.5),
        building(W1.solarFarm, 0.6, 9.5),
        building(P.containerYard, 0.5, 8.5),
      ],
    },
    {
      id: G.workerHomes,
      weight: 3,
      kinds: [
        building(P.cubeHome, 3, 7.5),
        building(W1.desertHome, 2, 7.5),
        building(P.domeHome, 1, 7),
        building(W1.waterTower, 0.5, 5),
      ],
    },
    {
      id: G.oil,
      weight: 2,
      kinds: [
        building(W.pumpjack, 5, Math.ceil(PUMPJACK_RADIUS * BUILDING_SCALE[1] * 10) / 10),
        building(P.tanks, 2, 10),
        building(P.refinery, 0.4, 7.5),
      ],
    },
    {
      id: G.refinery,
      weight: 2,
      kinds: [
        building(P.refinery, 3, 7.5),
        building(P.tanks, 3, 10),
        building(P.coolingTower, 0.8, 9.5),
        building(P.containerYard, 0.8, 8.5),
        ...variants('industrial-complex', 2),
      ],
    },
    {
      id: G.industrial,
      weight: 3,
      kinds: [
        building(P.factory, 3, 15),
        building(P.warehouse, 3, 15.5),
        building(P.tanks, 1.5, 10),
        building(P.coolingTower, 1, 9.5),
        building(P.containerYard, 2, 8.5),
        building(P.refinery, 1, 7.5),
        ...variants('industrial-complex', 4),
      ],
    },
    {
      id: G.heavyIndustry,
      weight: 1,
      kinds: [
        ...variants('industrial-plant', 16),
        ...variants('industrial-works', 10),
        ...variants('industrial-complex', 5),
        building(P.containerYard, 4, 8.5),
        building(P.tanks, 4, 10),
        building(P.refinery, 3, 7.5),
        building(P.factory, 2, 15),
        building(P.warehouse, 2, 15.5),
        building(P.coolingTower, 2, 9.5),
      ],
    },
  ],
  trees: [
    tree(P.deadTree, 1, 1.5),
    tree(P.forkedTree, 0.6, 1.5),
    tree(W1.palm, 2, 4),
    tree(W1.dryBush, 3, 2.5),
    tree(W1.cactus, 2, 2),
  ],
  treesPerCell: 4,
  cars: CAR_RULES,
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
};

/** Plants of the sections, from the oases to the last dead trees between the factories. */
export const DESERT_PLANTS = {
  oasis: [W1.palm, W1.dryBush, P.bush],
  desert: [W1.cactus, W1.dryBush, P.deadTree],
  rock: [W1.dryBush, P.deadTree, P.forkedTree],
  town: [W1.palm, W1.dryBush],
  industry: [P.deadTree, W1.dryBush],
} as const;

/** Roads of World 2: as in World 1 (no crossings, phase 6 review). */
export const WORLD_2_ROADS: RoadRules = WORLD_1_ROADS;
