import type { EnemyModelFactory } from '../../../render/game-view';
import {
  buildBulwark,
  buildLancer,
  buildRocketeer,
  buildSpinner,
  buildSplitter,
  buildSplitterPod,
} from './heavy-enemy-models';
import {
  buildGnat,
  buildHornet,
  buildScout,
  buildStrafer,
  buildWeaver,
} from './small-enemy-models';

/** One model per enemy model key (`EnemyStats.model`, P05-R01..R10). */
export const ENEMY_MODELS: Readonly<Record<string, EnemyModelFactory>> = {
  gnat: buildGnat,
  hornet: buildHornet,
  scout: buildScout,
  strafer: buildStrafer,
  weaver: buildWeaver,
  spinner: buildSpinner,
  lancer: buildLancer,
  rocketeer: buildRocketeer,
  bulwark: buildBulwark,
  splitter: buildSplitter,
  'splitter-pod': buildSplitterPod,
};
