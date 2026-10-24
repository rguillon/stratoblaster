import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SectionPoint, SolidBuilder } from '../../../render/geometry/solids';

type Vec3 = [number, number, number];

/** A point `r` from the model's centre in the direction `angle` (radians from +Z towards +X). */
export function radial(angle: number, r: number, y: number): Vec3 {
  return [Math.sin(angle) * r, y, Math.cos(angle) * r];
}

/** `count` angles evenly spread around the circle, the first one on +Z (the nose). */
export function around(count: number): number[] {
  return Array.from({ length: count }, (_, i) => (2 * Math.PI * i) / count);
}

/** The outline moved by `dx` across. */
export function shiftX(outline: readonly OutlinePoint[], dx: number): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [x + dx, z]);
}

/** The outline mirrored left to right (for the other wing). */
export function flipX(outline: readonly OutlinePoint[]): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [-x, z]);
}

/** Both sides: -1 (left) and 1 (right). */
export const SIDES = [-1, 1] as const;

/**
 * Loft cross-sections (`SolidBuilder.loft`), counter-clockwise seen from the nose. A hull: flat
 * belly and back, its widest point a chine low on the sides.
 */
export const HULL_SECTION: readonly SectionPoint[] = [
  [0.55, 0],
  [1, 0.4],
  [0.6, 1],
  [-0.6, 1],
  [-1, 0.4],
  [-0.55, 0],
];

/** A round-ish pod or boom: a hexagon. */
export const POD_SECTION: readonly SectionPoint[] = [
  [0.5, 0],
  [1, 0.5],
  [0.5, 1],
  [-0.5, 1],
  [-1, 0.5],
  [-0.5, 0],
];

/** A canopy or dorsal ridge sitting on a hull: open at the bottom (loft it with `open`). */
export const CANOPY_SECTION: readonly SectionPoint[] = [
  [1, 0],
  [0.7, 0.6],
  [0, 1],
  [-0.7, 0.6],
  [-1, 0],
];

/** A spike: a triangle `width` wide at `base`, pointed at `tip` (a fang, a claw, a horn). */
export function spike(base: OutlinePoint, tip: OutlinePoint, width: number): OutlinePoint[] {
  const [dx, dz] = [tip[0] - base[0], tip[1] - base[1]];
  const k = width / 2 / Math.hypot(dx, dz);
  return [[base[0] - dz * k, base[1] + dx * k], tip, [base[0] + dz * k, base[1] - dx * k]];
}

/**
 * Two eye slits on either side of `center`, `gap` apart, each `length` long and `width` deep,
 * their outer ends swept back by `slant` radians: a frown seen from above.
 */
export function angryEyes(
  [cx, cz]: OutlinePoint,
  gap: number,
  [length, width]: readonly [number, number],
  slant: number,
): OutlinePoint[][] {
  return SIDES.map((s) => {
    const inner: OutlinePoint = [cx + (s * gap) / 2, cz];
    const outer: OutlinePoint = [
      inner[0] + s * length * Math.cos(slant),
      cz - length * Math.sin(slant),
    ];
    return [inner, outer, [outer[0], outer[1] - width], [inner[0], inner[1] - width]];
  });
}

/** A flat convex outline at height `y`, facing up: a light painted on a hull (2 triangles a quad). */
export function decal(
  builder: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  color: readonly [number, number, number],
): void {
  const area = outline.reduce((sum, [x1, z1], i) => {
    const [x2, z2] = outline[(i + 1) % outline.length] ?? [x1, z1];
    return sum + x1 * z2 - x2 * z1;
  }, 0);
  // Facing up (+Y) takes clockwise corners in (x, z).
  const corners = area > 0 ? [...outline].reverse() : outline;
  builder.face(
    corners.map(([x, z]): Vec3 => [x, y, z]),
    color,
  );
}
