import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// Phase 4 review: buildings of the city centre. Sizes in world units, standing on Y = 0; the
// front faces -Z. Lit windows and neon trims are self-lit accents.

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

/** A slim glass tower with cyan window bands and an antenna. */
export function buildGlassTower(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  s.box([14, 78, 14], C.glassBlue, {}, C.metalDark);
  s.box([10, 4, 10], C.metal, { at: [0, 78, 0] });
  s.cylinder(0.5, 14, 4, C.metal, { at: [0, 82, 0] });
  windowBands(l, [14, 14], [6, 76], 8, 2, L.cyanDim);
  l.box([1.2, 1.2, 1.2], L.red, { at: [0, 96, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A broad concrete office block with warm window rows and roof units. */
export function buildOfficeBlock(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  s.box([22, 32, 16], C.concrete, {}, C.roof);
  s.box([6, 3, 5], C.metalDark, { at: [-5, 32, 2] });
  s.box([4, 2, 4], C.metal, { at: [6, 32, -3] });
  windowBands(l, [22, 16], [4, 30], 6, 2, L.windowDim);
  return { structure: s.geometry, lights: l.geometry };
}

/** An L-shaped brick apartment block with lit windows and a pink neon sign on the roof. */
export function buildApartmentBlock(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  s.box([20, 24, 8], C.brick, { at: [0, 0, -3] }, C.roof);
  s.box([8, 24, 14], C.brick, { at: [6, 0, 4] }, C.roof);
  windowBands(l, [20, 8], [3, 23], 6, 2, L.windowDim, [0, -3]);
  l.box([10, 3, 0.4], L.pink, { at: [-3, 24.5, -6.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A stepped tower in three tiers under a spire, with cyan trims at each step. */
export function buildSteppedTower(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder({ openBottoms: true });
  const tiers = [
    [18, 0, 22],
    [13, 22, 20],
    [8, 42, 18],
  ] as const;
  for (const [size, y, height] of tiers) {
    s.box([size, height, size], C.concreteDark, { at: [0, y, 0] }, C.roof);
    l.box([size + 0.4, 0.6, size + 0.4], L.cyanDim, { at: [0, y + height - 0.6, 0] });
    windowBands(l, [size, size], [y + 3, y + height - 2], 6, 1.8, L.windowDim);
  }
  s.lathe(
    [
      [2.5, 60],
      [0, 72],
    ],
    4,
    C.metal,
  );
  l.box([1, 1, 1], L.red, { at: [0, 72, 0] });
  return { structure: s.geometry, lights: l.geometry };
}
