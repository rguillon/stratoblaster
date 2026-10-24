import type { OutlinePoint } from '../../../render/geometry/outline';

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
