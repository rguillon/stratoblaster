import { describe, expect, it } from 'vitest';
import type { EnemyContext } from '../../../../src/core/entities/enemy';
import { JointedEnemy, type JointedDesign } from '../../../../src/core/entities/jointed-enemy';
import { RecordingContext, run } from '../../../helpers/enemy-context';

const STATS = { model: 'test', radius: 10, health: 100, points: 300 };

/** An arm swinging 30° each way every 2 s, a shield plate, and a drone orbiting the hull. */
const DESIGN: JointedDesign = {
  joints: { shoulder: { x: 10, y: 0, swing: { amplitudeDeg: 30, period: 2 } } },
  parts: [
    { id: 'arm', x: 10, y: -20, radius: 5, health: 30, joint: 'shoulder' },
    { id: 'plate', x: 0, y: -12, radius: 6, health: 20, shields: true },
    { id: 'drone', x: 0, y: 25, radius: 4, health: 10, orbits: true },
  ],
};

/** Fires a bullet along its arm every step while the arm stands. */
class Armed extends JointedEnemy {
  constructor() {
    super(100, 200, STATS, DESIGN);
  }

  protected act(ctx: EnemyContext, dt: number): void {
    this.spin += dt;
    const arm = this.part('arm');
    if (arm) ctx.fireBullet(arm.x, arm.y, arm.heading, { speed: 100, radius: 3, style: 'red' });
  }
}

const part = (enemy: JointedEnemy, id: string) => {
  const found = enemy.parts.find((p) => p.spec.id === id);
  if (!found) throw new Error(id);
  return found;
};

describe('JointedEnemy (P05-R13)', () => {
  it('P05-R13: a part on a joint follows its swing, its shots leaving along it', () => {
    const enemy = new Armed();
    const arm = part(enemy, 'arm');
    // At rest, below its shoulder, pointing down the screen.
    expect([arm.x, arm.y]).toEqual([110, 180]);
    const ctx = new RecordingContext();
    run(enemy, ctx, 0.5); // a quarter swing: turned 30° clockwise on screen
    const a = Math.PI / 6;
    expect(arm.x).toBeCloseTo(110 - 20 * Math.sin(a));
    expect(arm.y).toBeCloseTo(200 - 20 * Math.cos(a));
    expect(arm.heading).toBeCloseTo(Math.PI + a);
    // Muzzles hang on the joint too: the arm's tip moves with it.
    const tip = arm.place([10, -30, 0]);
    expect(tip.x).toBeCloseTo(110 - 30 * Math.sin(a));
    expect(ctx.shots.at(-1)?.heading).toBeCloseTo(Math.PI + a, 1);
  });

  it('P05-R13: an orbiting part turns around the hull with its spin', () => {
    const enemy = new Armed();
    run(enemy, new RecordingContext(), Math.PI / 2, 1 / 1000);
    const drone = part(enemy, 'drone');
    // A quarter turn clockwise: from above the hull to its right.
    expect(drone.x).toBeCloseTo(125, 0);
    expect(drone.y).toBeCloseTo(200, 0);
  });

  it('P05-R13: a destroyed part blows up once and stops its weapon; a shield keeps shots off the hull', () => {
    const enemy = new Armed();
    const ctx = new RecordingContext();
    expect(enemy.shotTargets).not.toContain(enemy);
    part(enemy, 'plate').health = 0;
    expect(enemy.shotTargets).toContain(enemy);
    part(enemy, 'arm').health -= 100;
    run(enemy, ctx, 0.1);
    expect(ctx.broken.map((p) => p.id)).toEqual([part(enemy, 'arm').id, part(enemy, 'plate').id]);
    expect(ctx.shots).toHaveLength(0);
    expect(part(enemy, 'arm').dropChance).toBe(0);
    expect(enemy.hitTargets).toHaveLength(2); // the hull and the drone
    expect(enemy.health).toBe(STATS.health);
  });

  it('P05-R13: the enemy goes with its hull, its remaining parts blowing up with it', () => {
    const enemy = new Armed();
    const ctx = new RecordingContext();
    enemy.health = 0;
    enemy.onDestroyed(ctx);
    expect(ctx.broken).toHaveLength(3);
    expect(enemy.parts.every((p) => p.destroyed)).toBe(true);
    // Part ids never clash with enemy ids (positive).
    expect(enemy.parts.every((p) => p.id < 0)).toBe(true);
  });
});
