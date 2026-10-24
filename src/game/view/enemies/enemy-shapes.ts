import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SectionPoint } from '../../../render/geometry/solids';

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
