import type { FloatRules, PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import { JUNGLE_VARIANTS, familyRules, type PartFamily } from '../building-families';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../level-zero';
import { WORLD_1_ROADS } from '../world-1/props';

/** Ids of the props added for World 3, the Jungle (P09-R06). */
export const WORLD_3_PROP_IDS = {
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

/** Building groups of World 3; each section lists the ones that stand on it. */
export const WORLD_3_GROUPS = {
  /** Stilt huts and fishing docks along the delta's channels. */
  riverHuts: 'river-huts',
  /** The small river port at the end of 3-1 and the start of 3-2. */
  riverPort: 'river-port',
  /** Stilt villages along the rainforest river. */
  villages: 'stilt-villages',
  /** Logging camps in the clearings. */
  logging: 'logging-camps',
  /** Overgrown temple ruins: pyramids, statues, shrines. */
  ruins: 'temple-ruins',
  /** The enemy's outposts in the ruins: gun pits, antennas, neon gates. */
  outposts: 'ruin-outposts',
  /** Bio-labs on stilts and pumping stations of the swamp. */
  swampLabs: 'swamp-labs',
  /** Tree-top outposts at the edge of the canopy city. */
  treetop: 'treetop-outposts',
  /** Towers rising out of the canopy, linked by sky bridges. */
  canopyCity: 'canopy-city',
  /** The dense city centre, trees on the roofs. */
  canopyCentre: 'canopy-centre',
} as const;

const G = WORLD_3_GROUPS;

/** Props are drawn small next to the ships, as in Worlds 1 and 2. */
const BUILDING_SCALE = [0.5, 0.65] as const;
const TREE_SCALE = [0.45, 0.75] as const;
/** The canopy's crowns are bigger, so they close over the ground. */
const CANOPY_SCALE = [0.7, 1] as const;

const variants = (family: PartFamily, weight: number) =>
  familyRules(family, JUNGLE_VARIANTS, weight, BUILDING_SCALE);

/**
 * Model radii (world units, at scale 1) of the World 3 buildings and set pieces: their models
 * stay inside these circles (P04-R04 footprints).
 */
export const WORLD_3_RADII: Readonly<Record<string, number>> = {
  [W.stiltHut]: 7,
  [W.longhouse]: 11,
  [W.riverDock]: 13,
  [W.sawmill]: 13,
  [W.logPile]: 7,
  [W.stepPyramid]: 22,
  [W.templeStatue]: 6,
  [W.ruinShrine]: 9,
  [W.gunPit]: 8,
  [W.neonGate]: 9,
  [W.ruinAntenna]: 7,
  [W.bioLab]: 12,
  [W.pumpingStation]: 11,
  [W.powerPlant]: 18,
  [W.treetopPlatform]: 10,
  [W.skyBridgeTowers]: 16,
};

const radius = (id: string): number => WORLD_3_RADII[id] ?? 10;
/** A building of `id`, whose model fits in its circle of `WORLD_3_RADII`. */
const b = (id: string, weight: number) => ({
  id,
  weight,
  footprint: Math.ceil(radius(id) * BUILDING_SCALE[1] * 10) / 10,
  scale: BUILDING_SCALE,
});

const tree = (
  id: string,
  weight: number,
  footprint: number,
  scale: readonly [number, number] = TREE_SCALE,
) => ({
  id,
  weight,
  footprint,
  scale,
});

/**
 * What grows and stands on the water (P09-R06): reeds and lily pads on the swamps and the delta's
 * channels, mangroves on their stilt roots, fishing platforms. They sit at the water's level
 * where it is at least `depth` deep, with the chance of each section's `floatDensity`.
 */
export const WORLD_3_FLOATING: FloatRules = {
  cellSize: 40,
  perCell: 2,
  depth: 1,
  kinds: [
    { id: W.lilyPads, weight: 4, footprint: 5, scale: [0.6, 1] },
    { id: W.reeds, weight: 3, footprint: 4, scale: [0.6, 1] },
    { id: W.mangrove, weight: 2, footprint: 6, scale: [0.6, 0.85] },
    { id: W.fishingPlatform, weight: 0.25, footprint: 7, scale: [0.5, 0.6] },
  ],
};

/**
 * The props of World 3 (P09-R03, R06): the building groups the sections pick from, the plants
 * (the canopy first: big crowns packed edge to edge), and what stands on the water. Lone stilt
 * huts stand among the trees like plants.
 */
export const WORLD_3_PROPS: PropRules = {
  cellSize: 50,
  treeClearance: 2,
  maxSlope: 0.12,
  treeMaxSlope: 0.6,
  minHeight: 2,
  zoneFrequency: 1 / 700,
  groups: [
    {
      id: G.riverHuts,
      weight: 2,
      kinds: [b(W.stiltHut, 4), b(W.longhouse, 1.5), b(W.riverDock, 0.6)],
    },
    {
      id: G.riverPort,
      weight: 1,
      kinds: [
        b(W.riverDock, 2),
        b(W.longhouse, 2),
        b(W.sawmill, 1),
        { ...b(P.containerYard, 1), footprint: 8.5 },
        { ...b(P.warehouse, 0.5), footprint: 15.5 },
      ],
    },
    {
      id: G.villages,
      weight: 3,
      kinds: [b(W.stiltHut, 4), b(W.longhouse, 2), b(W.logPile, 0.5)],
    },
    {
      id: G.logging,
      weight: 2,
      kinds: [b(W.sawmill, 2), b(W.logPile, 3), b(W.stiltHut, 1)],
    },
    {
      id: G.ruins,
      weight: 2,
      kinds: [b(W.stepPyramid, 1.2), b(W.templeStatue, 2), b(W.ruinShrine, 2)],
    },
    {
      id: G.outposts,
      weight: 2,
      kinds: [b(W.gunPit, 2), b(W.neonGate, 1), b(W.ruinAntenna, 1.5), b(W.ruinShrine, 1)],
    },
    {
      id: G.swampLabs,
      weight: 2,
      kinds: [b(W.bioLab, 3), b(W.pumpingStation, 2), { ...b(P.tanks, 0.5), footprint: 10 }],
    },
    {
      id: G.treetop,
      weight: 2,
      kinds: [b(W.treetopPlatform, 3), b(W.stiltHut, 1), b(W.skyBridgeTowers, 0.4)],
    },
    {
      id: G.canopyCity,
      weight: 2,
      kinds: [b(W.skyBridgeTowers, 2), ...variants('canopy-tower', 1), b(W.treetopPlatform, 1)],
    },
    {
      id: G.canopyCentre,
      weight: 1,
      kinds: [...variants('canopy-block', 6), ...variants('canopy-tower', 3)],
    },
  ],
  trees: [
    tree(W.canopyCluster, 6, 14.1, CANOPY_SCALE),
    tree(W.canopyCrown, 1.5, 7.8, CANOPY_SCALE),
    tree(W.junglePalm, 2, 4.3),
    tree(W.giantFern, 2, 4.4),
    tree(W.mangrove, 1.5, 4),
    tree(W.swampTree, 1.5, 3.7),
    { id: W.stiltHut, weight: 0.2, footprint: 4.6, scale: [0.5, 0.6] },
  ],
  treesPerCell: 10,
  cars: CAR_RULES,
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
  floating: WORLD_3_FLOATING,
};

/** Plants of the sections (P09-R03, R06). */
export const JUNGLE_PLANTS = {
  delta: [W.mangrove, W.junglePalm, W.giantFern],
  forestEdge: [W.canopyCluster, W.junglePalm, W.mangrove, W.giantFern],
  rainforest: [W.canopyCluster, W.canopyCrown, W.junglePalm, W.giantFern],
  clearing: [W.giantFern, W.junglePalm, W.canopyCrown],
  hills: [W.canopyCluster, W.canopyCrown, W.giantFern],
  swamp: [W.swampTree, W.mangrove, W.giantFern],
  town: [W.junglePalm, W.canopyCrown, W.giantFern],
} as const;

/**
 * Roads of World 3: as in World 1 (no crossings, phase 6 review); the looks make them red dirt
 * tracks.
 */
export const WORLD_3_ROADS: RoadRules = WORLD_1_ROADS;
