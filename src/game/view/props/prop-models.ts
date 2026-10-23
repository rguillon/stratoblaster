import type { PropModelFactory } from '../../../render/scenery/scenery-look';
import { CITY_VARIANTS, INDUSTRIAL_VARIANTS, PROP_IDS, variantId } from '../../config/level-zero';
import { buildCityBuilding } from './city-parts';
import { buildIndustrialComplex } from './industrial-parts';
import { buildDomeHome, buildCubeHome, buildStiltPod } from './home-props';
import {
  buildContainerYard,
  buildCoolingTower,
  buildFactory,
  buildRefinery,
  buildStorageTanks,
  buildWarehouse,
} from './industrial-props';
import {
  buildApartmentBlock,
  buildGlassTower,
  buildOfficeBlock,
  buildSteppedTower,
} from './city-props';
import { buildBroadleafTree, buildBush, buildConifer } from './green-tree-props';
import { buildAntennaMast, buildObservatory, buildRadarDish } from './science-props';
import { buildDeadTree, buildForkedTree } from './tree-props';

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
  [PROP_IDS.glassTower]: buildGlassTower,
  [PROP_IDS.officeBlock]: buildOfficeBlock,
  [PROP_IDS.apartmentBlock]: buildApartmentBlock,
  [PROP_IDS.steppedTower]: buildSteppedTower,
  [PROP_IDS.conifer]: buildConifer,
  [PROP_IDS.broadleaf]: buildBroadleafTree,
  [PROP_IDS.bush]: buildBush,
  // Phase 4 review: buildings assembled from parts, one model per variant.
  ...Object.fromEntries(
    Array.from({ length: INDUSTRIAL_VARIANTS }, (_, i) => [
      variantId('industrial-complex', i + 1),
      () => buildIndustrialComplex(i + 1),
    ]),
  ),
  ...Object.fromEntries(
    Array.from({ length: CITY_VARIANTS }, (_, i) => [
      variantId('city-building', i + 1),
      () => buildCityBuilding(i + 1),
    ]),
  ),
};
