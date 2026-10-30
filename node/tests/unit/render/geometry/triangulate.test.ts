import { describe, expect, it } from 'vitest';
import { triangulatePolygon } from '../../../../src/render/geometry/triangulate';
import type { OutlinePoint } from '../../../../src/render/geometry/outline';
import { at } from '../../../helpers/at';

function area(
  points: readonly OutlinePoint[],
  [a, b, c]: readonly [number, number, number],
): number {
  const [ax, az] = at(points, a);
  const [bx, bz] = at(points, b);
  const [cx, cz] = at(points, c);
  return ((bx - ax) * (cz - az) - (cx - ax) * (bz - az)) / 2;
}

describe('triangulatePolygon', () => {
  it('splits a convex polygon into n - 2 counter-clockwise triangles', () => {
    const square: OutlinePoint[] = [
      [0, 0],
      [1, 0],
      [1, 1],
      [0, 1],
    ];
    const tris = triangulatePolygon(square);
    expect(tris).toHaveLength(2);
    for (const t of tris) expect(area(square, t)).toBeGreaterThan(0);
  });

  it('handles concave polygons and preserves their area', () => {
    // A "C" shape: concave, not star-shaped around its centroid.
    const c: OutlinePoint[] = [
      [0, 0],
      [3, 0],
      [3, 0.2],
      [0.2, 0.2],
      [0.2, 2.8],
      [3, 2.8],
      [3, 3],
      [0, 3],
    ];
    const tris = triangulatePolygon(c);
    expect(tris).toHaveLength(c.length - 2);
    const total = tris.reduce((sum, t) => sum + area(c, t), 0);
    expect(total).toBeCloseTo(3 * 3 - 2.8 * 2.6);
    for (const t of tris) expect(area(c, t)).toBeGreaterThan(0);
  });

  it('rejects self-intersecting outlines', () => {
    const bowtie: OutlinePoint[] = [
      [0, 0],
      [1, 1],
      [1, 0],
      [0, 1],
    ];
    expect(() => triangulatePolygon(bowtie)).toThrow(/simple polygon/);
  });
});
