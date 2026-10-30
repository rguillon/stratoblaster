// The segments of the roads, indexed by buckets for distance queries, and the building slots
// along them (road network).
import type { Road, RoadSlot } from './road-network';

export interface Segment {
  readonly road: Road;
  readonly ax: number;
  readonly az: number;
  readonly bx: number;
  readonly bz: number;
  readonly halfWidth: number;
}

/** Bucket size of the segment index; distance queries see at least this far. */
export const BUCKET = 64;

/** Key of the bucket (`i`, `j`) of a {@link SegmentIndex} (|j| stays far below a million). */
function bucketKey(i: number, j: number): number {
  return i * 1_000_003 + j;
}

/** Distance from (`x`, `z`) to the centre line of `s`. */
export function segmentDistance(x: number, z: number, s: Segment): number {
  const dx = s.bx - s.ax;
  const dz = s.bz - s.az;
  const length2 = dx * dx + dz * dz;
  const t =
    length2 > 0 ? Math.max(0, Math.min(1, ((x - s.ax) * dx + (z - s.az) * dz) / length2)) : 0;
  return Math.hypot(x - (s.ax + t * dx), z - (s.az + t * dz));
}

/** The segments of roads, in buckets {@link BUCKET} wide by where their ends are. */
export class SegmentIndex {
  readonly #buckets = new Map<number, Segment[]>();
  /** Farthest a segment reaches from its nearer end: half its length, plus half its width. */
  #reach = 0;

  add(road: Road): void {
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      const halfWidth = Math.max(a.width, b.width) / 2;
      this.#reach = Math.max(this.#reach, Math.hypot(b.x - a.x, b.z - a.z) / 2 + halfWidth);
      const segment = { road, ax: a.x, az: a.z, bx: b.x, bz: b.z, halfWidth };
      const keys = new Set(
        [a, b].map((p) => bucketKey(Math.floor(p.x / BUCKET), Math.floor(p.z / BUCKET))),
      );
      for (const key of keys) {
        const bucket = this.#buckets.get(key);
        if (bucket) bucket.push(segment);
        else this.#buckets.set(key, [segment]);
      }
    });
  }

  /** The edge of the nearest road `which` accepts, within about {@link BUCKET} units. */
  nearest(
    x: number,
    z: number,
    which: (road: Road) => boolean,
  ): { readonly distance: number; readonly road?: Road } {
    const bx = Math.floor(x / BUCKET);
    const bz = Math.floor(z / BUCKET);
    // Reviewer, 2026-10-28: numbers for keys, and no object per segment (props ask this a lot).
    let distance = Infinity;
    let road: Road | undefined;
    for (let i = bx - 1; i <= bx + 1; i++) {
      for (let j = bz - 1; j <= bz + 1; j++) {
        for (const s of this.#buckets.get(bucketKey(i, j)) ?? []) {
          const d = segmentDistance(x, z, s) - s.halfWidth;
          if (d < distance && which(s.road)) [distance, road] = [d, s.road];
        }
      }
    }
    return road ? { distance, road } : { distance };
  }

  /**
   * Whether no road edge is closer than `clearance` to (`x`, `z`) among those {@link nearest}
   * sees. Only the buckets a road in reach can be in are searched, up to the first road in reach.
   */
  clearOf(x: number, z: number, clearance: number): boolean {
    const around = clearance + this.#reach;
    if (around > BUCKET) return this.nearest(x, z, () => true).distance >= clearance;
    const [bx, bz] = [Math.floor(x / BUCKET), Math.floor(z / BUCKET)];
    const [i0, i1] = [Math.floor((x - around) / BUCKET), Math.floor((x + around) / BUCKET)];
    const [j0, j1] = [Math.floor((z - around) / BUCKET), Math.floor((z + around) / BUCKET)];
    for (let i = Math.max(i0, bx - 1); i <= Math.min(i1, bx + 1); i++) {
      for (let j = Math.max(j0, bz - 1); j <= Math.min(j1, bz + 1); j++) {
        for (const s of this.#buckets.get(bucketKey(i, j)) ?? []) {
          if (segmentDistance(x, z, s) - s.halfWidth < clearance) return false;
        }
      }
    }
    return true;
  }
}

/**
 * What a `RoadNetwork` made: enough to draw it and place trees by it without generating it again
 * (P13-R03). Its slots and blocks are left out (reviewer, 2026-10-28): only placing the
 * buildings needs them, and that is done with the network.
 */
export interface RoadSnapshot {
  readonly roads: readonly Road[];
}

/** Adds to `slots` the slots every `spacing` along `road`, on both sides, numbered on from them. */
export function addSlots(road: Road, spacing: number, slots: RoadSlot[]): void {
  let travelled = spacing / 2;
  road.points.forEach((a, i) => {
    const b = road.points[i + 1];
    if (!b) return;
    const length = Math.hypot(b.x - a.x, b.z - a.z);
    if (length === 0) return;
    const [tx, tz] = [(b.x - a.x) / length, (b.z - a.z) / length];
    for (; travelled < length; travelled += spacing) {
      const t = travelled / length;
      const x = a.x + (b.x - a.x) * t;
      const z = a.z + (b.z - a.z) * t;
      const index = slots.length;
      slots.push(
        { road, index, x, z, nx: tz, nz: -tx },
        { road, index: index + 1, x, z, nx: -tz, nz: tx },
      );
    }
    travelled -= length;
  });
}
