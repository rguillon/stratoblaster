import type { ModelFactory } from '../../render/game-view';
import { buildBalancedShip } from './balanced-ship';
import { buildHeavyShip } from './heavy-ship';
import { buildLightShip } from './light-ship';

/** Player ship models, keyed by the ids of `PLAYER_SHIPS` (src/game/config/player-ships.ts). */
export const PLAYER_SHIP_MODELS: Readonly<Record<string, ModelFactory>> = {
  balanced: buildBalancedShip,
  heavy: buildHeavyShip,
  light: buildLightShip,
};
