import type { PropModelFactory } from '../../../render/scenery/scenery-look';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/prop-ids';
import { PROP_COLORS as C } from '../../config/prop-look';
import { WORLD_1_PROP_IDS as W } from '../../config/world-1/props';
import { buildCar } from './car-props';
import { buildCactus, buildDryBush, buildPalmTree } from './desert-plants';
import { buildBeachHut, buildDesertHome } from './desert-props';
import { buildDomeHome, buildCubeHome } from './home-props';
import { buildFarmhouse, buildGrainSilos, buildGreenhouse } from './farm-props';
import { buildBroadleafTree, buildBush, buildConifer } from './green-tree-props';
import { buildAntennaMast } from './science-props';
import { buildWindTurbine } from './wind-turbine';
import { buildDeadTree, buildForkedTree } from './tree-props';
import { TILE_PROP_MODELS } from './tile-models';
import { onTiles } from './tile-fit';
import { ROAD_KIT_MODELS } from './road-kit';

/** The hand-made models, before they are fitted to tiles. */
const FREE_MODELS: Readonly<Record<string, PropModelFactory>> = {
  [PROP_IDS.antenna]: buildAntennaMast,
  [PROP_IDS.cubeHome]: buildCubeHome,
  [PROP_IDS.domeHome]: buildDomeHome,
  [PROP_IDS.deadTree]: buildDeadTree,
  [PROP_IDS.forkedTree]: buildForkedTree,
  [PROP_IDS.conifer]: buildConifer,
  [PROP_IDS.broadleaf]: buildBroadleafTree,
  [PROP_IDS.bush]: buildBush,
  // Phase 6: desert and coast homes, outposts and plants.
  [W.desertHome]: buildDesertHome,
  [W.beachHut]: buildBeachHut,
  [W.palm]: buildPalmTree,
  [W.dryBush]: buildDryBush,
  [W.cactus]: buildCactus,
  // Reviewer, 2026-10-26: the farms of World 1's green land.
  [W.farmhouse]: buildFarmhouse,
  [W.greenhouse]: buildGreenhouse,
  [W.grainSilos]: buildGrainSilos,
  [W.windTurbine]: buildWindTurbine,
  [CAR_IDS.red]: () => buildCar('sedan', C.containerRed),
  [CAR_IDS.blue]: () => buildCar('sedan', C.containerBlue),
  [CAR_IDS.white]: () => buildCar('sedan', C.white),
  [CAR_IDS.grey]: () => buildCar('sedan', C.metal),
  [CAR_IDS.van]: () => buildCar('van', C.white),
  [CAR_IDS.truck]: () => buildCar('truck', C.containerGreen),
};

/**
 * One model per prop kind of this game, keyed by its id (P04-R04). Phase 15: every model has a
 * footprint of whole tiles (reviewer, 2026-10-28); those made for the grid already do.
 */
export const PROP_MODELS: Readonly<Record<string, PropModelFactory>> = {
  ...onTiles(FREE_MODELS),
  ...TILE_PROP_MODELS,
  // The road kit, for the `props/` page (no level places it: its streets are drawn).
  ...ROAD_KIT_MODELS,
};
