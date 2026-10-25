import type { EnemyBindings } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { createBlastRenderer } from './blast-renderer';
import { createEnemyShotRenderer } from './enemy-shot-renderer';
import { ENEMY_MODELS } from './enemy-models';
import { BOSS_MODELS } from '../bosses/boss-models';

/** How this game's enemies (and bosses, P07), their shots and their explosions look (P05). */
export const ENEMY_BINDINGS: EnemyBindings = {
  models: { ...ENEMY_MODELS, ...BOSS_MODELS },
  shots: createEnemyShotRenderer,
  blasts: createBlastRenderer,
  glow: ENEMY_LOOK.glow,
};
