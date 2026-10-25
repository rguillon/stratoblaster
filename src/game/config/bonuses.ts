import type { BonusRules } from '../../core/systems/bonus-world';

/**
 * Weapon bonuses (phase 6 review, GD-31): the chance a destroyed enemy drops one grows with its
 * health: 6 % for the small ones (Gnat to Splitter), a Lancer 12 %, a Rocketeer 15 %, a Bulwark or
 * a Carrier 20 %. A play-through shooting most enemies gets about 8 (1-1) to 23 (1-5), the first
 * within about a minute and a half (D-049). They fall a little slower than the ground scrolls,
 * so there is time to fly over them.
 */
export const BONUS_RULES: BonusRules = {
  chance: { perHealth: 0.0015, min: 0.06, max: 0.2 },
  fallSpeed: 45,
  pickupRadius: 22,
};
