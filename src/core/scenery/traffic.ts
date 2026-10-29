import { hash2D } from '../math/noise';
import type { GroundArea, PropPlacement } from './prop-placement';
import type { Road } from './road-network';
import type { CarRules } from './scenery-level';

// Phase 4 review: cars driving along the streets and main roads (not the paths), right-hand
// traffic, in one lane each way (two on 2×2 roads). All the cars of one lane drive at the same
// speed, so they never catch up with each other. A car that reaches the end of its road goes
// round to its start, hidden near both ends: streets end in the crossing street, main roads off
// the screen.

/**
 * A road as cars follow it: its points, their distance along it, and the road surface height
 * there, worked out when a car is first placed on it (reviewer, 2026-10-28: for every road at the
 * start of a level, that took 24–104 ms).
 */
interface Track {
  readonly road: Road;
  readonly along: readonly number[];
  heights: readonly number[] | undefined;
  readonly length: number;
  /** Z range of the road, to skip the cars of roads out of view. */
  readonly zMin: number;
  readonly zMax: number;
}

interface Car {
  readonly kind: string;
  readonly track: Track;
  /** 1 on the right of the road's direction (driving along it), -1 on the left. */
  readonly side: 1 | -1;
  /** Distance from the centre line. */
  readonly offset: number;
  /** Distance along the road at time 0. */
  readonly start: number;
  readonly speed: number;
}

function trackOf(road: Road): Track {
  const along = [0];
  road.points.forEach((p, i) => {
    const next = road.points[i + 1];
    if (next) along.push((along[i] ?? 0) + Math.hypot(next.x - p.x, next.z - p.z));
  });
  const zs = road.points.map((p) => p.z);
  const [zMin, zMax] = [Math.min(...zs) - road.width, Math.max(...zs) + road.width];
  return { road, along, heights: undefined, length: along.at(-1) ?? 0, zMin, zMax };
}

/** Index of the segment of `track` that contains distance `s` (binary search). */
function segmentAt(track: Track, s: number): number {
  let [lo, hi] = [0, track.along.length - 2];
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if ((track.along[mid] ?? 0) <= s) lo = mid;
    else hi = mid - 1;
  }
  return lo;
}

/** Z span of a bucket of the roads with cars (`Traffic.#buckets`). */
const BUCKET = 256;

const bucketOf = (z: number): number => Math.floor(z / BUCKET);

/**
 * The cars of `rules` on all the streets and main roads of a level, and where they are. The roads
 * with cars are indexed by the buckets of Z they span, so finding the cars in an area only looks
 * at the roads near it (reviewer, 2026-10-28: not at the level's 6–11K cars every frame).
 */
export class Traffic {
  /** The roads with cars, in the order of the level's roads, each with its cars. */
  readonly #tracks: { readonly track: Track; readonly cars: readonly Car[] }[] = [];
  /** Indices in `#tracks` of the roads that span each bucket, by bucket. */
  readonly #buckets = new Map<number, number[]>();
  /** The first and last buckets with roads. */
  #lowest = Infinity;
  #highest = -Infinity;
  #count = 0;

  constructor(
    roads: readonly Road[],
    private readonly height: (x: number, z: number) => number,
    private readonly rules: CarRules,
    private readonly seed: number,
  ) {
    this.add(roads);
  }

  /** Adds the cars of `roads` (e.g. the runout's, which come later: reviewer, 2026-10-28). */
  add(roads: readonly Road[]): void {
    for (const road of roads) {
      if (road.kind === 'cross' || road.points.length < 2) continue;
      const track = trackOf(road);
      const cars = road.points.flatMap((_, i) => this.#carAt(track, i, this.seed) ?? []);
      if (cars.length === 0) continue;
      const index = this.#tracks.push({ track, cars }) - 1;
      const [first, last] = [bucketOf(track.zMin), bucketOf(track.zMax)];
      for (let b = first; b <= last; b++) {
        const bucket = this.#buckets.get(b);
        if (bucket) bucket.push(index);
        else this.#buckets.set(b, [index]);
      }
      [this.#lowest, this.#highest] = [
        Math.min(this.#lowest, first),
        Math.max(this.#highest, last),
      ];
      this.#count += cars.length;
    }
  }

  /** Number of cars on the level. */
  get count(): number {
    return this.#count;
  }

  /** Width of the part of `road` cars drive on: P15-R11, streets without their sidewalks. */
  #roadway(road: Road): number {
    return road.kind === 'street' ? road.width - 2 * (this.rules.sidewalk ?? 0) : road.width;
  }

  /** The car that starts at point `i` of a road, if any: one chance per point. */
  #carAt(track: Track, i: number, seed: number): Car | undefined {
    const { road } = track;
    const r = (draw: number): number => hash2D(road.index * 7 + draw, i, seed * 13 + 5);
    const kind = this.rules.kinds[Math.floor(r(2) * this.rules.kinds.length)];
    if (r(0) >= this.rules.density || kind === undefined) return undefined;
    const side = r(1) < 0.5 ? 1 : -1;
    const lane = Math.floor(r(3) * road.lanes);
    // One speed per lane of the road, so cars of a lane keep their distance.
    const lr = hash2D(road.index, side * 3 + lane, seed * 17 + 9);
    const [slow, fast] = this.rules.speed;
    return {
      kind,
      track,
      side,
      offset: (this.#roadway(road) / (2 * road.lanes)) * (lane + 0.5),
      start: track.along[i] ?? 0,
      speed: slow + (fast - slow) * lr,
    };
  }

  /** The cars in `area` at `time` (seconds), facing the way they drive, in the roads' order. */
  at(time: number, area: GroundArea): PropPlacement[] {
    const out: PropPlacement[] = [];
    for (const index of this.#tracksIn(area)) {
      for (const car of this.#tracks[index]?.cars ?? []) {
        const p = this.#place(car, time);
        if (p && p.x >= area.xMin && p.x < area.xMax && p.z >= area.zMin && p.z < area.zMax) {
          out.push(p);
        }
      }
    }
    return out;
  }

  /** Indices of the roads with cars whose Z range meets `area`, in order. */
  #tracksIn(area: GroundArea): number[] {
    // Within the buckets that have roads (the area may be endless).
    const first = Math.max(bucketOf(area.zMin), this.#lowest);
    const last = Math.min(bucketOf(area.zMax), this.#highest);
    const found: number[] = [];
    for (let b = first; b <= last; b++) {
      for (const index of this.#buckets.get(b) ?? []) {
        const track = this.#tracks[index]?.track;
        // Once per road: in the first bucket of the area it spans.
        if (!track || Math.max(bucketOf(track.zMin), first) !== b) continue;
        if (track.zMax >= area.zMin && track.zMin < area.zMax) found.push(index);
      }
    }
    return found.sort((a, b) => a - b);
  }

  /** How far along its road `car` is at `time`; none near the ends, where it is hidden. */
  #distance(car: Car, time: number): number | undefined {
    const { length } = car.track;
    const s = (((car.start + car.side * car.speed * time) % length) + length) % length;
    // Hidden near the ends, where it turns into the crossing street or leaves the screen.
    return s < this.rules.length || s > length - this.rules.length ? undefined : s;
  }

  /** The road surface heights at the points of `track`, worked out on first use. */
  #heightsOf(track: Track): readonly number[] {
    track.heights ??= track.road.points.map((p) => this.height(p.x, p.z) + this.rules.lift);
    return track.heights;
  }

  #place(car: Car, time: number): PropPlacement | undefined {
    const { track, side } = car;
    const s = this.#distance(car, time);
    if (s === undefined) return undefined;
    const i = segmentAt(track, s);
    const [a, b] = [track.road.points[i], track.road.points[i + 1]];
    const [s0, s1] = [track.along[i] ?? 0, track.along[i + 1] ?? 0];
    if (!a || !b || s1 <= s0) return undefined;
    const t = (s - s0) / (s1 - s0);
    const [dx, dz] = [(b.x - a.x) / (s1 - s0), (b.z - a.z) / (s1 - s0)];
    const heights = this.#heightsOf(track);
    const [h0, h1] = [heights[i] ?? 0, heights[i + 1] ?? 0];
    return {
      kind: car.kind,
      x: a.x + (b.x - a.x) * t + dz * side * car.offset,
      y: h0 + (h1 - h0) * t,
      z: a.z + (b.z - a.z) * t - dx * side * car.offset,
      rotation: Math.atan2(dx, dz) + (side > 0 ? 0 : Math.PI),
      scale: this.rules.scale,
    };
  }
}
