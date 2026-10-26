import type {
  Channel,
  Lakes,
  Meander,
  PropLine,
  Relief,
  SceneryLevel,
  TerrainSection,
} from '../../../core/scenery/scenery-level';
import { smooth } from '../world-1/scenery-coast';
import {
  railWithWagons,
  VOLCANIC_SCATTER as SC,
  WORLD_4_GROUPS as G,
  WORLD_4_PROPS,
  WORLD_4_ROADS,
} from './props';
import { SCORCHED_ROCK } from './scenery-islands';

/*
 * The fire levels of World 4 (P10-R03): 4-3, cooled black basalt, cinder cones and a volcano's
 * flank, with more and more lava rivers and pools; 4-4, the foundries, slag rivers running out
 * of them; 4-5, the volcano's slopes, the war factory on the caldera rim, the fortress city and
 * the magma lake filling the caldera. No sea: the liquid at the level (0) is lava (the looks'
 * `sea.lava`), in channels and pools cut below it. Each level's `seconds` add up to 300
 * (P10-R02).
 */

/** The line the lava rivers follow down the levels. */
export const LAVA_PATH: Meander = { x: 0, amplitude: 120, wavelength: 2200 };

/** A lava river cut along `path`, `halfWidth` wide at its bed. */
const lava = (halfWidth: number, wall = 30, path = LAVA_PATH): Channel => ({
  path,
  halfWidth,
  wall,
  floor: -6,
});

/** Pools of lava among the rock, round basins below the lava level. */
const pools = (chance: number, radius: readonly [number, number] = [18, 36]): Lakes => ({
  spacing: 240,
  chance,
  radius,
  level: -4,
  edge: 14,
});

/** Cooled black basalt, broken and cracked. */
const BASALT = smooth(16, 10, 420);

/** Steep cinder cones and the volcano's flank: sharp crests. */
const cones = (base: number, amplitude: number, maxHeight: number): Relief => ({
  base,
  amplitude,
  frequency: 1 / 340,
  octaves: 4,
  style: 'ridged',
  maxHeight,
});

/** Terraces of cooled rock the mining outposts stand on, away from the lava rivers. */
const MINE_PATH: Meander = { x: -150, amplitude: 50, wavelength: 2600 };
const MINE_GROUND = { path: MINE_PATH, halfWidth: 90, edge: 60, height: 20, roughness: 1.5 };

/** Scorched, flattened ground where 4-3 ends and the foundries of 4-4 stand. */
const FORGE_GROUND = smooth(12, 4, 560, 3);

/** The lava delta where 4-3 ends and 4-4 begins. */
const LAVA_DELTA: TerrainSection = {
  name: 'lava delta',
  seconds: 50,
  relief: FORGE_GROUND,
  channel: lava(40),
  lakes: pools(0.4, [24, 44]),
  surface: { paved: 0.1 },
  buildingDensity: 0.6,
  treeDensity: 0.3,
  trees: SC.lavaFields,
  groups: [G.lavaWorks, G.mining],
};

const fields = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: BASALT,
  buildingDensity: 0.8,
  treeDensity: 0.35,
  trees: SC.lavaFields,
  groups: [G.mining, G.lavaWorks],
  ...extra,
});

/** 4-3, Lava fields: from 4-2's scorched rock over the basalt, more and more lava. */
const LAVA_FIELDS: readonly TerrainSection[] = [
  fields('scorched rock', 40, { relief: SCORCHED_ROCK, trees: SC.scorched, groups: [G.mining] }),
  fields('basalt cracks', 50, { lakes: pools(0.2) }),
  fields('first lava', 50, { channel: lava(18, 24), lakes: pools(0.25) }),
  fields('cinder slopes', 55, {
    relief: cones(16, 55, 100),
    flatten: MINE_GROUND,
    channel: lava(28),
    trees: SC.slopes,
    buildingDensity: 0.8,
  }),
  fields('volcano flank', 55, {
    relief: cones(24, 70, 120),
    flatten: MINE_GROUND,
    channel: lava(32),
    lakes: pools(0.3),
    trees: SC.slopes,
    buildingDensity: 0.8,
  }),
  LAVA_DELTA,
];

const forge = (name: string, seconds: number, extra: Partial<TerrainSection>): TerrainSection => ({
  name,
  seconds,
  relief: FORGE_GROUND,
  channel: lava(36),
  lakes: pools(0.35, [22, 40]),
  surface: { paved: 0.45 },
  buildingDensity: 1,
  treeDensity: 0.2,
  trees: SC.scorched,
  groups: [G.foundries, G.railYards],
  ...extra,
});

/** The foot of the volcano where 4-4 ends and 4-5 begins. */
const VOLCANO_FOOT = smooth(20, 10, 500);

/** 4-4, Forge belt: from 4-3's lava delta, foundries all along the level, slag rivers. */
const FORGE_BELT: readonly TerrainSection[] = [
  { ...LAVA_DELTA, seconds: 45, buildingDensity: 0.8, groups: [G.foundries, G.lavaWorks] },
  forge('smelter row', 55, {}),
  forge('blast furnaces', 55, { channel: lava(40) }),
  forge('rail yards', 50, { groups: [G.railYards, G.foundries] }),
  forge('chimney belt', 50, { channel: lava(44) }),
  forge('slag fields', 45, { relief: VOLCANO_FOOT, channel: lava(48), lakes: pools(0.45) }),
];

/** The flat top of the caldera rim, where the war factory stands. */
const RIM_PATH = { x: -110, amplitude: 50, wavelength: 2600 } as const;
const RIM_GROUND = { path: RIM_PATH, halfWidth: 120, edge: 70, height: 30, roughness: 1.5 };
const RIM = cones(30, 60, 110);

/** The magma lake filling the caldera, on the line of the lava rivers. */
const MAGMA_PATH: Meander = { x: 0, amplitude: 40, wavelength: 3000 };

/** 4-5, Caldera: from 4-4's slag fields up the slopes, the rim, the city, the magma lake. */
const CALDERA: readonly TerrainSection[] = [
  {
    name: 'volcano slopes',
    seconds: 45,
    relief: VOLCANO_FOOT,
    channel: lava(48),
    lakes: pools(0.45),
    buildingDensity: 0.4,
    treeDensity: 0.4,
    trees: SC.slopes,
    groups: [G.warFactory],
  },
  {
    name: 'war factory',
    seconds: 60,
    relief: RIM,
    flatten: RIM_GROUND,
    channel: lava(40, 30, { x: 110, amplitude: 50, wavelength: 2600 }),
    lakes: pools(0.3),
    surface: { paved: 0.5 },
    buildingDensity: 0.8,
    treeDensity: 0.3,
    trees: SC.slopes,
    groups: [G.warFactory],
  },
  {
    name: 'caldera rim',
    seconds: 50,
    relief: RIM,
    channel: lava(55),
    buildingDensity: 0.5,
    treeDensity: 0.4,
    trees: SC.lavaFields,
    groups: [G.warFactory, G.fortressCity],
  },
  {
    name: 'fortress city',
    seconds: 55,
    relief: smooth(16, 3, 600, 3),
    channel: lava(70, 40, MAGMA_PATH),
    surface: { paved: 0.6 },
    buildingDensity: 0.9,
    treeDensity: 0.15,
    trees: SC.scorched,
    groups: [G.fortressCity],
  },
  {
    name: 'lake shore',
    seconds: 40,
    relief: smooth(16, 6, 520),
    channel: lava(110, 50, MAGMA_PATH),
    buildingDensity: 0.6,
    treeDensity: 0.2,
    trees: SC.lavaFields,
    groups: [G.fortressCity],
  },
  {
    // The runout of the final fight repeats this section: the lake fills the caldera.
    name: 'magma lake',
    seconds: 50,
    relief: smooth(18, 8, 520),
    channel: { path: MAGMA_PATH, halfWidth: 170, wall: 60, floor: -10 },
    buildingDensity: 0.3,
    treeDensity: 0.2,
    trees: SC.lavaFields,
    groups: [G.fortressCity],
  },
];

/** The rail line of 4-4 through the foundries, and the ore wagons rolling to and fro on it. */
const RAIL_PATH: Meander = { x: -170, amplitude: 40, wavelength: 3200 };
const RAIL_SECTIONS = ['smelter row', 'blast furnaces', 'rail yards', 'chimney belt'];
const RAIL: readonly PropLine[] = railWithWagons(RAIL_PATH, RAIL_SECTIONS);

const level = (
  [id, name, seed]: readonly [string, string, number],
  scrollSpeed: number,
  sections: readonly TerrainSection[],
  props = WORLD_4_PROPS,
) =>
  ({
    id,
    name,
    seed,
    scrollSpeed,
    transition: 420,
    sections,
    sea: { level: 0 },
    roads: WORLD_4_ROADS,
    props,
  }) satisfies SceneryLevel;

/** 4-3 (P10-R03): the lava fields, more and more lava. */
export const LEVEL_4_3: SceneryLevel = level(
  ['world-4-3', '4-3 Lava fields', 4301],
  60,
  LAVA_FIELDS,
);
/** 4-4 (P10-R03): the forge belt, its slag rivers and rail line. */
export const LEVEL_4_4: SceneryLevel = level(
  ['world-4-4', '4-4 Forge belt', 4401],
  55,
  FORGE_BELT,
  {
    ...WORLD_4_PROPS,
    lines: RAIL,
  },
);
/** 4-5 (P10-R03): the caldera, ending on the magma lake. */
export const LEVEL_4_5: SceneryLevel = level(['world-4-5', '4-5 Caldera', 4501], 55, CALDERA);
