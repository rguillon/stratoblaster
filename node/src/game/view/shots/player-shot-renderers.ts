import type { ShotRendererFactory } from '../../../render/game-view';
import { BULLET, LASER, MISSILE } from '../../config/player-weapons';
import { createBulletRenderer } from './bullet-renderer';
import { createLaserRenderer } from './laser-renderer';
import { createMissileRenderer } from './missile-renderer';

/** Shot renderer of each player weapon, keyed by weapon id. */
export const PLAYER_SHOT_RENDERERS: Readonly<Record<string, ShotRendererFactory>> = {
  [BULLET.id]: createBulletRenderer,
  [LASER.id]: createLaserRenderer,
  [MISSILE.id]: createMissileRenderer,
};
