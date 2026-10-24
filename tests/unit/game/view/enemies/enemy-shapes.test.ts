import { describe, expect, it } from 'vitest';
import { SolidBuilder } from '../../../../../src/render/geometry/solids';
import { angryEyes, canopyPaint, decal } from '../../../../../src/game/view/enemies/enemy-shapes';

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
  it('phase 5 review: a canopy is painted on the back of a fighter fuselage', () => {
    const paint = canopyPaint([1, 2], [0, 0, 0]);
    expect(paint(3, 1)).toEqual([0, 0, 0]);
    // Not on the sides or the belly, nor outside the given stations.
    expect(paint(1, 1)).toBeUndefined();
    expect(paint(8, 2)).toBeUndefined();
    expect(paint(3, 0)).toBeUndefined();
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
