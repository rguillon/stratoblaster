import type { EnemyModelFactory } from '../../../render/game-view';
import { buildHive } from './elite-hive-model';
import { buildHydra } from './elite-hydra-model';
import { buildJuggernaut } from './elite-juggernaut-model';
import { buildOrbiter } from './elite-orbiter-model';
import { buildScissor } from './elite-scissor-model';

/** One model per elite model key (P05-R19 to P05-R23). */
export const ELITE_MODELS: Readonly<Record<string, EnemyModelFactory>> = {
  hydra: buildHydra,
  orbiter: buildOrbiter,
  scissor: buildScissor,
  juggernaut: buildJuggernaut,
  hive: buildHive,
};
