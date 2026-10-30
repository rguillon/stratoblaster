/** Something shots can hit: a circle with health. Positions in logical pixels, Y up. */
export interface ShotTarget {
  readonly id: number;
  x: number;
  y: number;
  readonly radius: number;
  health: number;
  readonly maxHealth: number;
}

/** Whether the target can still be hit. */
export function isAlive(target: ShotTarget): boolean {
  return target.health > 0;
}

/**
 * Removes `amount` health, never below 0. Returns the damage actually dealt: 0 when the target
 * ignores it (a shielded core, P07-R01).
 */
export function damageTarget(target: ShotTarget, amount: number): number {
  const before = target.health;
  target.health = before - Math.min(before, Math.max(0, amount));
  return before - target.health;
}

/** The living target closest to (x, y) and within `range`, or undefined if there is none. */
export function closestTarget(
  targets: readonly ShotTarget[],
  x: number,
  y: number,
  range = Infinity,
): ShotTarget | undefined {
  let best: ShotTarget | undefined;
  let bestDistance = range ** 2;
  for (const target of targets) {
    if (!isAlive(target)) continue;
    const distance = (target.x - x) ** 2 + (target.y - y) ** 2;
    if (distance < bestDistance) {
      best = target;
      bestDistance = distance;
    }
  }
  return best;
}
