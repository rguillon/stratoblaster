import type { PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import {
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  familyRules,
  type PartFamily,
} from '../building-families';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../level-zero';

/** Ids of the props added for World 1 (P06-R06). */
export const WORLD_1_PROP_IDS = {
  desertHome: 'desert-home',
  windcatcherHome: 'windcatcher-home',
  waterTower: 'water-tower',
  solarFarm: 'solar-farm',
  mineHeadframe: 'mine-headframe',
  beachHut: 'beach-hut',
  palm: 'palm-tree',
  dryBush: 'dry-bush',
  cactus: 'cactus',
  /** The farms of the green land (reviewer, 2026-10-26). */
  farmhouse: 'farmhouse',
  greenhouse: 'greenhouse',
  grainSilos: 'grain-silos',
} as const;

const P = PROP_IDS;
const W = WORLD_1_PROP_IDS;
/** World 2's wind turbine (`WORLD_2_PROP_IDS.windTurbine`; World 2's props import these). */
const WIND_TURBINE = 'wind-turbine';

/** Building groups of World 1; each section lists the ones that stand on it. */
export const WORLD_1_GROUPS = {
  /** Fishing huts and masts of the coast villages. */
  fishing: 'fishing',
  /** Coastal villages: huts and white homes. */
  coastHomes: 'coast-homes',
  /** Villages of the green land: futuristic homes among the farms (reviewer, 2026-10-26). */
  villages: 'villages',
  /** Farms of the green land: farmhouses, greenhouses, grain silos, wind turbines. */
  farms: 'farms',
  /** Futuristic desert homes (P06-R06). */
  desertHomes: 'desert-homes',
  /** Desert outposts: water towers, solar farms, antennas. */
  outposts: 'outposts',
  /** Mines, refinery, tanks: the desert industry (1-4). */
  industrial: 'industrial',
  heavyIndustry: 'heavy-industry',
  city: 'city',
} as const;

const G = WORLD_1_GROUPS;

/** Props are drawn small next to the ships, as in Level Zero. */
const BUILDING_SCALE = [0.5, 0.65] as const;
const TREE_SCALE = [0.45, 0.75] as const;
/** Lone huts and masts scattered on the islands, where no road goes (see `scatter` below). */
const LONE_SCALE = [0.5, 0.6] as const;

const variants = (family: PartFamily, count: number, weight: number) =>
  familyRules(family, count, weight, BUILDING_SCALE);

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

/**
 * The props of World 1 (P06-R05, R06): the building groups the sections pick from, and the
 * plants. Lone huts and masts are also listed with the plants: they stand alone on the islands
 * of 1-1, where no road goes, so they are scattered like plants instead of placed along roads.
 */
export const WORLD_1_PROPS: PropRules = {
  cellSize: 50,
  treeClearance: 3,
  maxSlope: 0.12,
  treeMaxSlope: 0.45,
  minHeight: 4,
  zoneFrequency: 1 / 700,
  groups: [
    {
      id: G.fishing,
      weight: 1,
      kinds: [building(W.beachHut, 4, 5), building(P.antenna, 0.5, 6)],
    },
    {
      id: G.coastHomes,
      weight: 2,
      kinds: [
        building(W.beachHut, 2, 5),
        building(P.cubeHome, 2, 7.5),
        building(P.domeHome, 1, 7),
        building(W.desertHome, 1, 7.5),
      ],
    },
    {
      id: G.villages,
      weight: 3,
      kinds: [
        building(P.cubeHome, 3, 7.5),
        building(P.domeHome, 2, 7),
        building(W.farmhouse, 1, 8.5),
        building(W.greenhouse, 0.6, 9.5),
      ],
    },
    {
      id: G.farms,
      weight: 2,
      kinds: [
        building(W.farmhouse, 3, 8.5),
        building(W.greenhouse, 2, 9.5),
        building(W.grainSilos, 2, 9.5),
        building(WIND_TURBINE, 1, 6),
      ],
    },
    {
      id: G.desertHomes,
      weight: 3,
      kinds: [
        building(W.desertHome, 3, 7.5),
        building(W.windcatcherHome, 2, 7),
        building(W.waterTower, 0.7, 5),
        building(P.domeHome, 0.4, 7),
      ],
    },
    {
      id: G.outposts,
      weight: 2,
      kinds: [
        building(W.waterTower, 2, 5),
        building(W.solarFarm, 2, 9.5),
        building(P.antenna, 1, 6),
        building(P.radar, 1, 7),
        building(P.tanks, 1, 10),
      ],
    },
    {
      id: G.industrial,
      weight: 2,
      kinds: [
        building(W.mineHeadframe, 3, 7),
        building(P.refinery, 2, 7.5),
        building(P.tanks, 2, 10),
        building(P.warehouse, 1, 15.5),
        building(P.containerYard, 1, 8.5),
        ...variants('industrial-complex', INDUSTRIAL_VARIANTS, 1),
      ],
    },
    {
      id: G.heavyIndustry,
      weight: 1,
      kinds: [
        ...variants('industrial-plant', INDUSTRIAL_VARIANTS, 6),
        ...variants('industrial-works', INDUSTRIAL_VARIANTS, 3),
        ...variants('industrial-complex', INDUSTRIAL_VARIANTS, 1),
        building(W.mineHeadframe, 0.5, 7),
        building(P.refinery, 0.5, 7.5),
        building(P.tanks, 0.5, 10),
      ],
    },
    {
      id: G.city,
      weight: 1,
      kinds: [
        ...variants('city-block', CITY_VARIANTS, 6),
        ...variants('city-tower', CITY_VARIANTS, 3),
      ],
    },
  ],
  trees: [
    tree(P.deadTree, 1, 1.5),
    tree(P.forkedTree, 1, 1.5),
    tree(W.palm, 2, 4),
    tree(W.dryBush, 3, 2.5),
    tree(W.cactus, 2, 2),
    tree(P.bush, 1, 3.5),
    tree(P.broadleaf, 2, 4.5),
    tree(P.conifer, 1, 3.5),
    { id: W.beachHut, weight: 0.3, footprint: 4.5, scale: LONE_SCALE },
    { id: P.antenna, weight: 0.1, footprint: 5, scale: LONE_SCALE },
  ],
  treesPerCell: 4,
  cars: CAR_RULES,
  // Phase 6 review: a few buildings away from the roads, and hamlets from time to time.
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
};

/** Plants of the sections, and the lone huts of the islands. */
export const PLANTS = {
  islands: [W.palm, P.bush, W.beachHut, P.antenna],
  coast: [W.palm, P.bush, P.broadleaf],
  /** The green land (reviewer, 2026-10-26): meadows, then woods and groves. */
  meadow: [P.broadleaf, P.bush],
  woods: [P.broadleaf, P.conifer, P.bush],
  /** Where the grass turns dry and yellow. */
  dryGrass: [W.dryBush, P.broadleaf, P.forkedTree],
  dry: [W.dryBush, P.deadTree, P.forkedTree],
  desert: [W.cactus, W.dryBush, P.deadTree],
  oasis: [W.palm, P.bush, W.dryBush],
  town: [W.palm, W.dryBush],
} as const;

/**
 * Roads of World 1 (P04-R07): one winding 2×2 highway and a second road, paths every 260-560
 * units, starting and ending off screen, as in Level Zero; unlike there, no road crosses
 * another (phase 6 review).
 */
export const WORLD_1_ROADS: RoadRules = {
  mainRoads: 2,
  spread: 200,
  meander: { amplitude: [80, 180], wavelength: [1300, 2600] },
  crossSpacing: [260, 560],
  crossBend: 40,
  mainWidth: 6,
  crossWidth: 4,
  dual: { width: 12, mainRoads: 1, avenues: 0.25 },
  junction: { width: 14, length: 28 },
  offscreenX: 420,
  turnRate: 0.05,
  minHeight: 3,
  maxSlope: 0.5,
  minRun: 6,
  step: 8,
  slotSpacing: 24,
  setback: 2,
  // Phase 6 review: roads never cross; paths only join roads.
  noCrossings: { gap: 30 },
};
