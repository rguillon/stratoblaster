import { hash2D } from '../math/noise';
import type { GroundArea, PropPlacement } from './prop-placement';
import type { Road } from './road-network';
import type { CarRules } from './scenery-level';

// Phase 4 review: cars driving along the streets and main roads (not the paths), right-hand
// traffic, in one lane each way (two on 2×2 roads). All the cars of one lane drive at the same
// speed, so they never catch up with each other. A car that reaches the end of its road goes
// round to its start, hidden near both ends: streets end in the crossing street, main roads off
// the screen.

/** A road as cars follow it: its points, their distance along it, and the road surface height. */
interface Track {
  readonly road: Road;
  readonly along: readonly number[];
  readonly heights: readonly number[];
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

function trackOf(road: Road, height: (x: number, z: number) => number, lift: number): Track {
  const along = [0];
  road.points.forEach((p, i) => {
    const next = road.points[i + 1];
    if (next) along.push((along[i] ?? 0) + Math.hypot(next.x - p.x, next.z - p.z));
  });
  const heights = road.points.map((p) => height(p.x, p.z) + lift);
  const zs = road.points.map((p) => p.z);
  const [zMin, zMax] = [Math.min(...zs) - road.width, Math.max(...zs) + road.width];
  return { road, along, heights, length: along.at(-1) ?? 0, zMin, zMax };
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

/** The cars of `rules` on all the streets and main roads of a level, and where they are. */
export class Traffic {
  readonly #cars: Car[] = [];

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
      const track = trackOf(road, this.height, this.rules.lift);
      road.points.forEach((_, i) => {
        const car = this.#carAt(track, i, this.seed);
        if (car) this.#cars.push(car);
      });
    }
  }

  /** Number of cars on the level. */
  get count(): number {
    return this.#cars.length;
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
      offset: (road.width / (2 * road.lanes)) * (lane + 0.5),
      start: track.along[i] ?? 0,
      speed: slow + (fast - slow) * lr,
    };
  }

  /** The cars in `area` at `time` (seconds), facing the way they drive. */
  at(time: number, area: GroundArea): PropPlacement[] {
    const out: PropPlacement[] = [];
    for (const car of this.#cars) {
      if (car.track.zMax < area.zMin || car.track.zMin >= area.zMax) continue;
      const p = this.#place(car, time);
      if (p && p.x >= area.xMin && p.x < area.xMax && p.z >= area.zMin && p.z < area.zMax) {
        out.push(p);
      }
    }
    return out;
  }

  /** How far along its road `car` is at `time`; none near the ends, where it is hidden. */
  #distance(car: Car, time: number): number | undefined {
    const { length } = car.track;
    const s = (((car.start + car.side * car.speed * time) % length) + length) % length;
    // Hidden near the ends, where it turns into the crossing street or leaves the screen.
    return s < this.rules.length || s > length - this.rules.length ? undefined : s;
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
    const [h0, h1] = [track.heights[i] ?? 0, track.heights[i + 1] ?? 0];
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
