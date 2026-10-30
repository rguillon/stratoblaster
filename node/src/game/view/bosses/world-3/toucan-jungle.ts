import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';

// P09-R09: the jungle on the 3-2 bosses (the Toucan and the Canopy Spider): moss on their
// plates, vines hanging along them, leaves (GD-61, World 3: dark metal with neon, plus moss,
// vines and stone). Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Moss: a deep green, and a lighter one where the light catches it. */
export const MOSS: Rgb = [0.13, 0.24, 0.08];
export const MOSS_LIT: Rgb = [0.22, 0.36, 0.1];
/** Vines and their leaves. */
export const VINE: Rgb = [0.1, 0.17, 0.06];
export const LEAF: Rgb = [0.16, 0.32, 0.09];

/**
 * A cylinder from `a` to `b` (radius `r` at `a`, `rb` at `b`, `sides` facets): a strut, a leg, a
 * vine. Pitched off +Y, then yawed, so that its axis runs along `b - a`.
 */
export function segment(
  builder: SolidBuilder,
  [a, b]: readonly [Vec3, Vec3],
  [r, rb]: readonly [number, number],
  color: Rgb,
  sides = 6,
): void {
  const [dx, dy, dz] = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const length = Math.hypot(dx, dy, dz);
  const pitch = Math.atan2(Math.hypot(dx, dz), dy);
  builder.cylinder(r, length, sides, color, { at: a, pitch, yaw: Math.atan2(dx, dz) }, rb);
}

/**
 * A patch of moss `radius` wide lying at `at` (its top a little above it): an uneven, low
 * hexagon, lighter on top. `seed` turns and bends its outline so no two patches look alike.
 */
export function moss(hull: SolidBuilder, at: Vec3, radius: number, seed = 0): void {
  const outline = Array.from({ length: 6 }, (_, k): OutlinePoint => {
    const a = (k * Math.PI) / 3 + seed;
    const r = radius * (0.75 + 0.25 * Math.sin(seed * 3.1 + k * 2.3));
    return [Math.cos(a) * r, Math.sin(a) * r];
  });
  hull.bevelSlab(outline, [-0.3, 0, 0.9], [0, radius * 0.25], MOSS, { at }, MOSS_LIT);
}

/**
 * A vine along `points`, a thin stem from one to the next, a leaf at every other joint (a
 * small slab turned along the stem).
 */
export function vine(hull: SolidBuilder, points: readonly Vec3[], thickness = 0.5): void {
  points.slice(1).forEach((b, i) => {
    const a = points[i] ?? b;
    segment(hull, [a, b], [thickness, thickness], VINE, 4);
    if (i % 2 === 1) return;
    const leaf: OutlinePoint[] = [
      [0, 0],
      [1.2, 1.4],
      [0, 3],
      [-1.2, 1.4],
    ];
    const yaw = Math.atan2(b[0] - a[0], b[2] - a[2]) + (i % 4 === 0 ? 1 : -1);
    hull.slab(leaf, [0, 0.3], LEAF, { at: b, yaw });
  });
}

/** `count` points from `a` to `b`, sagging `sag` down (-Y) in the middle: a hanging vine. */
export function sagging(a: Vec3, b: Vec3, count: number, sag: number): Vec3[] {
  return Array.from({ length: count }, (_, i): Vec3 => {
    const t = i / (count - 1);
    const drop = sag * 4 * t * (1 - t);
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - drop, a[2] + (b[2] - a[2]) * t];
  });
}
