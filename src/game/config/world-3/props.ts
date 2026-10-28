import type { PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import { INDUSTRIAL_VARIANTS, familyRules, type PartFamily } from '../building-families';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../level-zero';
import { WORLD_1_PROP_IDS, WORLD_1_ROADS } from '../world-1/props';

/**
 * Ids of the props added for World 3 (P09-R06). The jungle ones were made for the first World 3,
 * the Jungle; since the reviewer's rework (2026-10-27) no level places them, only the homes.
 */
export const WORLD_3_PROP_IDS = {
  // The homes, from the factories to the garden suburbs (reviewer, 2026-10-27).
  suburbHouse: 'suburb-house',
  rowHouses: 'row-houses',
  walkUp: 'walk-up-flats',
  // Plants.
  canopyCluster: 'canopy-cluster',
  canopyCrown: 'canopy-crown',
  junglePalm: 'jungle-palm',
  giantFern: 'giant-fern',
  mangrove: 'mangrove',
  swampTree: 'swamp-tree',
  // On the water.
  reeds: 'reeds',
  lilyPads: 'lily-pads',
  fishingPlatform: 'fishing-platform',
  // Stilt villages, river ports and logging camps.
  stiltHut: 'stilt-hut',
  longhouse: 'stilt-longhouse',
  riverDock: 'river-dock',
  sawmill: 'sawmill',
  logPile: 'log-pile',
  // Temple ruins and the enemy outposts in them.
  stepPyramid: 'step-pyramid',
  templeStatue: 'temple-statue',
  ruinShrine: 'ruin-shrine',
  causeway: 'causeway',
  gunPit: 'gun-pit',
  neonGate: 'neon-gate',
  ruinAntenna: 'ruin-antenna',
  // Swamp works.
  bioLab: 'bio-lab',
  swampPipeline: 'swamp-pipeline',
  pumpingStation: 'pumping-station',
  dam: 'giant-dam',
  powerPlant: 'dam-power-plant',
  // The canopy city.
  treetopPlatform: 'treetop-platform',
  skyBridgeTowers: 'sky-bridge-towers',
  // Water features.
  waterfall: 'waterfall',
} as const;

const P = PROP_IDS;
const W = WORLD_3_PROP_IDS;
const W1 = WORLD_1_PROP_IDS;

/** Building groups of World 3; each section lists the ones that stand on it. */
export const WORLD_3_GROUPS = {
  /** Dense heavy industry, where World 2 ended: large plants and works made of parts. */
  heavyIndustry: 'w3-heavy-industry',
  /** Factories, warehouses, yards, tanks and cooling towers. */
  industrial: 'w3-industrial',
  /** The canal docks: container yards, warehouses and tanks. */
  docks: 'w3-docks',
  /** Workshops and small works among the first flats. */
  workshops: 'w3-workshops',
  /** The workers' flats: small blocks, terraces. */
  workerFlats: 'w3-worker-flats',
  /** Rows of terraced houses. */
  terraces: 'w3-terraces',
  /** The suburbs: houses, terraces, modern homes. */
  suburbs: 'w3-suburbs',
  /** The garden villages: houses, farmhouses and greenhouses. */
  villages: 'w3-villages',
} as const;

const G = WORLD_3_GROUPS;

/** Props are drawn small next to the ships, as in Worlds 1 and 2. */
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

/** Model radii of the homes (world units, at scale 1): their models stay inside them. */
export const HOME_RADII = {
  [W.suburbHouse]: 8.3,
  [W.rowHouses]: 11.1,
  [W.walkUp]: 8.5,
} as const;

/** A home of `id`, whose model fits in its circle of `HOME_RADII`. */
const home = (id: keyof typeof HOME_RADII, weight: number) =>
  building(id, weight, Math.ceil(HOME_RADII[id] * BUILDING_SCALE[1] * 10) / 10);

/**
 * The props of World 3 (P09-R03, R06; reworked at the reviewer's request, 2026-10-27): Level
 * Zero's industrial buildings and those made of parts, then the workers' flats, terraces and
 * houses, and the farms of World 1's green land; each section picks the groups that stand on
 * it, so the homes slowly take over the factories. Small buildings only at the end: no tower.
 */
export const WORLD_3_PROPS: PropRules = {
  cellSize: 50,
  treeClearance: 3,
  maxSlope: 0.12,
  treeMaxSlope: 0.45,
  minHeight: 4,
  zoneFrequency: 1 / 700,
  groups: [
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
      id: G.docks,
      weight: 2,
      kinds: [
        building(P.containerYard, 4, 8.5),
        building(P.warehouse, 3, 15.5),
        building(P.tanks, 1.5, 10),
        building(P.factory, 0.5, 15),
        ...variants('industrial-complex', 1),
      ],
    },
    {
      id: G.workshops,
      weight: 3,
      kinds: [
        building(P.warehouse, 2, 15.5),
        building(P.factory, 1, 15),
        building(P.containerYard, 1, 8.5),
        home(W.walkUp, 2.5),
        building(P.cubeHome, 0.5, 7.5),
      ],
    },
    {
      id: G.workerFlats,
      weight: 3,
      kinds: [
        home(W.walkUp, 4),
        home(W.rowHouses, 2),
        building(P.cubeHome, 0.5, 7.5),
        building(P.warehouse, 0.3, 15.5),
      ],
    },
    {
      id: G.terraces,
      weight: 3,
      kinds: [home(W.rowHouses, 4), home(W.walkUp, 1), home(W.suburbHouse, 1)],
    },
    {
      id: G.suburbs,
      weight: 3,
      kinds: [
        home(W.suburbHouse, 4),
        home(W.rowHouses, 1),
        building(P.cubeHome, 1.5, 7.5),
        building(P.domeHome, 0.4, 7),
      ],
    },
    {
      id: G.villages,
      weight: 3,
      kinds: [
        home(W.suburbHouse, 3),
        building(W1.farmhouse, 1, 8.5),
        building(W1.greenhouse, 0.8, 9.5),
        building(P.domeHome, 0.4, 7),
        building(P.cubeHome, 0.5, 7.5),
      ],
    },
  ],
  trees: [
    tree(P.deadTree, 1, 1.5),
    tree(P.forkedTree, 0.6, 1.5),
    tree(P.bush, 2, 3.5),
    tree(P.broadleaf, 3, 4.5),
    tree(P.conifer, 1.5, 3.5),
  ],
  treesPerCell: 4,
  cars: CAR_RULES,
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
};

/** Plants of the sections, from the last dead trees by the factories to the gardens. */
export const TOWN_PLANTS = {
  industry: [P.deadTree, P.bush],
  yards: [P.deadTree, P.forkedTree, P.bush],
  streets: [P.broadleaf, P.bush],
  parks: [P.broadleaf, P.conifer, P.bush],
  gardens: [P.broadleaf, P.bush, P.conifer],
} as const;

/**
 * Roads of World 3: as in World 1 (no crossings, phase 6 review), but the street grids stop
 * closer to the screen edges (reviewer, 2026-10-28): the ground is drawn twice as big, so only
 * about ±195 of it shows, and the streets and buildings generated out to ±420 were never seen.
 */
export const WORLD_3_ROADS: RoadRules = { ...WORLD_1_ROADS, offscreenX: 240 };
