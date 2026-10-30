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
  const hits: PlayerHit[] = [];
  for (const e of world.enemies) {
    if (e.gone || e.health <= 0) continue;
    // What can be hit of it: the enemy, or a boss's core and parts (P07-R06).
    const body = e.hitTargets.find((t) => t.health > 0 && touches(t, t.radius));
    if (!body) continue;
    hits.push({
      kind: 'collision',
      damage: rules.damage.collision,
      x: body.x,
      y: body.y,
      // A boss takes no ramming damage (P07-R06).
      land: () => {
        if (e.rammable) e.health = Math.max(0, e.health - rules.ramDamage);
      },
    });
  }
  return hits;
}

/**
 * The enemy shots and enemies touching the player's hitbox at (`x`, `y`), the most damaging
 * first (GD-21: a small hitbox). A laser beam counts once: those in `lasersHit` are skipped,
 * and a beam's hit adds it there when it lands. A collision also hurts the enemy rammed, unless
 * it is a boss.
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
