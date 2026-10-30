import { describe, expect, it } from 'vitest';
import { BossJoints } from '../../../../src/core/entities/boss-joint';

const DEG = Math.PI / 180;

describe('BossJoints (phase 7 review: moving limbs)', () => {
  it('a joint swings either way and back over its period, from its phase', () => {
    const joints = new BossJoints({
      arm: { x: 0, y: 0, swing: { amplitudeDeg: 10, period: 4 } },
      late: { x: 0, y: 0, swing: { amplitudeDeg: 10, period: 4, phase: 0.25 } },
    });
    expect(joints.angle('arm')).toBeCloseTo(0);
    expect(joints.angle('late')).toBeCloseTo(10 * DEG);
    joints.step(1);
    expect(joints.angle('arm')).toBeCloseTo(10 * DEG);
    joints.step(2);
    expect(joints.angle('arm')).toBeCloseTo(-10 * DEG);
    expect(joints.angle('nothing')).toBe(0);
  });

  it('turns what hangs on it around its pivot, clockwise on screen, with the joints above it', () => {
    // A shoulder at the origin, an elbow 10 px to the right, each turned 90° at t = 1 s.
    const joints = new BossJoints({
      shoulder: { x: 0, y: 0, swing: { amplitudeDeg: 90, period: 4 } },
      elbow: { x: 10, y: 0, parent: 'shoulder', swing: { amplitudeDeg: 90, period: 4 } },
    });
    expect(joints.move('elbow', 20, 0)).toEqual([20, 0]);
    joints.step(1);
    // The elbow turns the hand down (clockwise), then the shoulder turns both down again.
    const [x, y] = joints.move('elbow', 20, 0);
    expect(x).toBeCloseTo(-10);
    expect(y).toBeCloseTo(-10);
    const [ex, ey] = joints.move('shoulder', 10, 0);
    expect(ex).toBeCloseTo(0);
    expect(ey).toBeCloseTo(-10);
    expect(joints.move(undefined, 3, 4)).toEqual([3, 4]);
  });

  it('refuses joints or parts hanging on nothing, joints hanging on themselves, orbiting parts', () => {
    const swing = { amplitudeDeg: 5, period: 1 };
    expect(() => new BossJoints({ a: { x: 0, y: 0, parent: 'b', swing } })).toThrow(/no joint/);
    expect(
      () =>
        new BossJoints({
          a: { x: 0, y: 0, parent: 'b', swing },
          b: { x: 0, y: 0, parent: 'a', swing },
        }),
    ).toThrow(/itself/);
    expect(() => new BossJoints({}, [{ id: 'claw', joint: 'wrist' }])).toThrow(/no joint/);
    expect(
      () =>
        new BossJoints({ wrist: { x: 0, y: 0, swing } }, [
          { id: 'c', joint: 'wrist', orbits: true },
        ]),
    ).toThrow(/orbits/);
  });
});
