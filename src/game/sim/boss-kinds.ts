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
import { WorldBoss } from './bosses/world-boss';

/** The ten World 1 boss designs, mini and final boss of 1-1, then of 1-2… (P07-R05). */
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
];

/** One boss kind per design. */
export const BOSS_KINDS: readonly BossKindDefinition[] = BOSS_DESIGNS.map((design) => ({
  id: design.id,
  name: design.stats.name,
  spawn: (area) => new WorldBoss(design, area),
}));
