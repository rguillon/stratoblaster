import { describe, expect, it } from 'vitest';
import { Enemy, type EnemyContext } from '../../../../src/core/entities/enemy';
import { createRng } from '../../../../src/core/math/rng';
import { EnemyWorld } from '../../../../src/core/systems/enemy-world';
import { Dropper, Twin } from '../../../fixtures/sample-enemies';

const OPTIONS = { width: 300, height: 400, cullMargin: 30, maxEnemyAge: 20 };
const world = (): EnemyWorld => new EnemyWorld(OPTIONS, createRng(1));

/** An enemy that remembers the player position it was shown, and can fire anything. */
class Watcher extends Enemy {
  seen: [number, number] | undefined;

  constructor(private readonly act?: (ctx: EnemyContext) => void) {
    super(150, 200, { model: 'cube', radius: 10, health: 5, points: 1 });
  }

  override update(ctx: EnemyContext): void {
    this.seen = [ctx.playerX, ctx.playerY];
    this.act?.(ctx);
  }
}

describe('EnemyWorld', () => {
  it('P05: numbers the enemies it is given and updates them every step', () => {
    const w = world();
    const a = new Dropper(100, 300);
    const b = new Dropper(200, 300);
    w.add(a, b);
    expect([a.id, b.id]).toEqual([1, 2]);
    w.step(0.5);
    expect(a.y).toBeCloseTo(250);
    expect(a.age).toBeCloseTo(0.5);
    expect(w.targets).toEqual([a, b]);
  });

  it('GD-44: shows the enemies where the player is', () => {
    const w = world();
    const watcher = new Watcher();
    w.add(watcher);
    w.playerX = 12;
    w.playerY = 34;
    w.step(0.1);
    expect(watcher.seen).toEqual([12, 34]);
  });

  it('GD-50, GD-62: scores destroyed enemies, blows them up and removes them', () => {
    const w = world();
    const enemy = new Dropper(100, 300);
    w.add(enemy);
    enemy.health = 0;
    w.step(0.1);
    expect(w.kills).toBe(1);
    expect(w.score).toBe(7);
    expect(w.blasts).toEqual([{ kind: 'enemy', x: 100, y: 300, radius: 10 }]);
    expect(w.enemies).toHaveLength(0);
    expect(w.targets).toHaveLength(0);
    w.step(0.1);
    expect(w.blasts).toEqual([]);
  });

  it('P05-R10: lets a destroyed enemy spawn its parts, from the next step', () => {
    const w = world();
    const twin = new Twin(100, 300);
    w.add(twin);
    twin.health = 0;
    w.step(0.1);
    expect(w.enemies).toHaveLength(2);
    expect(w.enemies.every((e) => e instanceof Dropper && !(e instanceof Twin))).toBe(true);
    expect(w.enemies.map((e) => e.id)).toEqual([2, 3]);
  });

  it('removes enemies once they have been on the playfield and left it', () => {
    const w = world();
    const above = new Dropper(150, 425);
    w.add(above);
    w.step(0.01);
    expect(w.enemies).toHaveLength(1);
    const leaving = new Dropper(150, 5);
    w.add(leaving);
    w.step(0.01);
    expect(w.enemies).toContain(leaving);
    w.step(0.4);
    expect(w.enemies).not.toContain(leaving);
  });

  it('removes enemies that are too old, whatever they do', () => {
    const w = world();
    const watcher = new Watcher();
    w.add(watcher);
    w.step(OPTIONS.maxEnemyAge + 1);
    expect(w.enemies).toHaveLength(0);
  });

  it('GD-43: moves the enemy shots, and lists missiles as targets', () => {
    const w = world();
    const missile = {
      speed: 10,
      turnRateDeg: 0,
      homingSeconds: 0,
      radius: 3,
      health: 4,
      style: 'm',
    };
    let fired = false;
    const gunner = new Watcher((ctx) => {
      if (fired) return;
      fired = true;
      ctx.fireBullet(150, 200, Math.PI, { speed: 100, radius: 2, style: 'b' });
      ctx.fireMissile(150, 200, Math.PI, missile);
    });
    w.add(gunner);
    w.step(0.1);
    expect(w.shots.bullets[0]?.y).toBeCloseTo(190);
    expect(w.targets).toHaveLength(2);
    expect(w.targets[1]).toBe(w.shots.missiles[0]);
  });

  it('GD-62: blows up the missiles the player shot down', () => {
    const w = world();
    w.shots.fireMissile(50, 60, 0, {
      speed: 0,
      turnRateDeg: 0,
      homingSeconds: 0,
      radius: 3,
      health: 4,
      style: 'm',
    });
    const [missile] = w.shots.missiles;
    if (missile) missile.health = 0;
    w.step(0.1);
    expect(w.blasts).toEqual([{ kind: 'missile', x: 50, y: 60, radius: 3 }]);
    expect(missile?.alive).toBe(false);
  });

  it('P05-R07: passes lasers to the shots', () => {
    const w = world();
    const lancer = new Watcher((ctx) => {
      if (ctx.width > 0 && w.shots.lasers.length === 0) {
        ctx.fireLaser(lancer, { warningSeconds: 1, firingSeconds: 1, width: 4, style: 'l' });
      }
    });
    w.add(lancer);
    w.step(0.1);
    expect(w.shots.lasers).toHaveLength(1);
  });

  it('clears everything', () => {
    const w = world();
    w.add(new Dropper(1, 1));
    w.shots.fireBullet(0, 0, 0, { speed: 1, radius: 1, style: 'b' });
    w.clear();
    expect(w.enemies).toHaveLength(0);
    expect(w.targets).toHaveLength(0);
    expect(w.shots.count).toBe(0);
  });
});
