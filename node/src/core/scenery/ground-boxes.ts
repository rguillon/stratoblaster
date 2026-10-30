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

/** Key of the bucket (`i`, `j`) of a {@link BuildingIndex} (|j| stays far below a million). */
function bucketKey(i: number, j: number): number {
  return i * 1_000_003 + j;
}

/** A bucket of a {@link BuildingIndex}: its buildings, and the largest half-extents among them. */
interface Bucket {
  readonly buildings: Building[];
  halfX: number;
  halfZ: number;
}

/** Distance from `v` to the bucket `i` along one axis (0 inside it). */
function toBucket(v: number, i: number): number {
  return Math.max(0, i * BUILDING_BUCKET - v, v - (i + 1) * BUILDING_BUCKET);
}

/** Margin the buckets left out keep, so rounding never leaves out one that counts. */
const SLACK = 1e-9;

/**
 * The placed buildings, in buckets {@link BUILDING_BUCKET} wide by where their centres are
 * (reviewer, 2026-10-28: number keys, and a bucket too far for its largest building to come
 * close is left out).
 */
export class BuildingIndex {
  readonly #buckets = new Map<number, Bucket>();

  add(building: Building): void {
    const { x, z } = building.placement;
    const key = bucketKey(Math.floor(x / BUILDING_BUCKET), Math.floor(z / BUILDING_BUCKET));
    const bucket = this.#buckets.get(key);
    if (!bucket) {
      this.#buckets.set(key, {
        buildings: [building],
        halfX: building.halfX,
        halfZ: building.halfZ,
      });
      return;
    }
    bucket.buildings.push(building);
    bucket.halfX = Math.max(bucket.halfX, building.halfX);
    bucket.halfZ = Math.max(bucket.halfZ, building.halfZ);
  }

  /** Whether no building of the buckets two around `area`'s comes closer to it than `gap`. */
  clear(area: GroundBox, gap: number): boolean {
    const { x, z } = area.placement;
    const [bx, bz] = [Math.floor(x / BUILDING_BUCKET), Math.floor(z / BUILDING_BUCKET)];
    for (let i = bx - 2; i <= bx + 2; i++) {
      const dx = toBucket(x, i);
      for (let j = bz - 2; j <= bz + 2; j++) {
        const bucket = this.#buckets.get(bucketKey(i, j));
        if (!bucket) continue;
        if (dx > area.halfX + bucket.halfX + gap + SLACK) continue;
        if (toBucket(z, j) > area.halfZ + bucket.halfZ + gap + SLACK) continue;
        if (bucket.buildings.some((b) => overlap(b, area, gap))) return false;
      }
    }
    return true;
  }
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
