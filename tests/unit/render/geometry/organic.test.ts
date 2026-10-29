import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import {
  carapace,
  curve,
  grown,
  membraneWing,
  organ,
  plate,
  ribs,
  segmentStations,
  segmentedBody,
  tendril,
  vein,
} from '../../../../src/render/geometry/organic';
import { SolidBuilder } from '../../../../src/render/geometry/solids';

const C = [0.2, 0.1, 0.1] as const;
const D = [0.1, 0.1, 0.1] as const;

/** The min and max of each axis of a builder's positions. */
function bounds(b: SolidBuilder) {
  const p = b.geometry.positions;
  const axis = (k: number) => {
    const values = p.filter((_, i) => i % 3 === k);
    return [Math.min(...values), Math.max(...values)];
  };
  return { x: axis(0), y: axis(1), z: axis(2) };
}

const triangles = (b: SolidBuilder) => b.geometry.indices.length / 3;

const BODY = { tail: -10, nose: 10, segments: 3, width: 4, bottom: -1, top: 2 };

describe('organic shapes (P16-R02)', () => {
  it('P16-R02: a segmented body bulges at its segments and pinches between them', () => {
    const stations = segmentStations(BODY);
    expect(stations).toHaveLength(7);
    // Closed to points at both ends.
    expect(stations[0]?.[1]).toBe(0);
    expect(stations[6]?.[1]).toBe(0);
    const [waist, bulge] = [stations[2]?.[1] ?? 0, stations[3]?.[1] ?? 0];
    expect(bulge).toBeGreaterThan(waist);
    const b = segmentedBody(new SolidBuilder(), BODY, C);
    const { x, z } = bounds(b);
    expect(z).toEqual([-10, 10]);
    expect(x[1]).toBeLessThanOrEqual(4 + 1e-9);
    expect(triangles(b)).toBeGreaterThan(0);
  });

  it('P16-R02: an open-ended body keeps its ends and caps them', () => {
    const stations = segmentStations({ ...BODY, closed: [false, true] });
    expect(stations[0]?.[1]).toBeGreaterThan(0);
  });

  it('P16-R02: a carapace has seams on every other plate', () => {
    const b = carapace(new SolidBuilder(), BODY, [C, D]);
    const colors = b.geometry.colors;
    expect(colors.some((c, i) => i % 4 === 0 && c === D[0] && colors[i + 1] === D[1])).toBe(true);
    expect(colors).toContain(C[0]);
  });

  it('P16-R02: a tendril tapers to a point along its path', () => {
    const b = tendril(
      new SolidBuilder(),
      [
        [0, 0, 0],
        [0, 0, 5],
        [0, 0, 10],
      ],
      [1, 0],
      4,
      C,
    );
    const { x, z } = bounds(b);
    expect(z[0]).toBeCloseTo(0);
    expect(z[1]).toBeCloseTo(10);
    expect(x[1]).toBeCloseTo(1);
    // 4 quads, 4 triangles at the tip, one cap: 8 + 4 + 2 triangles.
    expect(triangles(b)).toBe(14);
    expect(() => tendril(new SolidBuilder(), [[0, 0, 0]], [1, 1], 4, C)).toThrow();
  });

  it('P16-R02: a curve goes from one end to the other, bowed at its middle', () => {
    const points = curve([0, 0, 0], [10, 0, 0], [0, 4, 0], 4);
    expect(points[0]).toEqual([0, 0, 0]);
    expect(points[4]).toEqual([10, 0, 0]);
    expect(points[2]?.[1]).toBeCloseTo(4);
  });

  it('P16-R02: ribs arch over the back, one per station', () => {
    const one = triangles(
      ribs(new SolidBuilder(), [0], { halfWidth: 3, y: 0, height: 2, thickness: 0.3 }, C),
    );
    const b = ribs(
      new SolidBuilder(),
      [0, 4],
      { halfWidth: 3, y: 0, height: 2, thickness: 0.3 },
      C,
    );
    expect(triangles(b)).toBe(2 * one);
    const { y } = bounds(b);
    expect(y[1]).toBeGreaterThan(2);
  });

  it('P16-R02: an organ is a closed bulb of its size', () => {
    const b = organ(new SolidBuilder(), 2, 6, C, { at: [0, 1, 0] }, 1.5);
    const { x, y } = bounds(b);
    expect(y).toEqual([1, 7]);
    expect(x[1]).toBeCloseTo(2);
  });

  it('P16-R02: a membrane wing spreads between its root and tips, a strut to each tip', () => {
    const [skin, bone] = [new SolidBuilder(), new SolidBuilder()];
    const wing = {
      root: [1, 0],
      tips: [
        [10, -2],
        [8, -8],
        [3, -6],
      ],
      y: 0,
      thickness: 0.2,
      strut: 0.4,
    } as const;
    membraneWing(skin, bone, wing, [C, D]);
    expect(bounds(skin).x).toEqual([1, 10]);
    expect(bone.geometry.positions.length).toBeGreaterThan(0);
    const strutsOfOne = (() => {
      const b = new SolidBuilder();
      membraneWing(new SolidBuilder(), b, { ...wing, tips: [[10, -2]] }, [C, D]);
      return triangles(b);
    })();
    expect(triangles(bone)).toBeCloseTo(3 * strutsOfOne, -1);
  });

  it('P16-R02: a vein is a cheap three-sided tube', () => {
    const b = vein(
      new SolidBuilder(),
      [
        [0, 0, 0],
        [0, 0, 4],
      ],
      0.5,
      C,
    );
    // 3 quads and two caps.
    expect(triangles(b)).toBe(8);
  });

  it('P16-R02: a grafted plate has a rivet at each corner', () => {
    const square = [
      [-2, -2],
      [2, -2],
      [2, 2],
      [-2, 2],
    ] as const;
    const bare = triangles(new SolidBuilder().bevelSlab(square, [0, 0, 1], [0, 0.8], C));
    const b = plate(new SolidBuilder(), square, [0, 1], [C, D]);
    expect(triangles(b)).toBe(bare + 4 * 12);
  });

  it('P16-R02: a grown outline is uneven, and the same for the same seed', () => {
    const square = [
      [-2, -2],
      [2, -2],
      [2, 2],
      [-2, 2],
    ] as const;
    const a = grown(square, 0.5, createRng(3));
    expect(a).toEqual(grown(square, 0.5, createRng(3)));
    expect(a).not.toEqual(square);
    for (const [i, [x, z]] of a.entries()) {
      expect(Math.abs(x - (square[i]?.[0] ?? 0))).toBeLessThanOrEqual(0.5);
      expect(Math.abs(z - (square[i]?.[1] ?? 0))).toBeLessThanOrEqual(0.5);
    }
  });

  it('P16-R02: builders give the same geometry every time', () => {
    const draw = () => segmentedBody(new SolidBuilder(), BODY, C).geometry;
    expect(draw()).toEqual(draw());
  });
});
