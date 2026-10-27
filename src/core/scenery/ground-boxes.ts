// The boxes of ground props take, and the buckets of the index of placed buildings.
import type { Building } from './away-placement';

/** Bucket size of the index of placed buildings. */
export const BUILDING_BUCKET = 32;

/** Whether the ground boxes of `a` and `b` come closer than `gap`. */
export function overlap(a: GroundBox, b: GroundBox, gap: number): boolean {
  const apartX = Math.abs(a.placement.x - b.placement.x) >= a.halfX + b.halfX + gap;
  const apartZ = Math.abs(a.placement.z - b.placement.z) >= a.halfZ + b.halfZ + gap;
  return !apartX && !apartZ;
}

/** The box of ground a prop takes around its centre. */
export type GroundBox = Pick<Building, 'halfX' | 'halfZ'> & {
  readonly placement: { x: number; z: number };
};

/** Key of the bucket of the building index holding (`x`, `z`). */
export function bucketKey(x: number, z: number): string {
  return `${String(Math.floor(x / BUILDING_BUCKET))},${String(Math.floor(z / BUILDING_BUCKET))}`;
}

/**
 * What a {@link PropPlacer} placed, in order: enough to make it again without placing them
 * (P13-R03). The first `fixed` buildings are its set pieces and lines.
 */
export interface PlacerSnapshot {
  readonly buildings: readonly Building[];
  readonly fixed: number;
}

/** One prop standing on the ground. */
export interface PropPlacement {
  /** Key of the prop's model (`PropKindRule.id`). */
  readonly kind: string;
  readonly x: number;
  /** Height of the ground the prop stands on. */
  readonly y: number;
  readonly z: number;
  /** Turn around the vertical axis, in radians. */
  readonly rotation: number;
  readonly scale: number;
  /** Per-axis scale (X, Y, Z) instead of `scale`, for podiums stretched to their block. */
  readonly size?: readonly [number, number, number];
}

/** A rectangle of ground, in world units. */
export interface GroundArea {
  readonly xMin: number;
  readonly xMax: number;
  readonly zMin: number;
  readonly zMax: number;
}

/** Whether (`x`, `z`) is inside `area` (its far edges excluded). */
export function inside(area: GroundArea, x: number, z: number): boolean {
  return x >= area.xMin && x < area.xMax && z >= area.zMin && z < area.zMax;
}
