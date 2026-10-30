import type { SolidBuilder } from '../../../../render/geometry/solids';

// P09-R09, 3-3: the carved stone, moss, vines and neon cracks of the Lost temples' bosses (the
// Stone Idol and the Sky Temple; World 3 theme: dark metal with neon, plus moss, vines and
// stone). Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];
/** A point in the XZ plane. */
type Flat = readonly [number, number];

/** Stone and jungle shades (vertex colours, multiplied into the hull's dark metal). */
export const STONE = {
  /** Weathered stone on the top faces, catching the light. */
  light: [0.34, 0.32, 0.28] as Rgb,
  /** Carved stone. */
  base: [0.23, 0.22, 0.2] as Rgb,
  /** Stone in shadow: recesses, the undersides. */
  dark: [0.13, 0.12, 0.11] as Rgb,
  /** Deep cuts: sockets, doorways, the mouth. */
  deep: [0.04, 0.04, 0.045] as Rgb,
  /** Moss, and older moss in the cracks. */
  moss: [0.14, 0.46, 0.07] as Rgb,
  mossDark: [0.08, 0.3, 0.04] as Rgb,
  /** Vines and their leaves. */
  vine: [0.07, 0.3, 0.04] as Rgb,
  leaf: [0.12, 0.52, 0.06] as Rgb,
  /** Old gilding on carved stone. */
  gilt: [0.6, 0.45, 0.14] as Rgb,
};

/** A straight bar from `a` to `b` (3D), `width` across and `thick` high: a vine, a cable. */
export function bar(
  builder: SolidBuilder,
  [ax, ay, az]: Vec3,
  [bx, by, bz]: Vec3,
  [width, thick]: readonly [number, number],
  color: Rgb,
): void {
  const [dx, dy, dz] = [bx - ax, by - ay, bz - az];
  const length = Math.hypot(dx, dy, dz);
  if (length === 0) return;
  builder.box([width, thick, length], color, {
    at: [(ax + bx) / 2, (ay + by) / 2 - thick / 2, (az + bz) / 2],
    yaw: Math.atan2(dx, dz),
    pitch: -Math.asin(dy / length),
  });
}

/** A vine along `path` (3D points), with a leaf at every other joint. */
export function vine(hull: SolidBuilder, path: readonly Vec3[], width = 1.1): void {
  path.slice(1).forEach((b, i) => {
    const a = path[i];
    if (!a) return;
    bar(hull, a, b, [width, width * 0.8], STONE.vine);
    if (i % 2 === 0) leaf(hull, a, width * 2.2, i);
  });
}

/** A leaf at `at`, `size` long, turned by its index. */
export function leaf(hull: SolidBuilder, at: Vec3, size: number, turn: number): void {
  const blade = [
    [0, 0],
    [size * 0.35, size * 0.5],
    [0, size],
    [-size * 0.35, size * 0.5],
  ] as const;
  hull.slab(blade, [0, 0.3], STONE.leaf, { at, yaw: turn * 2.1 + 0.5 });
}

/** A patch of moss on a top face at `at`, `size` across: a low, faceted cushion. */
export function moss(hull: SolidBuilder, at: Vec3, size: number, turn = 0): void {
  hull.cylinder(size, size * 0.18, 6, STONE.mossDark, { at, yaw: turn }, size * 0.75);
  hull.cylinder(size * 0.6, size * 0.3, 5, STONE.moss, { at, yaw: turn + 0.7 }, size * 0.35);
}

/** A neon crack along `path` (XZ) at height `y`: thin lit strips, `width` wide. */
export function crack(
  neon: SolidBuilder,
  path: readonly Flat[],
  y: number,
  color: Rgb,
  width = 0.6,
): void {
  path.slice(1).forEach((b, i) => {
    const a = path[i];
    if (a) bar(neon, [a[0], y, a[1]], [b[0], y, b[1]], [width, 0.3], color);
  });
}
