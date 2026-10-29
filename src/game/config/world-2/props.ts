import type { PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import { LOT_KINDS, tileKinds } from '../tile-buildings';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../prop-ids';
import { WORLD_1_PROP_IDS, WORLD_1_ROADS } from '../world-1/props';

const P = PROP_IDS;
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

const TREE_SCALE = [0.45, 0.75] as const;

const tree = (id: string, weight: number, footprint: number) => ({
  id,
  weight,
  footprint,
  scale: TREE_SCALE,
});

/**
 * The props of World 2 (P08-R03, R07; reworked at the reviewer's request, 2026-10-27): World 1's
 * desert homes, outposts and plants, Level Zero's industrial buildings, the industrial buildings
 * made of parts, and the oil pumpjacks; each section picks the groups that stand on it, so the
 * industry slowly takes over the desert.
 */
export const WORLD_2_PROPS: PropRules = {
  // Phase 15 (P15-R08): lots for the tiles of the districts no building fits.
  lots: LOT_KINDS,
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
      kinds: tileKinds('desertHomes'),
    },
    {
      id: G.outposts,
      weight: 2,
      kinds: tileKinds('outposts'),
    },
    {
      id: G.mines,
      weight: 2,
      kinds: tileKinds('industrial'),
    },
    {
      id: G.workerHomes,
      weight: 3,
      kinds: tileKinds('homes'),
    },
    {
      id: G.oil,
      weight: 2,
      kinds: tileKinds('industrial'),
    },
    {
      id: G.refinery,
      weight: 2,
      kinds: tileKinds('industrial'),
    },
    {
      id: G.industrial,
      weight: 3,
      kinds: tileKinds('industrial'),
    },
    {
      id: G.heavyIndustry,
      weight: 1,
      kinds: tileKinds('heavyIndustry'),
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
