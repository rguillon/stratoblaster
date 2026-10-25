import type { Enemy, EnemyContext } from '../../../core/entities/enemy';
import { randomIn, type Random } from '../../../core/math/rng';
import { Path, type PathPoint } from '../../../core/systems/enemy-motion';

/** Degrees to radians. */
export const DEG = Math.PI / 180;

/** Straight down the screen, towards the player's side. */
export const DOWN = Math.PI;

/**
 * A repeating timer: {@link tick} returns how many times it went off during `dt` (an attack
 * every `interval` seconds, the first one after `first`).
 */
export class Cadence {
  #left: number;

  constructor(
    private readonly interval: number,
    first = interval,
  ) {
    this.#left = first;
  }

  /** Fraction of the wait done before the next time, 0..1 (for charging lights). */
  get progress(): number {
    return Math.min(1, Math.max(0, 1 - this.#left / this.interval));
  }

  tick(dt: number): number {
    this.#left -= dt;
    let count = 0;
    while (this.#left <= 0) {
      this.#left += this.interval;
      count++;
    }
    return count;
  }
}

/** Whether the enemy's centre is over the playfield (enemies only shoot from there). */
export function onPlayfield(enemy: Enemy, ctx: EnemyContext): boolean {
  return enemy.x >= 0 && enemy.x <= ctx.width && enemy.y >= 0 && enemy.y <= ctx.height;
}

/** Entries keep enemies this far (a fraction of the edge) from the corners. */
const ENTRY_INSET = 0.08;

/** A wave's entry position, kept away from the corners of the playfield. */
export function clampEntry(position: number): number {
  return Math.min(1 - ENTRY_INSET, Math.max(ENTRY_INSET, position));
}

/** Where enemies coming in from the top may be: the width, or `topRange` (`EnemySpawnArea`). */
interface TopArea {
  readonly width: number;
  readonly topRange?: readonly [number, number];
}

/** X at `fraction` (0..1) across the range enemies coming in from the top keep to. */
export function topX(area: TopArea, fraction: number): number {
  const [min, max] = area.topRange ?? [0, area.width];
  return min + (max - min) * fraction;
}

/** A random X at a fraction in `range` across the range enemies coming in from the top keep to. */
export function pickX(random: Random, range: readonly [number, number], area: TopArea): number {
  return topX(area, randomIn(random, range));
}

/**
 * A path given in fractions of the playfield, mirrored left to right if `mirror`. It comes in
 * from the top, so its X fractions are taken across the area's `topRange`.
 */
export function playfieldPath(
  points: readonly (readonly [number, number])[],
  area: TopArea & { readonly height: number },
  mirror: boolean,
): Path {
  return new Path(
    points.map(([x, y]): PathPoint => [topX(area, mirror ? 1 - x : x), y * area.height]),
  );
}
