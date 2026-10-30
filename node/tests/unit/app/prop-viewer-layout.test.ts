import { describe, expect, it } from 'vitest';
import { tileLayout } from '../../../src/app/prop-viewer-layout';

describe('props/ page on the grid of tiles (phase 15)', () => {
  it('P15-R10: each footprint covers whole tiles, a half tile off for an odd size', () => {
    const footprints = [
      [1, 2],
      [3, 4],
    ] as const;
    const { centres } = tileLayout(footprints, 1, false);
    footprints.forEach(([w, d], i) => {
      const [cx, cz] = centres[i] ?? [NaN, NaN];
      expect(Number.isInteger(cx - w / 2), 'x').toBe(true);
      expect(Number.isInteger(cz - d / 2), 'z').toBe(true);
    });
  });

  it('P15-R10: with streets, every block is ringed by one-tile roads that join', () => {
    const { roads, bounds, centres } = tileLayout(
      [
        [2, 2],
        [2, 2],
        [1, 1],
        [2, 1],
      ],
      1,
      true,
    );
    const at = new Set(roads.map((r) => `${String(r.x)},${String(r.z)}`));
    const [x0, x1, z0, z1] = bounds;
    // 2 × 2 cells of 3 tiles plus the far road: a ring and a cross of roads.
    expect(x1 - x0).toBe(7);
    expect(roads).toHaveLength(7 * 7 - 4 * 4);
    expect(roads.filter((r) => r.kind === 'cross')).toHaveLength(1);
    expect(roads.filter((r) => r.kind === 'turn')).toHaveLength(4);
    expect(roads.filter((r) => r.kind === 'tee')).toHaveLength(4);
    for (const [cx, cz] of centres)
      expect(at.has(`${String(Math.floor(cx))},${String(Math.floor(cz))}`)).toBe(false);
    expect(z1 - z0).toBe(7);
  });

  it('P15-R10: no road without streets', () => {
    expect(tileLayout([[1, 1]], 2, false).roads).toHaveLength(0);
  });
});
