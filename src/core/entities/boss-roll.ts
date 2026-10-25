/** How a boss rolls into its sideways moves (see `BossStats.roll`, phase 7 review). */
export interface BossRoll {
  readonly maxDeg: number;
  readonly fullSpeed: number;
  readonly easePerSec: number;
}

/**
 * Its roll after `dt` seconds moving across at `vx` px/s: easing from `roll` towards `rule.maxDeg`
 * at `rule.fullSpeed`, in proportion below it.
 */
export function rollTowards(rule: BossRoll, roll: number, vx: number, dt: number): number {
  const max = (rule.maxDeg * Math.PI) / 180;
  const target = Math.max(-max, Math.min(max, (vx / rule.fullSpeed) * max));
  return roll + (target - roll) * Math.min(1, rule.easePerSec * dt);
}
