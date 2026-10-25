import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import {
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  PART_FAMILIES,
  variantId,
  type PartFamily,
} from '../../config/building-families';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/level-zero';
import { PROP_COLORS as C } from '../../config/prop-look';
import { WORLD_1_PROP_IDS as W } from '../../config/world-1/props';
import { buildCar } from './car-props';
import { buildCityBuilding } from './city-parts';
import { buildIndustrialComplex } from './industrial-parts';
import { buildCactus, buildDryBush, buildPalmTree } from './desert-plants';
import {
  buildBeachHut,
  buildDesertHome,
  buildMineHeadframe,
  buildSolarFarm,
  buildWaterTower,
  buildWindcatcherHome,
} from './desert-props';
import { buildDomeHome, buildCubeHome, buildStiltPod } from './home-props';
import {
  buildContainerYard,
  buildCoolingTower,
  buildFactory,
  buildRefinery,
  buildStorageTanks,
  buildWarehouse,
} from './industrial-props';
import { buildBroadleafTree, buildBush, buildConifer } from './green-tree-props';
import { buildAntennaMast, buildObservatory, buildRadarDish } from './science-props';
import { buildDeadTree, buildForkedTree } from './tree-props';

/** The `count` variants of a family of buildings made of parts, built by `build`. */
function partModels(
  family: PartFamily,
  count: number,
  build: (seed: number, half: number) => PropGeometry,
): Record<string, PropModelFactory> {
  const half = PART_FAMILIES[family];
  return Object.fromEntries(
    Array.from({ length: count }, (_, i) => [variantId(family, i + 1), () => build(i + 1, half)]),
  );
}

/** One model per prop kind of this game, keyed by its id (P04-R04). */
export const PROP_MODELS: Readonly<Record<string, PropModelFactory>> = {
  [PROP_IDS.factory]: buildFactory,
  [PROP_IDS.tanks]: buildStorageTanks,
  [PROP_IDS.warehouse]: buildWarehouse,
  [PROP_IDS.coolingTower]: buildCoolingTower,
  [PROP_IDS.radar]: buildRadarDish,
  [PROP_IDS.antenna]: buildAntennaMast,
  [PROP_IDS.observatory]: buildObservatory,
  [PROP_IDS.cubeHome]: buildCubeHome,
  [PROP_IDS.domeHome]: buildDomeHome,
  [PROP_IDS.stiltPod]: buildStiltPod,
  [PROP_IDS.deadTree]: buildDeadTree,
  [PROP_IDS.forkedTree]: buildForkedTree,
  [PROP_IDS.containerYard]: buildContainerYard,
  [PROP_IDS.refinery]: buildRefinery,
  [PROP_IDS.conifer]: buildConifer,
  [PROP_IDS.broadleaf]: buildBroadleafTree,
  [PROP_IDS.bush]: buildBush,
  // Phase 4 review: buildings assembled from parts, one model per variant and family.
  ...partModels('industrial-complex', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('industrial-works', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('industrial-plant', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('city-tower', CITY_VARIANTS, buildCityBuilding),
  ...partModels('city-block', CITY_VARIANTS, buildCityBuilding),
  // Phase 6: desert and coast homes, outposts and plants.
  [W.desertHome]: buildDesertHome,
  [W.windcatcherHome]: buildWindcatcherHome,
  [W.waterTower]: buildWaterTower,
  [W.solarFarm]: buildSolarFarm,
  [W.mineHeadframe]: buildMineHeadframe,
  [W.beachHut]: buildBeachHut,
  [W.palm]: buildPalmTree,
  [W.dryBush]: buildDryBush,
  [W.cactus]: buildCactus,
  [CAR_IDS.red]: () => buildCar('sedan', C.containerRed),
  [CAR_IDS.blue]: () => buildCar('sedan', C.containerBlue),
  [CAR_IDS.white]: () => buildCar('sedan', C.white),
  [CAR_IDS.grey]: () => buildCar('sedan', C.metal),
  [CAR_IDS.van]: () => buildCar('van', C.white),
  [CAR_IDS.truck]: () => buildCar('truck', C.containerGreen),
};
