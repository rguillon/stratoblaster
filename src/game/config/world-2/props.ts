import type {
  FloatRules,
  PropLine,
  PropRules,
  RoadRules,
} from '../../../core/scenery/scenery-level';
import { POLAR_VARIANTS, familyRules, type PartFamily } from '../building-families';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../level-zero';
import { WORLD_1_ROADS } from '../world-1/props';

/** Ids of the props added for World 2, the Frozen North (P08-R07). */
export const WORLD_2_PROP_IDS = {
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

/** Building groups of World 2; each section lists the ones that stand on it. */
export const WORLD_2_GROUPS = {
  /** Lone posts of the cold coasts: a lighthouse, huts, a mast. */
  coastPosts: 'coast-posts',
  /** Fishing villages along the fjords. */
  fishing: 'polar-fishing',
  /** A harbour: cranes, fish stores, containers. */
  harbour: 'polar-harbour',
  /** Futuristic northern homes: chalets and heated domes. */
  homes: 'northern-homes',
  /** Research outposts of the tundra: radar domes, antennas, wind turbines. */
  research: 'research',
  /** Mining outposts on the glacier's edge. */
  mining: 'mining',
  /** The big mining complex of 2-4. */
  heavyMining: 'heavy-mining',
  /** The mining town and suburbs of 2-5. */
  polarTown: 'polar-town',
  /** The dense polar city centre of 2-5. */
  polarCity: 'polar-city',
} as const;

const G = WORLD_2_GROUPS;

/** Props are drawn small next to the ships, as in World 1. */
const BUILDING_SCALE = [0.5, 0.65] as const;
const TREE_SCALE = [0.45, 0.75] as const;
const LONE_SCALE = [0.5, 0.6] as const;

const variants = (family: PartFamily, weight: number) =>
  familyRules(family, POLAR_VARIANTS, weight, BUILDING_SCALE);

/** A building of `id`, whose model fits in a circle of `radius` (world units, at scale 1). */
const building = (id: string, weight: number, radius: number) => ({
  id,
  weight,
  footprint: Math.ceil(radius * BUILDING_SCALE[1] * 10) / 10,
  scale: BUILDING_SCALE,
});

const tree = (id: string, weight: number, footprint: number) => ({
  id,
  weight,
  footprint,
  scale: TREE_SCALE,
});

/**
 * Model radii (world units, at scale 1) of the World 2 buildings: their models stay inside
 * these circles (P04-R04 footprints).
 */
export const WORLD_2_RADII: Readonly<Record<string, number>> = {
  [W.chalet]: 11,
  [W.longChalet]: 12.5,
  [W.hut]: 7,
  [W.heatedDome]: 11,
  [W.lighthouse]: 7,
  [W.harbourCrane]: 13,
  [W.fishStore]: 14,
  [W.radarDome]: 10,
  [W.antennaArray]: 10,
  [W.windTurbine]: 8,
  [W.drillTower]: 10,
  [W.conveyor]: 15,
  [W.oreSilo]: 9,
  [W.miningCrane]: 13,
};

const radius = (id: string): number => WORLD_2_RADII[id] ?? 10;
const b = (id: string, weight: number) => building(id, weight, radius(id));

/** Ice floating on the cold sea of 2-1 (P08-R07): floes and icebergs drift very slowly. */
export const WORLD_2_FLOATING: FloatRules = {
  cellSize: 60,
  perCell: 1,
  depth: 6,
  kinds: [
    {
      id: W.floeSmall,
      weight: 5,
      footprint: 7,
      scale: [0.6, 1],
      drift: { x: 6, z: 4, period: 70 },
    },
    {
      id: W.floeLarge,
      weight: 2,
      footprint: 16,
      scale: [0.6, 1],
      drift: { x: -5, z: 3, period: 90 },
    },
    {
      id: W.iceberg,
      weight: 0.6,
      footprint: 13,
      scale: [0.6, 0.9],
      drift: { x: 3, z: -2, period: 120 },
    },
    {
      id: W.weatherBuoy,
      weight: 0.08,
      footprint: 3,
      scale: [0.6, 0.7],
      drift: { x: 1, z: 1, period: 9 },
    },
  ],
};

/**
 * The props of World 2 (P08-R03, R07): the building groups the sections pick from, the plants,
 * and the ice on the sea. Lone huts and masts stand on the islands of 2-1 like plants.
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
      id: G.coastPosts,
      weight: 1,
      kinds: [b(W.lighthouse, 1), b(W.hut, 3), b(W.antennaArray, 0.5)],
    },
    {
      id: G.fishing,
      weight: 2,
      kinds: [b(W.hut, 3), b(W.chalet, 2), b(W.fishStore, 1), b(W.harbourCrane, 0.5)],
    },
    {
      id: G.harbour,
      weight: 1,
      kinds: [
        b(W.harbourCrane, 2),
        b(W.fishStore, 2),
        building(P.containerYard, 1, 13),
        building(P.tanks, 0.5, 15),
      ],
    },
    {
      id: G.homes,
      weight: 3,
      kinds: [b(W.chalet, 3), b(W.longChalet, 2), b(W.heatedDome, 1), b(W.hut, 0.5)],
    },
    {
      id: G.research,
      weight: 2,
      kinds: [b(W.radarDome, 2), b(W.antennaArray, 1.5), b(W.windTurbine, 1.5), b(W.heatedDome, 1)],
    },
    {
      id: G.mining,
      weight: 2,
      kinds: [b(W.drillTower, 3), b(W.conveyor, 2), b(W.oreSilo, 2), b(W.miningCrane, 1)],
    },
    {
      id: G.heavyMining,
      weight: 1,
      kinds: [...variants('mining-complex', 6), b(W.oreSilo, 1), b(W.drillTower, 1)],
    },
    {
      id: G.polarTown,
      weight: 2,
      kinds: [
        ...variants('polar-tower', 2),
        b(W.chalet, 2),
        b(W.longChalet, 2),
        b(W.heatedDome, 2),
      ],
    },
    {
      id: G.polarCity,
      weight: 1,
      kinds: [...variants('polar-block', 6), ...variants('polar-tower', 3)],
    },
  ],
  trees: [
    tree(W.snowPine, 4, 3),
    tree(W.frostedTree, 1.5, 2),
    tree(W.snowyBush, 2, 2.5),
    { id: W.hut, weight: 0.25, footprint: 4.5, scale: LONE_SCALE },
    { id: P.antenna, weight: 0.1, footprint: 5, scale: LONE_SCALE },
  ],
  treesPerCell: 4,
  cars: CAR_RULES,
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
  floating: WORLD_2_FLOATING,
};

/** Plants of the sections, and the lone huts of the islands. */
export const POLAR_PLANTS = {
  islands: [W.snowyBush, W.hut, P.antenna],
  coast: [W.snowPine, W.snowyBush, W.frostedTree],
  forest: [W.snowPine, W.snowPine, W.frostedTree],
  tundra: [W.snowyBush, W.frostedTree, W.snowPine],
  glacier: [W.frostedTree],
  town: [W.snowPine, W.snowyBush],
} as const;

/**
 * The pipeline on stilts of 2-3 (P08-R03): one 15-unit piece every 15 along a gentle line across
 * the tundra, from end to end.
 */
export const TUNDRA_PIPELINE: PropLine = {
  kind: W.pipeline,
  path: { x: 120, amplitude: 70, wavelength: 3200 },
  spacing: 15,
  footprint: 9,
  maxSlope: 0.6,
};

/** Roads of World 2: as in World 1 (no crossings, phase 6 review), on snowy ground. */
export const WORLD_2_ROADS: RoadRules = WORLD_1_ROADS;
