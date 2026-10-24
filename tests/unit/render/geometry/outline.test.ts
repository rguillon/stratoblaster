import { describe, expect, it } from 'vitest';
import { insetOutline, ringAt } from '../../../../src/render/geometry/outline';

describe('ringAt', () => {
  it('wraps indices around the ring in both directions', () => {
    expect(ringAt(['a', 'b', 'c'], 3)).toBe('a');
    expect(ringAt(['a', 'b', 'c'], -1)).toBe('c');
  });

  it('throws on an empty ring', () => {
    expect(() => ringAt([], 0)).toThrow(RangeError);
  });
});

describe('insetOutline', () => {
  it('phase 5 review: moves every side of a counter-clockwise outline inwards', () => {
    const square = [
      [0, 0],
      [4, 0],
      [4, 4],
      [0, 4],
    ] as const;
    const inset = insetOutline(square, 1);
    const expected = [
      [1, 1],
      [3, 1],
      [3, 3],
      [1, 3],
    ];
    inset.forEach(([x, z], i) => {
      expect(x).toBeCloseTo(expected[i]?.[0] ?? NaN);
      expect(z).toBeCloseTo(expected[i]?.[1] ?? NaN);
    });
  });

  it('phase 5 review: a sharp tip moves at most `maxMiter` times the distance', () => {
    const needle = [
      [-1, 0],
      [1, 0],
      [0, 40],
    ] as const;
    const [, , tip] = insetOutline(needle, 0.5, 3);
    expect(tip?.[0]).toBeCloseTo(0);
    expect(40 - (tip?.[1] ?? 0)).toBeCloseTo(1.5);
  });
});
