import { describe, expect, it } from 'vitest';
import { SolidBuilder } from '../../../../../src/render/geometry/solids';
import { angryEyes, decal, spike } from '../../../../../src/game/view/enemies/enemy-shapes';

/** Y of Babylon's front-face normal of the first triangle, (c - a) × (b - a). */
function upward(positions: readonly number[], indices: readonly number[]): number {
  const at = (n: number): [number, number] => {
    const k = indices[n] ?? 0;
    return [positions[k * 3] ?? 0, positions[k * 3 + 2] ?? 0];
  };
  const [[ax, az], [bx, bz], [cx, cz]] = [at(0), at(1), at(2)];
  return (cz - az) * (bx - ax) - (cx - ax) * (bz - az);
}

describe('enemy shapes', () => {
  it('phase 5 review: a spike is a triangle `width` wide at its base, pointed at its tip', () => {
    const [left, tip, right] = spike([0, 0], [0, 10], 4);
    expect(tip).toEqual([0, 10]);
    expect(left?.[0]).toBeCloseTo(-2);
    expect(right?.[0]).toBeCloseTo(2);
    expect(left?.[1]).toBeCloseTo(0);
  });

  it('phase 5 review: angry eyes slant back from the centre on both sides', () => {
    const [left, right] = angryEyes([0, 5], 1, [2, 0.5], 0.4);
    // Inner ends in front of the outer ends: a frown seen from above.
    expect(left?.[0]).toEqual([-0.5, 5]);
    expect(left?.[1]?.[0]).toBeLessThan(-0.5);
    expect(left?.[1]?.[1]).toBeLessThan(5);
    expect(right?.[0]).toEqual([0.5, 5]);
    expect(right?.[1]?.[0]).toBeGreaterThan(0.5);
  });

  it('phase 5 review: a decal is one flat face facing up, whatever the winding', () => {
    const quad = [
      [0, 0],
      [1, 0],
      [1, 1],
      [0, 1],
    ] as const;
    for (const outline of [quad, [...quad].reverse()]) {
      const builder = new SolidBuilder();
      decal(builder, outline, 2, [1, 0, 0]);
      const { positions, indices } = builder.geometry;
      expect(indices).toHaveLength(6);
      expect(positions.filter((_, i) => i % 3 === 1).every((y) => y === 2)).toBe(true);
      // Babylon's front face normal (c - a) × (b - a) points up.
      expect(upward(positions, indices)).toBeGreaterThan(0);
    }
  });
});
