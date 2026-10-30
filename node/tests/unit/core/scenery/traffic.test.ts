import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import type { CarRules } from '../../../../src/core/scenery/scenery-level';
import { Traffic } from '../../../../src/core/scenery/traffic';

const RULES: CarRules = {
  kinds: ['car'],
  density: 0.5,
  lift: 0.5,
  scale: 1,
  length: 4,
  speed: [10, 20],
};
const AREA = { xMin: -500, xMax: 500, zMin: -500, zMax: 500 };

/** A straight road along Z from 0 to 400, points every 8. */
function road(kind: Road['kind'], width = 6, lanes: 1 | 2 = 1): Road {
  return {
    index: 0,
    kind,
    width,
    lanes,
    points: Array.from({ length: 51 }, (_, i) => ({ x: 0, z: i * 8, width })),
  };
}

describe('Traffic', () => {
  it('P04 review: cars drive in their lane, facing their way, on the road surface', () => {
    const traffic = new Traffic([road('street')], () => 2, RULES, 1);
    expect(traffic.count).toBeGreaterThan(10);
    const cars = traffic.at(3, AREA);
    expect(cars.length).toBeGreaterThan(5);
    for (const car of cars) {
      expect(car.y).toBeCloseTo(2.5);
      expect(Math.abs(car.x)).toBeCloseTo(1.5);
      // Right-hand traffic: on the right (+X) going up Z, on the left coming down.
      expect(Math.cos(car.rotation)).toBeCloseTo(car.x > 0 ? 1 : -1);
    }
  });

  it('P04 review: cars move with time, and those of a lane keep their distance', () => {
    const traffic = new Traffic([road('main')], () => 0, RULES, 2);
    const before = traffic.at(0, AREA).filter((c) => c.x > 0);
    const after = traffic.at(1, AREA).filter((c) => c.x > 0);
    expect(after.map((c) => c.z)).not.toEqual(before.map((c) => c.z));
    const zs = after.map((c) => c.z).sort((a, b) => a - b);
    zs.slice(1).forEach((z, k) => {
      expect(z - (zs[k] ?? 0)).toBeGreaterThanOrEqual(7.9);
    });
  });

  it('P04 review: cars are hidden near the ends of their road, and paths have none', () => {
    const traffic = new Traffic([road('street')], () => 0, RULES, 3);
    for (let t = 0; t < 30; t += 0.5) {
      for (const car of traffic.at(t, AREA)) {
        expect(car.z).toBeGreaterThanOrEqual(RULES.length - 1e-6);
        expect(car.z).toBeLessThanOrEqual(400 - RULES.length + 1e-6);
      }
    }
    expect(new Traffic([road('cross')], () => 0, RULES, 3).count).toBe(0);
  });

  it('P04 review: on 2×2 roads, cars use both lanes each way', () => {
    const traffic = new Traffic([road('main', 12, 2)], () => 0, RULES, 4);
    const offsets = new Set(traffic.at(5, AREA).map((c) => Math.abs(c.x).toFixed(3)));
    expect([...offsets].sort()).toEqual(['1.500', '4.500']);
  });

  it('P04 review: an area only gets the cars inside it', () => {
    const traffic = new Traffic([road('main')], () => 0, RULES, 5);
    const half = traffic.at(2, { ...AREA, zMin: 200 });
    expect(half.length).toBeLessThan(traffic.at(2, AREA).length);
    expect(half.every((c) => c.z >= 200)).toBe(true);
  });

  it('only looks at the roads near an area, and finds the same cars (reviewer, 2026-10-28)', () => {
    // Streets across the level all along it, and long streets along it, over many buckets.
    const across = Array.from({ length: 40 }, (_, i): Road => {
      const z = i * 97 - 300;
      const points = Array.from({ length: 21 }, (_, j) => ({ x: j * 8 - 80, z, width: 6 }));
      return { index: i, kind: 'street', width: 6, lanes: 1, points };
    });
    const along = [-60, 60].map((x, i): Road => {
      const points = Array.from({ length: 401 }, (_, j) => ({ x, z: j * 8 - 200, width: 6 }));
      return { index: 40 + i, kind: 'street', width: 6, lanes: 1, points };
    });
    const traffic = new Traffic([...across, ...along], () => 0, RULES, 6);
    const everywhere = { xMin: -500, xMax: 500, zMin: -Infinity, zMax: Infinity };
    for (const [time, zMin, zMax] of [
      [0, 100, 600],
      [3, -1000, -250],
      [7, 2900, 3500],
      [9, 255, 257],
    ] as const) {
      const area = { ...AREA, zMin, zMax };
      const all = traffic.at(time, everywhere).filter((c) => c.z >= zMin && c.z < zMax);
      expect(traffic.at(time, area), `${String(zMin)}…${String(zMax)}`).toEqual(all);
    }
    expect(traffic.at(0, { ...AREA, zMin: 5000, zMax: 6000 })).toEqual([]);
  });
});
