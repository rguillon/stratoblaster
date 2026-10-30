import { describe, expect, it } from 'vitest';
import { buildGradientRect } from '../../../../src/render/geometry/gradient-shapes';
import type { GradientStop } from '../../../../src/render/environment/gradient-cube';

const STOPS: GradientStop[] = [
  { at: 1, color: [1, 1, 1] },
  { at: -1, color: [0, 0, 0] },
];

describe('buildGradientRect', () => {
  it('builds one row of 2 vertices per stop, coloured bottom to top', () => {
    const geo = buildGradientRect(4, 2, STOPS);
    expect(geo.positions).toEqual([-2, -1, 0, 2, -1, 0, -2, 1, 0, 2, 1, 0]);
    expect(geo.colors).toEqual([0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]);
    expect(geo.indices).toEqual([0, 1, 3, 0, 3, 2]);
  });

  it('needs 2 stops', () => {
    expect(() => buildGradientRect(1, 1, [{ at: 0, color: [1, 1, 1] }])).toThrow();
  });
});
