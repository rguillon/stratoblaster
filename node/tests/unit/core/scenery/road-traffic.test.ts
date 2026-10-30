import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import {
  cachedStreetLines,
  inCrossing,
  meetingWidth,
  roadZSpan,
  streetLines,
} from '../../../../src/core/scenery/road-traffic';

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

describe('street crossings, indexed (P13-R04)', () => {
  // A grid of streets, as in a district: 12 along Z, 12 across, 64 apart.
  const grid: Road[] = [
    ...Array.from({ length: 12 }, (_, i) =>
      line(i, 'street', [i * 64 - 352, -400], [i * 64 - 352, 400]),
    ),
    ...Array.from({ length: 12 }, (_, i) =>
      line(12 + i, 'street', [-400, i * 64 - 352], [400, i * 64 - 352]),
    ),
  ];
  const lines = streetLines(grid);
  const distance = (l: (typeof lines)[number], x: number, z: number): number => {
    const [dx, dz] = [l.bx - l.ax, l.bz - l.az];
    const t = Math.max(
      0,
      Math.min(1, ((x - l.ax) * dx + (z - l.az) * dz) / (dx * dx + dz * dz || 1)),
    );
    return Math.hypot(l.ax + t * dx - x, l.az + t * dz - z);
  };

  it('P13-R04: answers as a check of every street would, at points all over the grid', () => {
    for (let x = -410; x <= 410; x += 7.3) {
      for (let z = -410; z <= 410; z += 5.9) {
        for (const road of [0, 5, 17]) {
          const crossing = lines.some(
            (l) => l.road !== road && distance(l, x, z) < l.width / 2 + 0.5,
          );
          expect(inCrossing(lines, road, x, z, 0.5)).toBe(crossing);
          const widths = lines
            .filter((l) => l.road !== road && distance(l, x, z) < 0.5)
            .map((l) => l.width);
          expect(meetingWidth(lines, road, x, z)).toBe(
            widths.length > 0 ? Math.max(...widths) : undefined,
          );
        }
      }
    }
  });

  it('P13-R04: a margin wider than the index reaches checks every street', () => {
    expect(inCrossing(lines, 0, -352 + 40, 0, 40)).toBe(true);
    expect(inCrossing(lines, 0, -352 + 40, 0, 20)).toBe(false);
  });

  it('P13-R04: the street lines and the Z span of a road are made once', () => {
    expect(cachedStreetLines(grid)).toBe(cachedStreetLines(grid));
    expect(cachedStreetLines(grid)).toEqual(lines);
    const road = grid[0];
    if (!road) throw new Error('no road');
    expect(roadZSpan(road)).toEqual([-400, 400]);
    expect(roadZSpan(road)).toBe(roadZSpan(road));
  });
});
