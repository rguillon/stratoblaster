import type { PropGeometry, PropModelFactory } from '../../../render/scenery/scenery-look';
import {
  BUILDING_MARGIN,
  TILE,
  TILE_MODELS,
  type TileArchetype,
  type TileModel,
} from '../../config/tile-buildings';
import {
  buildCarPark,
  buildMidrise,
  buildOffice,
  buildPark,
  buildPlaza,
  buildSkyscraper,
  buildTower,
  buildYard,
} from './tile-city';
import {
  buildAdobe,
  buildBarn,
  buildCottage,
  buildCourtyard,
  buildFarmhouse,
  buildFlats,
  buildGreenhouse,
  buildHouse,
  buildTerrace,
  buildVilla,
  buildWorkshop,
} from './tile-homes';
import { geometryOf, tileKit, type TileKit } from './tile-kit';
import {
  buildContainers,
  buildCoolingTower,
  buildDepot,
  buildDockCrane,
  buildFactory,
  buildFlare,
  buildFoundry,
  buildHeadframe,
  buildMineWorks,
  buildOilTanks,
  buildOreSilos,
  buildPlant,
  buildPumpjack,
  buildRadio,
  buildRefinery,
  buildSolar,
  buildTanks,
  buildWarehouse,
  buildWaterTower,
} from './tile-works';

// Phase 15 (P15-R07, R09): the models made for the grid of tiles, one per entry of
// `TILE_MODELS`, each built to fill its tiles less the margin.

const BUILDERS: Readonly<Record<TileArchetype, (k: TileKit) => void>> = {
  house: buildHouse,
  villa: buildVilla,
  cottage: buildCottage,
  terrace: buildTerrace,
  flats: buildFlats,
  workshop: buildWorkshop,
  farmhouse: buildFarmhouse,
  greenhouse: buildGreenhouse,
  barn: buildBarn,
  adobe: buildAdobe,
  courtyard: buildCourtyard,
  waterTower: buildWaterTower,
  solar: buildSolar,
  radio: buildRadio,
  depot: buildDepot,
  headframe: buildHeadframe,
  oreSilos: buildOreSilos,
  mineWorks: buildMineWorks,
  pumpjack: buildPumpjack,
  oilTanks: buildOilTanks,
  flare: buildFlare,
  refinery: buildRefinery,
  factory: buildFactory,
  warehouse: buildWarehouse,
  containers: buildContainers,
  coolingTower: buildCoolingTower,
  tanks: buildTanks,
  foundry: buildFoundry,
  plant: buildPlant,
  dockCrane: buildDockCrane,
  midrise: buildMidrise,
  office: buildOffice,
  tower: buildTower,
  skyscraper: buildSkyscraper,
  carPark: buildCarPark,
  yard: buildYard,
  plaza: buildPlaza,
  park: buildPark,
};

/** The geometry of `model`, filling its tiles less {@link BUILDING_MARGIN} each side. */
export function buildTileModel(model: TileModel): PropGeometry {
  const [w, d] = model.tiles;
  const k = tileKit(
    w * TILE.size - 2 * BUILDING_MARGIN,
    d * TILE.size - 2 * BUILDING_MARGIN,
    TILE.size,
    model.seed,
  );
  BUILDERS[model.archetype](k);
  return geometryOf(k);
}

/** The models made for the grid, keyed by id. */
export const TILE_PROP_MODELS: Readonly<Record<string, PropModelFactory>> = Object.fromEntries(
  TILE_MODELS.map((m) => [m.id, () => buildTileModel(m)]),
);
