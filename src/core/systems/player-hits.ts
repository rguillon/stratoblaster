import type { EnemyLaser } from './enemy-shots';
import type { EnemyWorld } from './enemy-world';
import type { HullRules } from './player-hull';

/** What can hit the player. */
export type PlayerHitKind = 'bullet' | 'missile' | 'laser' | 'collision';

/** Something touching the player's hitbox, and what happens to it if the hit counts. */
export interface PlayerHit {
  readonly kind: PlayerHitKind;
  readonly damage: number;
  /** Where it touched, for effects. */
  readonly x: number;
  readonly y: number;
  /** The bullet goes, the missile blows up, the rammed enemy takes damage… */
  readonly land: () => void;
}

/** Distance from (x, y) to the segment from (ax, ay) along `heading` for `length`. */
function beamDistance(x: number, y: number, laser: EnemyLaser): number {
  const [dx, dy] = [Math.sin(laser.heading), Math.cos(laser.heading)];
  const t = Math.max(0, Math.min(laser.length, (x - laser.x) * dx + (y - laser.y) * dy));
  return Math.hypot(x - (laser.x + t * dx), y - (laser.y + t * dy));
}

/** The player's hitbox: whether a circle at `p` of `radius` touches it. */
type Touches = (p: { readonly x: number; readonly y: number }, radius: number) => boolean;

function bulletHits(world: EnemyWorld, rules: HullRules, touches: Touches): PlayerHit[] {
  return world.shots.bullets
    .filter((b) => b.alive && touches(b, b.radius))
    .map((b) => ({
      kind: 'bullet',
      damage: rules.damage.bullet,
      x: b.x,
      y: b.y,
      land: () => (b.alive = false),
    }));
}

function missileHits(world: EnemyWorld, rules: HullRules, touches: Touches): PlayerHit[] {
  return world.shots.missiles
    .filter((m) => m.alive && m.health > 0 && touches(m, m.radius))
    .map((m) => ({
      kind: 'missile',
      damage: rules.damage.missile,
      x: m.x,
      y: m.y,
      // Shot down by the hit: it blows up on the next step.
      land: () => (m.health = 0),
    }));
}

function laserHits(
  world: EnemyWorld,
  rules: HullRules,
  ship: { readonly x: number; readonly y: number },
  lasersHit: WeakSet<EnemyLaser>,
): PlayerHit[] {
  const { x, y } = ship;
  return world.shots.lasers
    .filter(
      (l) =>
        l.phase === 'firing' &&
        !lasersHit.has(l) &&
        beamDistance(x, y, l) <= rules.hitRadius + l.spec.width / 2,
    )
    .map((l) => ({
      kind: 'laser',
      damage: rules.damage.laser,
      x,
      y,
      land: () => lasersHit.add(l),
    }));
}

function collisionHits(world: EnemyWorld, rules: HullRules, touches: Touches): PlayerHit[] {
  return world.enemies
    .filter((e) => !e.gone && e.health > 0 && touches(e, e.radius))
    .map((e) => ({
      kind: 'collision',
      damage: rules.damage.collision,
      x: e.x,
      y: e.y,
      land: () => {
        e.health = Math.max(0, e.health - rules.ramDamage);
      },
    }));
}

/**
 * The enemy shots and enemies touching the player's hitbox at (`x`, `y`), the most damaging
 * first (GD-21: a small hitbox). A laser beam counts once: those in `lasersHit` are skipped,
 * and a beam's hit adds it there when it lands. A collision also hurts the enemy rammed.
 */
export function findPlayerHits(
  ship: { readonly x: number; readonly y: number },
  rules: HullRules,
  world: EnemyWorld,
  lasersHit: WeakSet<EnemyLaser>,
): PlayerHit[] {
  const touches: Touches = (p, radius) =>
    Math.hypot(p.x - ship.x, p.y - ship.y) <= rules.hitRadius + radius;
  return [
    ...bulletHits(world, rules, touches),
    ...missileHits(world, rules, touches),
    ...laserHits(world, rules, ship, lasersHit),
    ...collisionHits(world, rules, touches),
  ].sort((a, b) => b.damage - a.damage);
}
