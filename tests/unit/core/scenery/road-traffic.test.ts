import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import { inCrossing, placeCars, streetLines } from '../../../../src/core/scenery/road-traffic';
import type { CarRules } from '../../../../src/core/scenery/scenery-level';

const RULES: CarRules = {
  kinds: ['car'],
  density: 1,
  laneOffset: 1.5,
  lift: 0.5,
  scale: 1,
  length: 2,
};
const AREA = { xMin: -100, xMax: 100, zMin: -100, zMax: 100 };
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
    points: Array.from({ length: steps + 1 }, (_, i) => ({
      x: ax + ((bx - ax) * i) / steps,
      z: az + ((bz - az) * i) / steps,
      width: 6,
    })),
  };
};

describe('road traffic', () => {
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

  it('P04 review: cars stand in a lane of the streets and main roads, facing along them', () => {
    const cars = placeCars([along, across], () => 2, RULES, 1, AREA);
    expect(cars.length).toBeGreaterThan(10);
    for (const car of cars) {
      expect(car.y).toBeCloseTo(2.5);
      const onAlong = Math.abs(Math.abs(car.x) - 1.5) < 1e-6;
      const onAcross = Math.abs(Math.abs(car.z) - 1.5) < 1e-6;
      expect(onAlong || onAcross).toBe(true);
      // Facing along their street.
      const heading = Math.abs(Math.sin(car.rotation));
      expect(heading).toBeCloseTo(onAlong ? 0 : 1);
      // None in the crossing.
      expect(Math.abs(car.x) < 5 && Math.abs(car.z) < 5).toBe(false);
    }
  });

  it('P04 review: no cars on paths, and an area only gets the cars it contains', () => {
    expect(placeCars([line(0, 'cross', [0, -48], [0, 48])], () => 0, RULES, 1, AREA)).toEqual([]);
    const all = placeCars([along], () => 0, RULES, 1, AREA);
    const half = placeCars([along], () => 0, RULES, 1, { ...AREA, zMin: 0 });
    expect(half.length).toBeLessThan(all.length);
    expect(half.every((c) => c.z >= 0)).toBe(true);
    expect(placeCars([along], () => 0, { ...RULES, density: 0 }, 1, AREA)).toEqual([]);
  });
});
