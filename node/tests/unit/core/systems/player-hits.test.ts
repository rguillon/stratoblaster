import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import type { EnemyLaser } from '../../../../src/core/systems/enemy-shots';
import { EnemyWorld } from '../../../../src/core/systems/enemy-world';
import { findPlayerHits } from '../../../../src/core/systems/player-hits';
import type { HullRules } from '../../../../src/core/systems/player-hull';
import { Dropper } from '../../../fixtures/sample-enemies';

const RULES: HullRules = {
  lives: 3,
  invincibleSeconds: 2,
  hitRadius: 5,
  damage: { bullet: 10, missile: 20, laser: 25, collision: 30 },
  ramDamage: 40,
};
const OPTIONS = { width: 300, height: 400, cullMargin: 30, maxEnemyAge: 20 };
const BULLET = { speed: 0, radius: 3, style: 'red' };
const MISSILE = { speed: 0, turnRateDeg: 0, homingSeconds: 0, radius: 4, health: 10, style: 'r' };
const SHIP = { x: 100, y: 100 };

const world = (): EnemyWorld => new EnemyWorld(OPTIONS, createRng(1));

describe('findPlayerHits (phase 6 review)', () => {
  it('GD-21: a bullet hits the small hitbox only, and goes when the hit lands', () => {
    const w = world();
    w.shots.fireBullet(100, 107.5, 0, BULLET);
    w.shots.fireBullet(100, 109, 0, BULLET);
    const hits = findPlayerHits(SHIP, RULES, w, new WeakSet());
    expect(hits.map((h) => [h.kind, h.damage, h.y])).toEqual([['bullet', 10, 107.5]]);
    hits[0]?.land();
    expect(w.shots.bullets.map((b) => b.alive)).toEqual([false, true]);
  });

  it('a missile hit blows the missile up; the most damaging hit comes first', () => {
    const w = world();
    w.shots.fireBullet(100, 100, 0, BULLET);
    w.shots.fireMissile(102, 100, 0, MISSILE);
    const hits = findPlayerHits(SHIP, RULES, w, new WeakSet());
    expect(hits.map((h) => h.kind)).toEqual(['missile', 'bullet']);
    hits[0]?.land();
    expect(w.shots.missiles[0]?.health).toBe(0);
    w.step(0.1);
    expect(w.blasts.map((b) => b.kind)).toEqual(['missile']);
  });

  it('a laser beam hits along its whole line while firing, once per beam', () => {
    const w = world();
    const owner = new Dropper(100, 380);
    w.shots.fireLaser(owner, { warningSeconds: 1, firingSeconds: 2, width: 6, style: 'l' });
    const lasers = new WeakSet<EnemyLaser>();
    expect(findPlayerHits(SHIP, RULES, w, lasers)).toEqual([]);
    w.shots.step(1.1, 0, 0);
    const [hit] = findPlayerHits(SHIP, RULES, w, lasers);
    expect(hit?.kind).toBe('laser');
    expect(findPlayerHits({ x: 109, y: 100 }, RULES, w, lasers)).toEqual([]);
    hit?.land();
    expect(findPlayerHits(SHIP, RULES, w, lasers)).toEqual([]);
  });

  it('ramming an enemy hurts the ship and the enemy', () => {
    const w = world();
    const enemy = new Dropper(100 + 5 + 9, 100);
    w.add(enemy);
    const [hit] = findPlayerHits(SHIP, RULES, w, new WeakSet());
    expect(hit?.kind).toBe('collision');
    expect(hit?.damage).toBe(30);
    const health = enemy.health;
    hit?.land();
    expect(enemy.health).toBe(Math.max(0, health - 40));
  });
});
