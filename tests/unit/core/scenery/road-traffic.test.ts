import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import { inCrossing, streetLines } from '../../../../src/core/scenery/road-traffic';

const line = (
  index: number,
  kind: Road['kind'],
  [ax, az]: [number, number],
  [bx, bz]: [number, number],
): Road => {
  const steps = Math.round(Math.hypot(bx - ax, bz - az) / 8);
  return {
    index,
    kind,
    width: 6,
    lanes: 1,
    points: Array.from({ length: steps + 1 }, (_, i) => ({
      x: ax + ((bx - ax) * i) / steps,
      z: az + ((bz - az) * i) / steps,
      width: 6,
    })),
  };
};

describe('street crossings', () => {
  const along = line(0, 'street', [0, -48], [0, 48]);
  const across = line(1, 'street', [-48, 0], [48, 0]);

  it('P04 review: finds the points of a street where another street crosses it', () => {
    const lines = streetLines([along, across, line(2, 'cross', [5, 5], [9, 9])]);
    expect(lines).toHaveLength(2);
    expect(inCrossing(lines, 0, 0, 2, 0)).toBe(true);
    expect(inCrossing(lines, 0, 0, 20, 0)).toBe(false);
    // A street never crosses itself.
    expect(inCrossing(lines, 1, 20, 0, 0)).toBe(false);
  });
});
