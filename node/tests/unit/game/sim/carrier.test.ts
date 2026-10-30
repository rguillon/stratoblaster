import { describe, expect, it } from 'vitest';
import { ENEMY_CONFIG as C } from '../../../../src/game/config/enemies';
import { Carrier } from '../../../../src/game/sim/enemies/carrier';
import { Gnat } from '../../../../src/game/sim/enemies/gnat';
import { RecordingContext, run } from '../../../helpers/enemy-context';

describe('P05-R12: Carrier', () => {
  it('P05-R12: descends slowly and never shoots', () => {
    const ctx = new RecordingContext();
    const carrier = new Carrier(240, 640);
    run(carrier, ctx, 4);
    expect(carrier.x).toBe(240);
    expect(carrier.y).toBeCloseTo(640 - 4 * C.carrier.speed);
    expect(ctx.shots).toHaveLength(0);
  });

  it('P05-R12: launches a Gnat from each side port, out sideways then down', () => {
    const ctx = new RecordingContext();
    const carrier = new Carrier(240, 600);
    run(carrier, ctx, C.carrier.firstLaunch + 0.01);
    expect(ctx.spawned).toHaveLength(2 * C.carrier.ports.length);
    for (const gnat of ctx.spawned) {
      expect(gnat).toBeInstanceOf(Gnat);
    }
    // At the ports, on both sides.
    const near = (x: number, y: number): boolean =>
      ctx.spawned.some((g) => Math.hypot(g.x - carrier.x - x, g.y - carrier.y - y) < 1);
    for (const [px, py] of C.carrier.ports) {
      expect(near(px, py), String([px, py])).toBe(true);
      expect(near(-px, py), String([-px, py])).toBe(true);
    }
    const gnats = ctx.spawned as Gnat[];
    const left = gnats.find((g) => g.x < carrier.x);
    const right = gnats.find((g) => g.x > carrier.x);
    if (!left || !right) throw new Error('a Gnat from each side');
    // Each flies away from the Carrier on its own side, then down past the bottom of the screen.
    run(left, ctx, 0.25);
    run(right, ctx, 0.25);
    expect(left.x).toBeLessThan(carrier.x - C.carrier.ports[0][0]);
    expect(right.x).toBeGreaterThan(carrier.x + C.carrier.ports[0][0]);
    expect(right.path.at(right.path.length).y).toBeLessThan(0);
    run(carrier, ctx, C.carrier.launchInterval);
    expect(ctx.spawned).toHaveLength(4 * C.carrier.ports.length);
  });

  it('P05-R12: stops launching in the lower part of the screen', () => {
    const ctx = new RecordingContext();
    const carrier = new Carrier(240, C.carrier.lastLaunchFraction * 640 - 1);
    run(carrier, ctx, 2 * C.carrier.launchInterval);
    expect(ctx.spawned).toHaveLength(0);
    expect(carrier.charge).toBe(0);
  });
});
