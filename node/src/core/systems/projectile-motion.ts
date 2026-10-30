import { closestTarget, type ShotTarget } from '../entities/shot-target';
import type { ProjectileWeaponDefinition } from '../entities/weapon';

const DEG = Math.PI / 180;

/** A shot in flight. Heading in radians from forward (+Y), positive to the right. */
export interface Projectile {
  alive: boolean;
  weapon: ProjectileWeaponDefinition;
  x: number;
  y: number;
  heading: number;
  speed: number;
  /** Seconds since launch. */
  age: number;
}

/** Wraps an angle into (-π, π]. */
export function wrapAngle(angle: number): number {
  const wrapped = angle - 2 * Math.PI * Math.floor((angle + Math.PI) / (2 * Math.PI));
  return wrapped === -Math.PI ? Math.PI : wrapped;
}

/** Heading (from +Y, positive to the right) of the direction from (x, y) to (tx, ty). */
export function headingTo(x: number, y: number, tx: number, ty: number): number {
  return Math.atan2(tx - x, ty - y);
}

/** Turns `heading` towards `desired` by at most `maxTurn` radians. */
export function turnTowards(heading: number, desired: number, maxTurn: number): number {
  const delta = wrapAngle(desired - heading);
  if (Math.abs(delta) <= maxTurn) return desired;
  return wrapAngle(heading + Math.sign(delta) * maxTurn);
}

/**
 * Advances a projectile by `dt` (P03-R01, P03-R03): homes on the living target closest to it,
 * within its weapon's homing range
 * (re-chosen every step) if its weapon homes, accelerates up to the speed cap, then moves
 * along its heading.
 */
export function advanceProjectile(
  shot: Projectile,
  targets: readonly ShotTarget[],
  dt: number,
): void {
  const { weapon } = shot;
  if (weapon.homingTurnRateDeg > 0) {
    const target = closestTarget(targets, shot.x, shot.y, weapon.homingRange);
    if (target) {
      const desired = headingTo(shot.x, shot.y, target.x, target.y);
      shot.heading = turnTowards(shot.heading, desired, weapon.homingTurnRateDeg * DEG * dt);
    }
  }
  if (weapon.acceleration > 0) {
    shot.speed = Math.min(weapon.maxSpeed, shot.speed + weapon.acceleration * dt);
  }
  shot.x += Math.sin(shot.heading) * shot.speed * dt;
  shot.y += Math.cos(shot.heading) * shot.speed * dt;
  shot.age += dt;
}
