// The segments of the roads, indexed by buckets for distance queries (road network).
import type { Road, RoadSlot } from './road-network';
import type { Block } from './street-grid';

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

/** Distance from (`x`, `z`) to the centre line of `s`. */
export function segmentDistance(x: number, z: number, s: Segment): number {
  const dx = s.bx - s.ax;
  const dz = s.bz - s.az;
  const length2 = dx * dx + dz * dz;
  const t =
    length2 > 0 ? Math.max(0, Math.min(1, ((x - s.ax) * dx + (z - s.az) * dz) / length2)) : 0;
  return Math.hypot(x - (s.ax + t * dx), z - (s.az + t * dz));
}

/** What a {@link RoadNetwork} made: enough to make it again without generating it (P13-R03). */
export interface RoadSnapshot {
  readonly roads: readonly Road[];
  readonly slots: readonly RoadSlot[];
  readonly blocks: readonly Block[];
}
