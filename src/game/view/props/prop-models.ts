import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import {
  CITY_PODIUMS,
  CITY_VARIANTS,
  INDUSTRIAL_VARIANTS,
  PART_FAMILIES,
  podiumId,
  variantId,
  type PartFamily,
} from '../../config/building-families';
import { PROP_IDS } from '../../config/level-zero';
import { buildCityBuilding, buildCityPodium } from './city-parts';
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
  [PROP_IDS.glassTower]: buildGlassTower,
  [PROP_IDS.officeBlock]: buildOfficeBlock,
  [PROP_IDS.apartmentBlock]: buildApartmentBlock,
  [PROP_IDS.steppedTower]: buildSteppedTower,
  [PROP_IDS.conifer]: buildConifer,
  [PROP_IDS.broadleaf]: buildBroadleafTree,
  [PROP_IDS.bush]: buildBush,
  // Phase 4 review: buildings assembled from parts, one model per variant and family.
  ...partModels('industrial-complex', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('industrial-works', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('industrial-plant', INDUSTRIAL_VARIANTS, buildIndustrialComplex),
  ...partModels('city-building', CITY_VARIANTS, buildCityBuilding),
  ...partModels('city-tower', CITY_VARIANTS, buildCityBuilding),
  ...partModels('city-block', CITY_VARIANTS, buildCityBuilding),
  ...Object.fromEntries(
    Array.from({ length: CITY_PODIUMS }, (_, i) => [podiumId(i + 1), () => buildCityPodium(i + 1)]),
  ),
};
