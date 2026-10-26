import type { BombRules } from '../../core/systems/player-bombs';

/**
 * The player's bombs (GD-32, P11-R05, D-091): 3 at the start of a level (and after a Continue,
 * and again after a lost life if fewer are left), 5 at most. One deals 100 to every enemy on
 * screen, enough to destroy every World 1 kind up to the Rocketeer (100 HP), clears the enemy
 * shots, and keeps the ship safe for 1 s.
 */
export const BOMB_RULES: BombRules = {
  start: 3,
  max: 5,
  damage: 100,
  seconds: 1,
};
