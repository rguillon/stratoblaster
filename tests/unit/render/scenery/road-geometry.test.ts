import { describe, expect, it } from 'vitest';
import type { Road } from '../../../../src/core/scenery/road-network';
import { buildRoadGeometry } from '../../../../src/render/scenery/road-geometry';

const LOOK = {
  main: [0.1, 0.1, 0.1],
  cross: [0.5, 0.4, 0.3],
  opacity: { main: 0.8, cross: 0.6 },
  shoulder: 1,
  streetShoulder: 0.5,
  wear: 0,
  lift: 0.5,
} as const;
const point = (x: number, z: number, width = 4) => ({ x, z, width });

const ROAD: Road = {
  index: 0,
  kind: 'main',
  width: 4,
  lanes: 1,
  // Wider at its start, like a path at its junction.
  points: [point(0, 0, 8), point(0, 10), point(0, 20), point(0, 30), point(0, 40)],
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
    // 5 points, 4 vertices each (2 shoulders, 2 road edges), and 3 quads per segment.
    expect(geo.positions.length / 3).toBe(20);
    expect(geo.indices).toHaveLength(4 * 3 * 6);
    const xs = (point: number) => [0, 1, 2, 3].map((k) => geo.positions[(point * 4 + k) * 3]);
    // The first point is 8 wide, the others 4, with a shoulder of 1 on each side.
    expect(xs(0)).toEqual([-5, -4, 4, 5]);
    expect(xs(1)).toEqual([-3, -2, 2, 3]);
    // Height of the ground (here = x) plus the lift.
    const ys = [0, 1, 2, 3].map((k) => geo.positions[k * 3 + 1]);
    expect(ys).toEqual([-4.5, -3.5, 4.5, 5.5]);
    expect(upwardY(geo.positions, geo.indices)).toBeGreaterThan(0);
  });

  it('P04 review: the road surface is see-through and its shoulders fade into the ground', () => {
    const geo = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 100, LOOK);
    const alphas = [0, 1, 2, 3].map((k) => geo.colors[k * 4 + 3]);
    expect(alphas).toEqual([0, 0.8, 0.8, 0]);
    expect(geo.colors.slice(4, 7)).toEqual([0.1, 0.1, 0.1]);
    const worn = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 100, { ...LOOK, wear: 0.5 });
    const reds = new Set(worn.colors.filter((_, i) => i % 4 === 0).map((v) => v.toFixed(4)));
    expect(reds.size).toBeGreaterThan(1);
    for (let i = 3; i < worn.colors.length; i += 4) {
      expect(worn.colors[i]).toBeLessThanOrEqual(0.8);
    }
  });

  it('P04-R07: draws only the segments that start in the chunk, so chunks share none', () => {
    const first = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 15, LOOK);
    const second = buildRoadGeometry([ROAD], { height: () => 0 }, 15, 100, LOOK);
    expect(first.indices.length + second.indices.length).toBe(4 * 3 * 6);
    expect(
      buildRoadGeometry(
        [{ ...ROAD, kind: 'cross' }],
        { height: () => 0 },
        0,
        100,
        LOOK,
      ).colors.slice(4, 8),
    ).toEqual([0.5, 0.4, 0.3, 0.6]);
  });

  it('P04 review: a street goes on past its ends by half its width, with a narrow shoulder', () => {
    const street: Road = {
      index: 1,
      kind: 'street',
      width: 6,
      lanes: 1,
      points: [point(0, 0, 6), point(0, 10, 6)],
    };
    const geo = buildRoadGeometry([street], { height: () => 0 }, -100, 100, LOOK);
    const zs = geo.positions.filter((_, i) => i % 3 === 2);
    expect(Math.min(...zs)).toBeCloseTo(-3);
    expect(Math.max(...zs)).toBeCloseTo(13);
    const xs = geo.positions.filter((_, i) => i % 3 === 0);
    expect(Math.max(...xs)).toBeCloseTo(3.5);
  });
});

describe('centre lines', () => {
  const LINED = {
    ...LOOK,
    centreLine: { color: [1, 1, 0], laneColor: [1, 1, 1], width: 0.5, dash: 4, lift: 0.05 },
  } as const;
  const yellow = (colors: readonly number[]) =>
    colors.filter((_, i) => i % 4 === 0).filter((_, k) => colors[k * 4 + 2] === 0).length;

  it('P04 review: streets get a solid yellow line that stops where another street crosses', () => {
    const across: Road = {
      index: 1,
      kind: 'street',
      width: 6,
      lanes: 1,
      points: [point(-40, 20, 6), point(40, 20, 6)],
    };
    const along: Road = {
      index: 2,
      kind: 'street',
      width: 6,
      lanes: 1,
      points: [point(0, 0, 6), point(0, 40, 6)],
    };
    const geo = buildRoadGeometry([along, across], { height: () => 0 }, -100, 100, LINED);
    const lineZs = geo.positions
      .filter((_, i) => i % 3 === 2)
      .filter((_, v) => geo.colors[v * 4 + 2] === 0 && Math.abs(geo.positions[v * 3] ?? 9) < 1);
    expect(lineZs.length).toBeGreaterThan(0);
    // Nothing of the line of `along` within the crossing street (Z 17..23).
    expect(lineZs.every((z) => z <= 17 || z >= 23)).toBe(true);
    // Painted above the road surface.
    const ys = geo.positions.filter((_, i) => i % 3 === 1);
    expect(Math.max(...ys)).toBeCloseTo(LOOK.lift + 0.05);
  });

  it('P04 review: main roads get a dashed line, paths none', () => {
    const lined = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 100, LINED);
    const plain = buildRoadGeometry([ROAD], { height: () => 0 }, 0, 100, LOOK);
    const quads = (lined.indices.length - plain.indices.length) / 6;
    // 40 long in pieces of 2: half of them in dashes of 4.
    expect(quads).toBe(10);
    expect(yellow(lined.colors)).toBeGreaterThan(0);
    const path = buildRoadGeometry(
      [{ ...ROAD, kind: 'cross' }],
      { height: () => 0 },
      0,
      100,
      LINED,
    );
    expect(path.indices).toHaveLength(4 * 3 * 6);
  });

  it('P04 review: 2×2 roads get a double yellow line and white dashed lines between lanes', () => {
    const dual: Road = {
      ...ROAD,
      width: 12,
      lanes: 2,
      points: ROAD.points.map((p) => ({ ...p, width: 12 })),
    };
    const geo = buildRoadGeometry([dual], { height: () => 0 }, 0, 100, LINED);
    const plain = buildRoadGeometry([dual], { height: () => 0 }, 0, 100, LOOK);
    const marks = geo.positions.length / 3 - plain.positions.length / 3;
    const xs = Array.from(
      { length: marks },
      (_, k) => geo.positions[(plain.positions.length / 3 + k) * 3] ?? 0,
    );
    // Centre lines around ±0.5, lane lines around ±3.
    expect(xs.some((x) => Math.abs(Math.abs(x) - 0.5) <= 0.25)).toBe(true);
    expect(xs.some((x) => Math.abs(Math.abs(x) - 3) <= 0.25)).toBe(true);
    const white = geo.colors.filter((_, i) => i % 4 === 2).filter((b) => b === 1).length;
    expect(white).toBeGreaterThan(0);
  });
});
