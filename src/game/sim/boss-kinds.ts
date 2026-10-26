import type { BossKindDefinition } from '../../core/systems/boss-fights';
import { withOwnLasers, type BossDesign } from '../config/bosses/boss-kit';
import {
  GULL_MOTHERSHIP,
  MESA_FORTRESS,
  OVERLORD,
  REFINERY_TITAN,
  STORM_PETREL,
} from '../config/bosses/final-bosses';
import {
  BREAKWATER,
  DUST_DEVIL,
  REEF_WARDEN,
  SCORPION,
  SENTINEL,
} from '../config/bosses/mini-bosses';
import { FLOE_BREAKER } from '../config/bosses/world-2/floe-breaker';
import { NARWHAL } from '../config/bosses/world-2/narwhal';
import { FJORD_LYNX } from '../config/bosses/world-2/fjord-lynx';
import { HARBOUR_KRAKEN } from '../config/bosses/world-2/harbour-kraken';
import { SNOW_OWL } from '../config/bosses/world-2/snow-owl';
import { AURORA_STATION } from '../config/bosses/world-2/aurora-station';
import { AVALANCHE } from '../config/bosses/world-2/avalanche';
import { GLACIER_COLOSSUS } from '../config/bosses/world-2/glacier-colossus';
import { ICE_QUEEN } from '../config/bosses/world-2/ice-queen';
import { BOREAL_CITADEL } from '../config/bosses/world-2/boreal-citadel';
import { MANGROVE_CROC } from '../config/bosses/world-3/mangrove-croc';
import { RIVER_LEVIATHAN } from '../config/bosses/world-3/river-leviathan';
import { TOUCAN } from '../config/bosses/world-3/toucan';
import { CANOPY_SPIDER } from '../config/bosses/world-3/canopy-spider';
import { STONE_IDOL } from '../config/bosses/world-3/stone-idol';
import { SKY_TEMPLE } from '../config/bosses/world-3/sky-temple';
import { MOSQUITO } from '../config/bosses/world-3/mosquito';
import { DAM_BREAKER } from '../config/bosses/world-3/dam-breaker';
import { JAGUAR } from '../config/bosses/world-3/jaguar';
import { VERDANT_CROWN } from '../config/bosses/world-3/verdant-crown';
import { CINDER_CRAB } from '../config/bosses/world-4/cinder-crab';
import { STEAM_DREADNOUGHT } from '../config/bosses/world-4/steam-dreadnought';
import { ASH_WRAITH } from '../config/bosses/world-4/ash-wraith';
import { GEYSER_RIG } from '../config/bosses/world-4/geyser-rig';
import { MAGMA_SALAMANDER } from '../config/bosses/world-4/magma-salamander';
import { OBSIDIAN_GOLEM } from '../config/bosses/world-4/obsidian-golem';
import { FURNACE_DRAKE } from '../config/bosses/world-4/furnace-drake';
import { FOUNDRY_ARK } from '../config/bosses/world-4/foundry-ark';
import { EMBER_HERALD } from '../config/bosses/world-4/ember-herald';
import { CALDERA_THRONE } from '../config/bosses/world-4/caldera-throne';
import { WorldBoss } from './bosses/world-boss';

/**
 * The boss designs, mini and final boss of 1-1, then of 1-2… (P07-R05), then the ten of World 2
 * (P08-R10), the ten of World 3 (P09-R09) and the ten of World 4 (P10-R11) in the same order.
 */
export const BOSS_DESIGNS: readonly BossDesign[] = [
  REEF_WARDEN,
  STORM_PETREL,
  BREAKWATER,
  GULL_MOTHERSHIP,
  DUST_DEVIL,
  MESA_FORTRESS,
  SCORPION,
  REFINERY_TITAN,
  SENTINEL,
  OVERLORD,
  FLOE_BREAKER,
  NARWHAL,
  FJORD_LYNX,
  HARBOUR_KRAKEN,
  SNOW_OWL,
  AURORA_STATION,
  AVALANCHE,
  GLACIER_COLOSSUS,
  ICE_QUEEN,
  BOREAL_CITADEL,
  MANGROVE_CROC,
  RIVER_LEVIATHAN,
  TOUCAN,
  CANOPY_SPIDER,
  STONE_IDOL,
  SKY_TEMPLE,
  MOSQUITO,
  DAM_BREAKER,
  JAGUAR,
  VERDANT_CROWN,
  CINDER_CRAB,
  STEAM_DREADNOUGHT,
  ASH_WRAITH,
  GEYSER_RIG,
  MAGMA_SALAMANDER,
  OBSIDIAN_GOLEM,
  FURNACE_DRAKE,
  FOUNDRY_ARK,
  EMBER_HERALD,
  CALDERA_THRONE,
];

/** One boss kind per design, its lasers in its own colour. */
export const BOSS_KINDS: readonly BossKindDefinition[] = BOSS_DESIGNS.map((design) => {
  const own = withOwnLasers(design);
  return { id: design.id, name: design.stats.name, spawn: (area) => new WorldBoss(own, area) };
});
