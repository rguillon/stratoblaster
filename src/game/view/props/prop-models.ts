import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import {
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  PART_FAMILIES,
  POLAR_VARIANTS,
  variantId,
  type PartFamily,
} from '../../config/building-families';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/level-zero';
import { PROP_COLORS as C } from '../../config/prop-look';
import { WORLD_1_PROP_IDS as W } from '../../config/world-1/props';
import { WORLD_2_PROP_IDS as W2 } from '../../config/world-2/props';
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
import { buildPolarBuilding } from './polar-city';
import { buildFishStore, buildHarbourCrane, buildLighthouse } from './polar-coast';
import { buildHeatedDome, buildIceHut, buildLongChalet, buildPolarChalet } from './polar-homes';
import { buildIceberg, buildLargeFloe, buildSmallFloe, buildWeatherBuoy } from './polar-ice';
import { buildMiningComplex } from './polar-mine';
import { buildConveyor, buildDrillTower, buildMiningCrane, buildOreSilo } from './polar-mining';
import {
  buildAntennaArray,
  buildPipeline,
  buildRadarDome,
  buildWindTurbine,
} from './polar-outposts';
import { buildFrostedTree, buildSnowPine, buildSnowyBush } from './polar-plants';
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
  // Phase 8: World 2, the Frozen North (P08-R07).
  [W2.snowPine]: buildSnowPine,
  [W2.frostedTree]: buildFrostedTree,
  [W2.snowyBush]: buildSnowyBush,
  [W2.chalet]: buildPolarChalet,
  [W2.longChalet]: buildLongChalet,
  [W2.hut]: buildIceHut,
  [W2.heatedDome]: buildHeatedDome,
  [W2.lighthouse]: buildLighthouse,
  [W2.harbourCrane]: buildHarbourCrane,
  [W2.fishStore]: buildFishStore,
  [W2.radarDome]: buildRadarDome,
  [W2.antennaArray]: buildAntennaArray,
  [W2.windTurbine]: buildWindTurbine,
  [W2.pipeline]: buildPipeline,
  [W2.drillTower]: buildDrillTower,
  [W2.conveyor]: buildConveyor,
  [W2.oreSilo]: buildOreSilo,
  [W2.miningCrane]: buildMiningCrane,
  [W2.floeSmall]: buildSmallFloe,
  [W2.floeLarge]: buildLargeFloe,
  [W2.iceberg]: buildIceberg,
  [W2.weatherBuoy]: buildWeatherBuoy,
  ...partModels('polar-tower', POLAR_VARIANTS, buildPolarBuilding),
  ...partModels('polar-block', POLAR_VARIANTS, buildPolarBuilding),
  ...partModels('mining-complex', POLAR_VARIANTS, buildMiningComplex),
  [CAR_IDS.red]: () => buildCar('sedan', C.containerRed),
  [CAR_IDS.blue]: () => buildCar('sedan', C.containerBlue),
  [CAR_IDS.white]: () => buildCar('sedan', C.white),
  [CAR_IDS.grey]: () => buildCar('sedan', C.metal),
  [CAR_IDS.van]: () => buildCar('van', C.white),
  [CAR_IDS.truck]: () => buildCar('truck', C.containerGreen),
};
