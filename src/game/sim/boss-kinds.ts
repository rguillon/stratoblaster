import type { BossKindDefinition } from '../../core/systems/boss-fights';
import type { BossDesign } from '../config/bosses/boss-kit';
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
import { WorldBoss } from './bosses/world-boss';

/**
 * The boss designs, mini and final boss of 1-1, then of 1-2… (P07-R05), then the ten of World 2
 * in the same order (P08-R10).
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
];

/** One boss kind per design. */
export const BOSS_KINDS: readonly BossKindDefinition[] = BOSS_DESIGNS.map((design) => ({
  id: design.id,
  name: design.stats.name,
  spawn: (area) => new WorldBoss(design, area),
}));
