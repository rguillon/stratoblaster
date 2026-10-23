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

/** Removes `amount` health, never below 0. Returns the damage actually dealt. */
export function damageTarget(target: ShotTarget, amount: number): number {
  const dealt = Math.min(target.health, Math.max(0, amount));
  target.health -= dealt;
  return dealt;
}

/** The living target closest to (x, y), or undefined if none is alive. */
export function closestTarget(
  targets: readonly ShotTarget[],
  x: number,
  y: number,
): ShotTarget | undefined {
  let best: ShotTarget | undefined;
  let bestDistance = Infinity;
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
