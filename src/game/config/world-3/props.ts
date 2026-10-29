import type { PropRules, RoadRules } from '../../../core/scenery/scenery-level';
import { LOT_KINDS, tileKinds } from '../tile-buildings';
import { CAR_RULES } from '../cars';
import { PROP_IDS } from '../prop-ids';
import { WORLD_1_ROADS } from '../world-1/props';

const P = PROP_IDS;

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
  /** The residences (reviewer, 2026-10-28: the terraces and suburbs as one): homes of the future. */
  residences: 'w3-residences',
  /** The garden villages: houses, farmhouses and greenhouses. */
  villages: 'w3-villages',
} as const;

const G = WORLD_3_GROUPS;

/** Plants are drawn small next to the ships, as in Worlds 1 and 2. */
const TREE_SCALE = [0.45, 0.75] as const;

const tree = (id: string, weight: number, footprint: number) => ({
  id,
  weight,
  footprint,
  scale: TREE_SCALE,
});

/**
 * The props of World 3 (P09-R03, R06; reworked at the reviewer's request, 2026-10-27): Level
 * Zero's industrial buildings and those made of parts, then the workers' flats, terraces and
 * houses, and the farms of World 1's green land; each section picks the groups that stand on
 * it, so the homes slowly take over the factories. Small buildings only at the end: no tower.
 */
export const WORLD_3_PROPS: PropRules = {
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
      id: G.heavyIndustry,
      weight: 1,
      kinds: tileKinds('heavyIndustry'),
    },
    {
      id: G.industrial,
      weight: 3,
      kinds: tileKinds('industrial'),
    },
    {
      id: G.docks,
      weight: 2,
      kinds: tileKinds('docks'),
    },
    {
      id: G.workshops,
      weight: 3,
      kinds: tileKinds('workshops'),
    },
    {
      id: G.workerFlats,
      weight: 3,
      kinds: tileKinds('workerFlats'),
    },
    {
      id: G.residences,
      weight: 3,
      kinds: tileKinds('residences'),
    },
    {
      id: G.villages,
      weight: 3,
      kinds: tileKinds('homes'),
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
