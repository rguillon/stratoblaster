import type { SolidBuilder } from '../../../render/geometry/solids';

// Phase 4 review: rows of lit windows for the buildings of the city centre (see `city-lots.ts`).

type Rgb = readonly [number, number, number];

/**
 * Rows of lit windows on the 4 faces (few and thick: thin bands under a pixel shimmered as the
 * view scrolled) of a `w × d` block, from `y0` to `y1`, every `gap`, each
 * row `band` high: one flat quad per face and row, just off the walls (2 triangles each).
 */
export function windowBands(
  l: SolidBuilder,
  [w, d]: readonly [number, number],
  [y0, y1]: readonly [number, number],
  gap: number,
  band: number,
  color: Rgb,
  [x, z]: readonly [number, number] = [0, 0],
  /** How far the bands stand off the walls. */
  proud = 0.1,
): void {
  const [x0, x1, xl, xr] = [x - w * 0.43, x + w * 0.43, x - w / 2 - proud, x + w / 2 + proud];
  const [z0, z1, zf, zb] = [z - d * 0.43, z + d * 0.43, z - d / 2 - proud, z + d / 2 + proud];
  // The bottom edge of each face, from (x, z) to (x, z), counter-clockwise seen from outside.
  const faces = [
    [x0, zf, x1, zf],
    [x1, zb, x0, zb],
    [xl, z1, xl, z0],
    [xr, z0, xr, z1],
  ] as const;
  for (let y = y0; y + band <= y1; y += gap) {
    const t = y + band;
    for (const [ax, az, bx, bz] of faces) {
      l.face(
        [
          [ax, y, az],
          [ax, t, az],
          [bx, t, bz],
          [bx, y, bz],
        ],
        color,
      );
    }
  }
}
