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

/** A random X within `range` (fractions of `width`). */
export function pickX(random: Random, range: readonly [number, number], width: number): number {
  return randomIn(random, range) * width;
}

/** A path given in fractions of the playfield, mirrored left to right if `mirror`. */
export function playfieldPath(
  points: readonly (readonly [number, number])[],
  size: { readonly width: number; readonly height: number },
  mirror: boolean,
): Path {
  return new Path(
    points.map(([x, y]): PathPoint => [(mirror ? 1 - x : x) * size.width, y * size.height]),
  );
}
