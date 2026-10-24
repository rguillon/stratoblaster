import { describe, expect, it } from 'vitest';
import {
  closestTarget,
  damageTarget,
  isAlive,
  type ShotTarget,
} from '../../../../src/core/entities/shot-target';

function target(id: number, x: number, y: number, health = 10): ShotTarget {
  return { id, x, y, radius: 5, health, maxHealth: 10 };
}

describe('shot targets', () => {
  it('takes damage down to 0 and reports the damage actually dealt', () => {
    const t = target(1, 0, 0);
    expect(damageTarget(t, 4)).toBe(4);
    expect(t.health).toBe(6);
    expect(damageTarget(t, 100)).toBe(6);
    expect(t.health).toBe(0);
    expect(isAlive(t)).toBe(false);
    expect(damageTarget(t, -3)).toBe(0);
  });

  it('finds the closest living target', () => {
    const near = target(1, 3, 0, 0);
    const far = target(2, 10, 0);
    const mid = target(3, 0, 6);
    expect(closestTarget([near, far, mid], 0, 0)).toBe(mid);
    expect(closestTarget([near], 0, 0)).toBeUndefined();
    expect(closestTarget([near, far, mid], 0, 0, 1)).toBeUndefined();
  });
});
