import type {
  DropSource,
  Enemy,
  EnemyBulletSpec,
  EnemyContext,
  EnemyLaserSpec,
  EnemyMissileSpec,
  LaserOwner,
} from '../../src/core/entities/enemy';
import { createRng } from '../../src/core/math/rng';

/** A shot an enemy fired, as recorded by {@link RecordingContext}. */
export interface FiredShot {
  readonly kind: 'bullet' | 'missile';
  readonly x: number;
  readonly y: number;
  readonly heading: number;
  readonly spec: EnemyBulletSpec | EnemyMissileSpec;
}

/** An enemy context on a 480×640 playfield that records what enemies do. */
export class RecordingContext implements EnemyContext {
  readonly width = 480;
  readonly height = 640;
  playerX = 240;
  playerY = 90;
  readonly random = createRng(1);
  fireRate = 1;
  readonly shots: FiredShot[] = [];
  readonly lasers: { owner: LaserOwner; spec: EnemyLaserSpec }[] = [];
  readonly spawned: Enemy[] = [];
  readonly blasts: { x: number; y: number; radius: number }[] = [];
  readonly broken: DropSource[] = [];

  fireBullet(x: number, y: number, heading: number, spec: EnemyBulletSpec): void {
    this.shots.push({ kind: 'bullet', x, y, heading, spec });
  }

  fireMissile(x: number, y: number, heading: number, spec: EnemyMissileSpec): void {
    this.shots.push({ kind: 'missile', x, y, heading, spec });
  }

  fireLaser(owner: LaserOwner, spec: EnemyLaserSpec): void {
    this.lasers.push({ owner, spec });
  }

  spawn(enemy: Enemy): void {
    this.spawned.push(enemy);
  }

  explode(x: number, y: number, radius: number): void {
    this.blasts.push({ x, y, radius });
  }

  breakPart(part: DropSource): void {
    this.broken.push(part);
  }
}

/** Steps `enemy` for `seconds` at 60 Hz (advancing its age, as the world does). */
export function run(enemy: Enemy, ctx: EnemyContext, seconds: number, dt = 1 / 60): void {
  for (let t = 0; t < seconds - 1e-9; t += dt) {
    enemy.age += dt;
    enemy.update(ctx, dt);
  }
}

/** Steps `enemy` until `done` holds (at most `maxSeconds`); returns the seconds it took. */
export function runUntil(
  enemy: Enemy,
  ctx: EnemyContext,
  done: () => boolean,
  maxSeconds = 30,
  dt = 1 / 60,
): number {
  let t = 0;
  while (!done() && t < maxSeconds) {
    enemy.age += dt;
    enemy.update(ctx, dt);
    t += dt;
  }
  return t;
}
