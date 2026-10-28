import type { HullRules } from '../../core/systems/player-hull';

/**
 * What hurts the player (phase 6 review, GD-20..GD-22): 3 lives at the start (then those kept from
 * the level completed before, reviewer 2026-10-28), as many as life bonuses add, each a full health bar (the
 * ship's `maxHealth`: balanced 100, heavy 140, light 80); 2 s of invincibility after a hit; a
 * hitbox of 5 px around the ship's centre, much smaller than its model (GD-21). Bullets take 10,
 * missiles 20, a laser beam 25 (once per beam), ramming an enemy 30, and the rammed enemy takes
 * 40 (small ones blow up) (D-050).
 */
export const HULL_RULES: HullRules = {
  lives: 3,
  invincibleSeconds: 2,
  hitRadius: 5,
  damage: { bullet: 10, missile: 20, laser: 25, collision: 30 },
  ramDamage: 40,
};
