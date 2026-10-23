import { describe, expect, it } from 'vitest';
import { buildGlowBar, buildGlowDisc } from '../../../../src/game/view/shot-geometry';

const WHITE = [1, 1, 1] as const;
const BLACK = [0, 0, 0] as const;

describe('buildGlowDisc', () => {
  it('P03-R01: a bright centre fading to a black rim of radius 1', () => {
    const geo = buildGlowDisc(4, [WHITE, BLACK]);
    expect(geo.positions.length / 3).toBe(1 + 4);
    expect(geo.colors.slice(0, 4)).toEqual([1, 1, 1, 1]);
    expect(geo.colors.slice(4, 8)).toEqual([0, 0, 0, 1]);
    expect(geo.indices).toHaveLength(4 * 3);
    expect(Math.hypot(geo.positions[3] ?? 0, geo.positions[4] ?? 0)).toBeCloseTo(1);
  });

  it('adds a ring of quads per extra colour', () => {
    const geo = buildGlowDisc(6, [WHITE, [0.5, 0.5, 0.5], BLACK]);
    expect(geo.positions.length / 3).toBe(1 + 2 * 6);
    expect(geo.indices).toHaveLength(6 * 3 + 6 * 6);
    expect(Math.max(...geo.indices)).toBe(12);
  });

  it('needs 3 segments and 2 colours', () => {
    expect(() => buildGlowDisc(2, [WHITE, BLACK])).toThrow(RangeError);
    expect(() => buildGlowDisc(5, [WHITE])).toThrow(RangeError);
  });
});

describe('buildGlowBar', () => {
  it('P03-R02: a unit-high bar, bright on the centre line, black on both edges', () => {
    const geo = buildGlowBar([WHITE, BLACK]);
    // Columns at x = -0.5, 0, 0.5, each with a bottom and a top vertex.
    const xs = geo.positions.filter((_, i) => i % 3 === 0);
    const ys = geo.positions.filter((_, i) => i % 3 === 1);
    expect(xs).toEqual([-0.5, -0.5, 0, 0, 0.5, 0.5]);
    expect(ys).toEqual([0, 1, 0, 1, 0, 1]);
    const reds = geo.colors.filter((_, i) => i % 4 === 0);
    expect(reds).toEqual([0, 0, 1, 1, 0, 0]);
    expect(geo.indices).toHaveLength(2 * 6);
    expect(() => buildGlowBar([WHITE])).toThrow(RangeError);
  });
});
