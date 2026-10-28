import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import {
  JUNGLE_VARIANTS,
  PART_FAMILIES,
  POLAR_VARIANTS,
  variantId,
  type PartFamily,
} from '../../config/building-families';
import { CAR_IDS } from '../../config/cars';
import { PROP_IDS } from '../../config/prop-ids';
import { PROP_COLORS as C } from '../../config/prop-look';
import { WORLD_1_PROP_IDS as W } from '../../config/world-1/props';
import { WORLD_2_PROP_IDS as W2 } from '../../config/world-2/props';
import { WORLD_3_PROP_IDS as W3 } from '../../config/world-3/props';
import { buildCar } from './car-props';
import { buildCactus, buildDryBush, buildPalmTree } from './desert-plants';
import { buildBeachHut, buildDesertHome } from './desert-props';
import { buildDomeHome, buildCubeHome } from './home-props';
import { buildFarmhouse, buildGrainSilos, buildGreenhouse } from './farm-props';
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
import {
  buildCanopyCluster,
  buildCanopyCrown,
  buildGiantFern,
  buildJunglePalm,
  buildMangrove,
  buildSwampTree,
} from './jungle-plants';
import { buildCanopyBuilding } from './jungle-city';
import { buildGiantDam } from './jungle-dam';
import {
  buildLogPile,
  buildLonghouse,
  buildRiverDock,
  buildSawmill,
  buildStiltHut,
} from './jungle-homes';
import { buildGunPit, buildNeonGate, buildRuinAntenna } from './jungle-outposts';
import {
  buildCauseway,
  buildRuinShrine,
  buildStepPyramid,
  buildTempleStatue,
} from './jungle-ruins';
import {
  buildBioLab,
  buildDamPowerPlant,
  buildPumpingStation,
  buildSwampPipeline,
} from './jungle-swamp';
import { buildSkyBridgeTowers, buildTreetopPlatform } from './jungle-treetop';
import { buildFishingPlatform, buildLilyPads, buildReeds, buildWaterfall } from './jungle-water';
import { buildFrostedTree, buildSnowPine, buildSnowyBush } from './polar-plants';
import { buildAntennaMast } from './science-props';
import { buildDeadTree, buildForkedTree } from './tree-props';
import { TILE_PROP_MODELS } from './tile-models';
import { ROAD_KIT_MODELS } from './road-kit';

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
  // Reviewer's rework (2026-10-27): the oil fields of World 2.
  // Phase 8: World 2, the Frozen North (P08-R07); no level places them since the rework.
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
  // Phase 9: World 3, the Jungle (P09-R06).
  [W3.canopyCluster]: buildCanopyCluster,
  [W3.canopyCrown]: buildCanopyCrown,
  [W3.junglePalm]: buildJunglePalm,
  [W3.giantFern]: buildGiantFern,
  [W3.mangrove]: buildMangrove,
  [W3.swampTree]: buildSwampTree,
  [W3.reeds]: buildReeds,
  [W3.lilyPads]: buildLilyPads,
  [W3.fishingPlatform]: buildFishingPlatform,
  [W3.stiltHut]: buildStiltHut,
  [W3.longhouse]: buildLonghouse,
  [W3.riverDock]: buildRiverDock,
  [W3.sawmill]: buildSawmill,
  [W3.logPile]: buildLogPile,
  [W3.stepPyramid]: buildStepPyramid,
  [W3.templeStatue]: buildTempleStatue,
  [W3.ruinShrine]: buildRuinShrine,
  [W3.causeway]: buildCauseway,
  [W3.gunPit]: buildGunPit,
  [W3.neonGate]: buildNeonGate,
  [W3.ruinAntenna]: buildRuinAntenna,
  [W3.bioLab]: buildBioLab,
  [W3.swampPipeline]: buildSwampPipeline,
  [W3.pumpingStation]: buildPumpingStation,
  [W3.dam]: buildGiantDam,
  [W3.powerPlant]: buildDamPowerPlant,
  [W3.treetopPlatform]: buildTreetopPlatform,
  [W3.skyBridgeTowers]: buildSkyBridgeTowers,
  [W3.waterfall]: buildWaterfall,
  ...partModels('canopy-tower', JUNGLE_VARIANTS, buildCanopyBuilding),
  ...partModels('canopy-block', JUNGLE_VARIANTS, buildCanopyBuilding),
  // Phase 15: the models made for the grid of tiles.
  ...TILE_PROP_MODELS,
  // Phase 15: the road kit, for the `props/` page (no level places it: its streets are drawn).
  ...ROAD_KIT_MODELS,
  [CAR_IDS.red]: () => buildCar('sedan', C.containerRed),
  [CAR_IDS.blue]: () => buildCar('sedan', C.containerBlue),
  [CAR_IDS.white]: () => buildCar('sedan', C.white),
  [CAR_IDS.grey]: () => buildCar('sedan', C.metal),
  [CAR_IDS.van]: () => buildCar('van', C.white),
  [CAR_IDS.truck]: () => buildCar('truck', C.containerGreen),
};
