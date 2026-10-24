import type { EnemyBindings } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { createBlastRenderer } from './blast-renderer';
import { createEnemyShotRenderer } from './enemy-shot-renderer';
import { ENEMY_MODELS } from './enemy-models';

/** How this game's enemies, their shots and their explosions look (P05). */
export const ENEMY_BINDINGS: EnemyBindings = {
  models: ENEMY_MODELS,
  shots: createEnemyShotRenderer,
  blasts: createBlastRenderer,
  glow: ENEMY_LOOK.glow,
  showcaseScale: ENEMY_LOOK.showcaseScale,
};
