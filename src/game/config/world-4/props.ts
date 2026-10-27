import type {
  FloatRules,
  Meander,
  PropLine,
  PropRules,
  RoadRules,
} from '../../../core/scenery/scenery-level';
import { CAR_RULES } from '../cars';
import { WORLD_1_ROADS } from '../world-1/props';

/**
 * Ids of the props added for World 4, the Volcanic Lands (P10-R08). Since the reviewer's rework
 * (2026-10-27) no level places them: World 4 goes from the houses to the skyscrapers
 * (`city-props.ts`); the volcanic rules below are kept with their models.
 */
export const WORLD_4_PROP_IDS = {
  // Vegetation and rock.
  hardyGrass: 'hardy-grass',
  burntTree: 'burnt-tree',
  burntStump: 'burnt-stump',
  lavaBoulder: 'lava-boulder',
  smokingVent: 'smoking-vent',
  sulphurVent: 'sulphur-vent',
  // On the sea and the hot coast.
  seaSteam: 'sea-steam',
  hotSpring: 'hot-spring',
  // 4-1: fishing huts, geothermal wells, the small harbour.
  fishingHut: 'fishing-hut',
  geothermalWell: 'geothermal-well',
  harbourDock: 'harbour-dock',
  // Not 'harbour-crane' / 'cooling-tower': those ids are World 2's and Level Zero's models.
  harbourCrane: 'volcanic-crane',
  // 4-2: geothermal power, ash-covered settlements.
  powerPlant: 'geothermal-plant',
  coolingTower: 'volcanic-cooling-tower',
  pipeline: 'volcanic-pipeline',
  ashHut: 'ash-hut',
  ashHouse: 'ash-house',
  // 4-3: mining on the cooled rock, lava works.
  miningOutpost: 'mining-outpost',
  lavaPump: 'lava-pump',
  heatCollector: 'heat-collector',
  // 4-4: the giant foundries.
  smelter: 'smelter',
  blastFurnace: 'blast-furnace',
  chimneyRow: 'chimney-row',
  gantryCrane: 'gantry-crane',
  railLine: 'rail-line',
  oreWagon: 'ore-wagon',
  slagHeap: 'slag-heap',
  // 4-5: the war factory and the fortress city.
  hangar: 'war-hangar',
  launchPad: 'launch-pad',
  armouredTower: 'armoured-tower',
  fortressBlock: 'fortress-block',
} as const;

/** Building groups of World 4; each section lists the ones that stand on it. */
export const VOLCANIC_GROUPS = {
  /** Fishing huts on the black-sand beaches of the islands (4-1). */
  fishing: 'fishing-huts',
  /** Geothermal wells on the islands and the plains (4-1, 4-2). */
  wells: 'geothermal-wells',
  /** The small harbour on 4-1's final coast. */
  harbour: 'volcanic-harbour',
  /** Ash-covered settlements along the road (4-2). */
  ashTowns: 'ash-towns',
  /** Geothermal power plants and cooling towers (4-2). */
  powerPlants: 'geothermal-plants',
  /** Mining outposts on the cooled basalt (4-3). */
  mining: 'mining-outposts',
  /** Lava pumps and heat collectors by the lava (4-3). */
  lavaWorks: 'lava-works',
  /** The giant foundries: smelters, blast furnaces, chimney rows (4-4). */
  foundries: 'foundries',
  /** Rail yards, cranes and slag heaps between the foundries (4-4). */
  railYards: 'rail-yards',
  /** The war factory on the caldera rim: hangars, launch pads, armoured towers (4-5). */
  warFactory: 'war-factory',
  /** The fortress city at the edge of the magma lake (4-5). */
  fortressCity: 'fortress-city',
} as const;

const W = WORLD_4_PROP_IDS;
const G = VOLCANIC_GROUPS;

/**
 * What grows and lies on the ground of each kind of section (P10-R08), as `TerrainSection.trees`
 * lists: hardy grass and vents on the islands, burnt trees and a few hot springs on the ash
 * plains, nothing living in the lava fields (only rock and vents).
 */
export const VOLCANIC_SCATTER = {
  islands: [W.hardyGrass, W.smokingVent, W.lavaBoulder],
  coast: [W.hardyGrass, W.lavaBoulder],
  ashPlains: [W.burntTree, W.burntStump, W.smokingVent, W.hotSpring],
  deadForest: [W.burntTree, W.burntStump],
  lavaFields: [W.lavaBoulder, W.smokingVent, W.sulphurVent],
  scorched: [W.burntStump, W.lavaBoulder],
  slopes: [W.lavaBoulder, W.sulphurVent],
} as const;

/** Props are drawn small next to the ships, as in Worlds 1 to 3. */
const BUILDING_SCALE = [0.5, 0.65] as const;
/** The enemy's foundries, war factory and fortress are bigger than the homes and wells. */
const GIANT_SCALE = [0.6, 0.8] as const;
const TREE_SCALE = [0.45, 0.75] as const;

/**
 * Model radii (world units, at scale 1) of the World 4 buildings: their models (lights included)
 * stay inside these circles (P04-R04 footprints).
 */
export const WORLD_4_RADII: Readonly<Record<string, number>> = {
  [W.hotSpring]: 6,
  [W.fishingHut]: 7,
  [W.geothermalWell]: 7,
  [W.harbourDock]: 13,
  [W.harbourCrane]: 10,
  [W.powerPlant]: 17,
  [W.coolingTower]: 10,
  [W.ashHut]: 7,
  [W.ashHouse]: 10,
  [W.miningOutpost]: 10.5,
  [W.lavaPump]: 9,
  [W.heatCollector]: 10,
  [W.smelter]: 14.5,
  [W.blastFurnace]: 14.5,
  [W.chimneyRow]: 13.5,
  [W.gantryCrane]: 12,
  [W.slagHeap]: 9.5,
  [W.hangar]: 15,
  [W.launchPad]: 13,
  [W.armouredTower]: 7,
  [W.fortressBlock]: 16.5,
};

const radius = (id: string): number => WORLD_4_RADII[id] ?? 10;
/** A building of `id`, whose model fits in its circle of `WORLD_4_RADII` at `scale`. */
const b = (id: string, weight: number, scale: readonly [number, number] = BUILDING_SCALE) => ({
  id,
  weight,
  footprint: Math.ceil(radius(id) * scale[1] * 10) / 10,
  scale,
});
/** One of the enemy's giant buildings. */
const giant = (id: string, weight: number) => b(id, weight, GIANT_SCALE);

const tree = (
  id: string,
  weight: number,
  footprint: number,
  scale: readonly [number, number] = TREE_SCALE,
) => ({ id, weight, footprint, scale });

/**
 * What stands on the hot sea of 4-1 (P10-R08): steam rising off the water (a ring of disturbed
 * water, a steam plume), and black rocks sticking out of it. They sit at the water's level where
 * it is at least `depth` deep, with the chance of each section's `floatDensity`: the sea sections
 * near the islands and the hot coast get a high `floatDensity`, the open sea a low one.
 */
export const VOLCANIC_FLOATING: FloatRules = {
  cellSize: 45,
  perCell: 2,
  depth: 1,
  kinds: [
    { id: W.seaSteam, weight: 4, footprint: 5.1, scale: [0.8, 1.2] },
    { id: W.lavaBoulder, weight: 1, footprint: 3.9, scale: [0.6, 1] },
  ],
};

/**
 * The props of the first World 4, the Volcanic Lands (P10-R03, R08): the building groups the
 * sections picked from, what grows and lies on the ground (`VOLCANIC_SCATTER` picks per section),
 * and what stands on the hot sea. Lone ash huts stand out on the plains like the scatter. No
 * level uses them since the reviewer's rework (2026-10-27); kept with their models.
 */
export const VOLCANIC_PROPS: PropRules = {
  cellSize: 50,
  treeClearance: 2,
  maxSlope: 0.12,
  treeMaxSlope: 0.6,
  minHeight: 2,
  zoneFrequency: 1 / 700,
  groups: [
    { id: G.fishing, weight: 2, kinds: [b(W.fishingHut, 4), b(W.geothermalWell, 0.6)] },
    {
      id: G.wells,
      weight: 2,
      kinds: [b(W.geothermalWell, 3), b(W.hotSpring, 1), b(W.ashHut, 0.5)],
    },
    {
      id: G.harbour,
      weight: 1,
      kinds: [b(W.harbourDock, 2), b(W.harbourCrane, 1.5), b(W.fishingHut, 1.5)],
    },
    {
      id: G.ashTowns,
      weight: 3,
      kinds: [b(W.ashHut, 4), b(W.ashHouse, 3), b(W.geothermalWell, 0.4)],
    },
    {
      id: G.powerPlants,
      weight: 2,
      kinds: [b(W.powerPlant, 1.5), b(W.coolingTower, 2), b(W.geothermalWell, 1.5)],
    },
    {
      id: G.mining,
      weight: 2,
      kinds: [b(W.miningOutpost, 3), b(W.slagHeap, 0.8), b(W.heatCollector, 0.5)],
    },
    {
      id: G.lavaWorks,
      weight: 2,
      kinds: [b(W.lavaPump, 3), b(W.heatCollector, 2.5), b(W.miningOutpost, 0.5)],
    },
    {
      id: G.foundries,
      weight: 3,
      kinds: [
        giant(W.smelter, 3),
        giant(W.blastFurnace, 2),
        giant(W.chimneyRow, 2),
        b(W.slagHeap, 1),
      ],
    },
    {
      id: G.railYards,
      weight: 2,
      kinds: [b(W.gantryCrane, 2), b(W.slagHeap, 2), giant(W.chimneyRow, 0.5)],
    },
    {
      id: G.warFactory,
      weight: 2,
      kinds: [giant(W.hangar, 3), giant(W.launchPad, 2), b(W.armouredTower, 2)],
    },
    {
      id: G.fortressCity,
      weight: 2,
      kinds: [giant(W.fortressBlock, 4), b(W.armouredTower, 2), giant(W.hangar, 0.5)],
    },
  ],
  trees: [
    tree(W.hardyGrass, 6, 2.8, [0.5, 0.8]),
    tree(W.burntTree, 4, 2.7),
    tree(W.burntStump, 3, 3.5),
    tree(W.lavaBoulder, 2.5, 3.9, [0.5, 1]),
    tree(W.smokingVent, 0.4, 5.1, [0.6, 1]),
    tree(W.sulphurVent, 0.6, 3.4, [0.5, 0.9]),
    tree(W.hotSpring, 0.3, 4.8, [0.6, 0.8]),
    { id: W.ashHut, weight: 0.15, footprint: 4.6, scale: [0.5, 0.65] },
  ],
  treesPerCell: 8,
  cars: CAR_RULES,
  loners: { cell: 150, chance: 0.15, clearance: 18 },
  hamlets: { spacing: [700, 1400], buildings: [5, 9], radius: 32, gap: 2, clearance: 18 },
  floating: VOLCANIC_FLOATING,
};

// Lines of World 4 (P10-R08): the geothermal pipeline of 4-2, and the rail lines of 4-4 with ore
// wagons running to and fro on them. Pieces are laid along X, every `spacing` along the path; a
// level declares them in its `props.lines`, with a gentle path (an amplitude under about a
// fiftieth of the wavelength, since wagons drift straight along the level) and the sections
// they run through, e.g.
//
// ```ts
// const YARD_PATH = { x: -90, amplitude: 40, wavelength: 3000 };
// props: {
//   ...VOLCANIC_PROPS,
//   lines: [pipelineLine(PIPE_PATH, ['ash plain']), ...railWithWagons(YARD_PATH, ['forge'])],
// }
// ```

/** Length of a pipeline or rail track piece: their models span x = -7.5 to 7.5. */
export const LINE_PIECE_LENGTH = 15;
/** Ore wagons stand on every third track piece, and run up to 10 either way in 18 s. */
export const ORE_WAGON_SPACING = 3 * LINE_PIECE_LENGTH;
export const ORE_WAGON_DRIFT = { x: 0, z: 10, period: 18 } as const;
/** Radius of ground each pipeline or track piece takes: buildings keep clear of it. */
const LINE_FOOTPRINT = 8;
const LINE_SLOPE = 0.4;

/** The geothermal pipeline along `path` (4-2), in the sections named (all when omitted). */
export function pipelineLine(path: Meander, sections?: readonly string[]): PropLine {
  return {
    kind: W.pipeline,
    path,
    spacing: LINE_PIECE_LENGTH,
    footprint: LINE_FOOTPRINT,
    maxSlope: 0.6,
    ...(sections ? { sections } : {}),
  };
}

/** A rail line along `path` (4-4): track pieces end to end. */
export function railLine(path: Meander, sections?: readonly string[]): PropLine {
  return {
    kind: W.railLine,
    path,
    spacing: LINE_PIECE_LENGTH,
    footprint: LINE_FOOTPRINT,
    maxSlope: LINE_SLOPE,
    ...(sections ? { sections } : {}),
  };
}

/**
 * Ore wagons on the rail line of the same `path` and `sections`: one on every third track piece
 * (same footprint and slope test, so a wagon stands only where its track does), all running to
 * and fro together along the level.
 */
export function oreWagonLine(path: Meander, sections?: readonly string[]): PropLine {
  return {
    ...railLine(path, sections),
    kind: W.oreWagon,
    spacing: ORE_WAGON_SPACING,
    drift: ORE_WAGON_DRIFT,
  };
}

/** A rail line and its ore wagons along `path`: the two lines to put in a level's `lines`. */
export function railWithWagons(path: Meander, sections?: readonly string[]): readonly PropLine[] {
  return [railLine(path, sections), oreWagonLine(path, sections)];
}

/** Roads of World 4: as in World 1 (no crossings, D-046); the looks make them dark and cracked. */
export const WORLD_4_ROADS: RoadRules = WORLD_1_ROADS;
