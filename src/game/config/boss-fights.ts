import type { BossFightRules } from '../../core/systems/boss-fights';

/**
 * How boss fights go (P07, tunable values): the ground eases to the fight's speed and back over
 * 2 s (`boss_speed_ease`), and the health bar fills up over 1 s (`health_bar_fill`).
 */
export const BOSS_FIGHT_RULES: BossFightRules = { speedEaseSeconds: 2, barFillSeconds: 1 };
