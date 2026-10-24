import { describe, expect, it } from 'vitest';
import { SolidBuilder } from '../../../../src/render/geometry/solids';
import type { ColoredGeometry } from '../../../../src/render/geometry/gradient-shapes';

type V = [number, number, number];

function vertex(geo: ColoredGeometry, i: number): V {
  return [geo.positions[i * 3] ?? 0, geo.positions[i * 3 + 1] ?? 0, geo.positions[i * 3 + 2] ?? 0];
}

const sub = (p: V, q: V): V => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
const cross = (u: V, v: V): V => [
  u[1] * v[2] - u[2] * v[1],
  u[2] * v[0] - u[0] * v[2],
  u[0] * v[1] - u[1] * v[0],
];

/** Babylon's front-face normal of each triangle: (c - a) × (b - a). */
function normals(geo: ColoredGeometry): V[] {
  const out: V[] = [];
  for (let t = 0; t < geo.indices.length; t += 3) {
    const [a, b, c] = [0, 1, 2].map((k) => vertex(geo, geo.indices[t + k] ?? 0)) as [V, V, V];
    out.push(cross(sub(c, a), sub(b, a)));
  }
  return out;
}

/** Every face points away from `center`. */
function facesOutward(geo: ColoredGeometry, center: V): boolean {
  return normals(geo).every((n, i) => {
    const a = vertex(geo, geo.indices[i * 3] ?? 0);
    return n[0] * (a[0] - center[0]) + n[1] * (a[1] - center[1]) + n[2] * (a[2] - center[2]) > 0;
  });
}

describe('SolidBuilder', () => {
  it('P04-R04: a box stands on its base, flat-shaded, with faces pointing outward', () => {
    const geo = new SolidBuilder().box([4, 2, 6], [1, 0, 0], {}, [0, 1, 0]).geometry;
    expect(geo.positions.length / 3).toBe(24);
    expect(geo.indices).toHaveLength(36);
    const ys = geo.positions.filter((_, i) => i % 3 === 1);
    expect(Math.min(...ys)).toBe(0);
    expect(Math.max(...ys)).toBe(2);
    expect(facesOutward(geo, [0, 1, 0])).toBe(true);
    expect(geo.colors.slice(0, 4)).toEqual([0, 1, 0, 1]);
  });

  it('P04-R04: lathes and cylinders are closed and face outward; rings have no caps', () => {
    const dome = new SolidBuilder().lathe(
      [
        [5, 0],
        [3, 2],
        [0, 3],
      ],
      6,
      [1, 1, 1],
    ).geometry;
    expect(facesOutward(dome, [0, 1, 0])).toBe(true);
    const cylinder = new SolidBuilder().cylinder(2, 4, 8, [1, 1, 1]).geometry;
    expect(facesOutward(cylinder, [0, 2, 0])).toBe(true);
    // 8 sides of 2 triangles, plus two caps of 6 triangles.
    expect(cylinder.indices.length / 3).toBe(8 * 2 + 2 * 6);
    const ring = new SolidBuilder().ring(2, 1, 8, [1, 1, 1]).geometry;
    expect(ring.indices.length / 3).toBe(8 * 2);
    const cone = new SolidBuilder().lathe(
      [
        [0, 0],
        [2, 1],
        [0, 2],
      ],
      5,
      [1, 1, 1],
    ).geometry;
    expect(cone.indices.length / 3).toBe(5 * 2);
  });

  it('places solids: turns, then moves them', () => {
    const geo = new SolidBuilder().box([2, 2, 2], [1, 1, 1], {
      at: [10, 5, 0],
      roll: Math.PI / 2,
    }).geometry;
    const xs = geo.positions.filter((_, i) => i % 3 === 0);
    const ys = geo.positions.filter((_, i) => i % 3 === 1);
    // Rolled a quarter turn around Z, the box lies along -X from its base.
    expect(Math.min(...xs)).toBeCloseTo(8);
    expect(Math.max(...xs)).toBeCloseTo(10);
    expect(Math.min(...ys)).toBeCloseTo(4);
    expect(Math.max(...ys)).toBeCloseTo(6);
    const turned = new SolidBuilder().box([2, 2, 2], [1, 1, 1], { yaw: 1, pitch: 0.5 }).geometry;
    // The box centre (0, 1, 0) turned the same way.
    const centre: V = [Math.sin(1) * Math.sin(0.5), Math.cos(0.5), Math.cos(1) * Math.sin(0.5)];
    expect(facesOutward(turned, centre)).toBe(true);
  });

  it('P05: a slab extrudes an outline of either winding, faces pointing outward', () => {
    const square = [
      [-2, -3],
      [2, -3],
      [2, 3],
      [-2, 3],
    ] as const;
    for (const outline of [square, [...square].reverse()]) {
      const geo = new SolidBuilder().slab(outline, [-1, 1], [1, 1, 1], {}, [0, 0, 1]).geometry;
      // Top and bottom of 2 triangles each, and 4 sides of 2 triangles.
      expect(geo.indices.length / 3).toBe(12);
      expect(facesOutward(geo, [0, 0, 0])).toBe(true);
      const ys = geo.positions.filter((_, i) => i % 3 === 1);
      expect([Math.min(...ys), Math.max(...ys)]).toEqual([-1, 1]);
    }
    // A concave outline (an arrow head) is triangulated: 4 corners, 2 triangles a side.
    const arrow = [
      [0, 4],
      [3, -3],
      [0, -1],
      [-3, -3],
    ] as const;
    const geo = new SolidBuilder().slab(arrow, [0, 1], [1, 1, 1]).geometry;
    expect(geo.indices.length / 3).toBe(2 * 2 + 4 * 2);
  });
});
