import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import { buildRoadGeometry } from '../../../../src/render/scenery/road-geometry';

const LOOK = { main: [0.1, 0.1, 0.1], cross: [0.5, 0.4, 0.3], lift: 0.5 } as const;
const point = (x: number, z: number, valid = true) => ({ x, z, valid });

const ROAD: Road = {
  index: 0,
  kind: 'main',
  width: 4,
  points: [
    point(0, 0),
    point(0, 10),
    point(0, 20),
    point(0, 30, false),
    point(0, 40),
    point(0, 50),
  ],
};

/** X and Z of vertex `i`. */
function xz(positions: readonly number[], i: number): [number, number] {
  return [positions[i * 3] ?? 0, positions[i * 3 + 2] ?? 0];
}

/** Y of Babylon's front-face normal of the first triangle: (c - a) × (b - a). */
function upwardY(positions: readonly number[], indices: readonly number[]): number {
  const [a, b, c] = [0, 1, 2].map((k) => xz(positions, indices[k] ?? 0)) as [
    [number, number],
    [number, number],
    [number, number],
  ];
  const [ux, uz] = [c[0] - a[0], c[1] - a[1]];
  const [vx, vz] = [b[0] - a[0], b[1] - a[1]];
  return uz * vx - ux * vz;
}

describe('buildRoadGeometry', () => {
  it('P04-R07: drapes a ribbon of the road width on the ground, facing up', () => {
    const geo = buildRoadGeometry([ROAD], { height: (x) => x }, 0, 100, LOOK);
    // Runs 0-10-20 and 40-50: 3 + 2 points, 2 vertices each.
    expect(geo.positions.length / 3).toBe(10);
    expect(geo.indices).toHaveLength((2 + 1) * 6);
    const [x0, y0, , x1, y1] = geo.positions;
    expect([x0, x1].sort()).toEqual([-2, 2]);
    // Height of the ground (here = x) plus the lift.
    expect([y0, y1]).toEqual([(x0 ?? 0) + 0.5, (x1 ?? 0) + 0.5]);
    expect(geo.colors.slice(0, 4)).toEqual([0.1, 0.1, 0.1, 1]);
    expect(upwardY(geo.positions, geo.indices)).toBeGreaterThan(0);
  });

  it('P04-R07: draws only the segments that start in the chunk, so chunks share none', () => {
    const first = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 15, LOOK);
    const second = buildRoadGeometry([ROAD], { height: () => 0 }, 15, 100, LOOK);
    expect(first.indices.length + second.indices.length).toBe(3 * 6);
    expect(
      buildRoadGeometry(
        [{ ...ROAD, kind: 'cross' }],
        { height: () => 0 },
        0,
        100,
        LOOK,
      ).colors.slice(0, 3),
    ).toEqual([0.5, 0.4, 0.3]);
  });
});
