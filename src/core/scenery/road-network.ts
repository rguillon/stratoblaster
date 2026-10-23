import { createNoise2D, smoothstep } from '../math/noise';
import { createRng, randomIn, type Random } from '../math/rng';
import type { HeightField } from './height-field';
import type { RoadRules } from './scenery-level';
import { findDistricts, streetRuns, type Block, type District } from './street-grid';

/** One point of a road's centre line. */
export interface RoadPoint {
  readonly x: number;
  readonly z: number;
  /** Width of the road there (paths widen where they meet a road). */
  readonly width: number;
}

/**
 * A piece of winding road (`main`, along the level), a path (`cross`, branching off a main road)
 * or a straight street of a district (`street`). Every point of it is on buildable ground, and it
 * starts and ends off the screen or at another road.
 */
export interface Road {
  readonly index: number;
  readonly kind: 'main' | 'cross' | 'street';
  /** Nominal width (paths are wider near their junction, see `RoadPoint.width`). */
  readonly width: number;
  readonly points: readonly RoadPoint[];
}

/** A spot by a road where a building may stand, on one side of it. */
export interface RoadSlot {
  readonly road: Road;
  /** Slot number along its road, for hashing. */
  readonly index: number;
  /** Point on the road's centre line. */
  readonly x: number;
  readonly z: number;
  /** Unit vector across the road, towards the side of the slot. */
  readonly nx: number;
  readonly nz: number;
}

interface Point {
  readonly x: number;
  readonly z: number;
}

interface Segment {
  readonly road: Road;
  readonly ax: number;
  readonly az: number;
  readonly bx: number;
  readonly bz: number;
  readonly halfWidth: number;
}

/** Bucket size of the segment index; distance queries see at least this far. */
const BUCKET = 64;
/** Irregular wobble of a main road, as a share of its meander amplitude. */
const WOBBLE = 0.3;
/** When a road cannot leave the screen from its end, it tries again this many points earlier… */
const RETREAT_POINTS = 4;
/** …at most this many times, then the piece is dropped. */
const MAX_RETREATS = 40;
/** A path starts at most this many points from where it was asked for along its road. */
const PATH_START_SLACK = 4;
/** Directions (same / other side) and bends (share of the drawn bend) a path tries in turn. */
const PATH_TRIES: readonly (readonly [number, number])[] = [
  [1, 1],
  [1, -1],
  [1, 0],
  [-1, 1],
  [-1, -1],
  [-1, 0],
];

function segmentDistance(x: number, z: number, s: Segment): number {
  const dx = s.bx - s.ax;
  const dz = s.bz - s.az;
  const length2 = dx * dx + dz * dz;
  const t =
    length2 > 0 ? Math.max(0, Math.min(1, ((x - s.ax) * dx + (z - s.az) * dz) / length2)) : 0;
  return Math.hypot(x - (s.ax + t * dx), z - (s.az + t * dz));
}

/** Heading of the segment ending at `points[i]`, in radians from +Z, positive towards +X. */
function heading(points: readonly Point[], i: number): number {
  const a = points[Math.max(0, i - 1)];
  const b = points[i];
  return a && b ? Math.atan2(b.x - a.x, b.z - a.z) : 0;
}

/**
 * Randomly generated roads and paths of a level (P04-R07). Main roads wind along the whole
 * level. Where the ground is under `minHeight` (the sea) or steeper than `maxSlope`, a main road
 * turns off the screen before it and comes back from the side after it, so no road ever starts
 * or ends on screen (beyond X = ±`offscreenX`). Paths branch off the main roads at random
 * intervals, widen where they meet them, and run across to past the screen edge; a path that
 * cannot reach it on buildable ground is dropped. Buildings stand only along roads, in slots
 * every `slotSpacing` on both sides. Pure and deterministic for a given seed.
 */
export class RoadNetwork {
  readonly roads: Road[] = [];
  readonly slots: RoadSlot[] = [];
  /** The blocks between the streets of the districts (phase 4 review). */
  readonly blocks: Block[] = [];
  /** Gap between road edges and building footprints. */
  readonly setback: number;
  readonly #buckets = new Map<string, Segment[]>();
  /** Sections with street grids, kept clear of the winding roads and the paths. */
  readonly #districts: District[];

  constructor(
    private readonly field: HeightField,
    private readonly rules: RoadRules,
    seed: number,
    /** Z range covered by the main roads; their ends there are out of view. */
    private readonly range: { readonly zMin: number; readonly zMax: number },
  ) {
    this.setback = rules.setback;
    this.#districts = findDistricts(field.sections, range);
    const random = createRng(seed + 4);
    for (let i = 0; i < rules.mainRoads; i++) {
      for (const piece of this.#mainPieces(this.#mainLine(random))) {
        this.#addRoad(
          'main',
          piece.map((p) => ({ ...p, width: rules.mainWidth })),
        );
      }
    }
    const mains = [...this.roads];
    for (const path of this.#paths(random, mains)) this.#addRoad('cross', path);
    this.#addStreets(createRng(seed + 5));
    for (const road of this.roads) this.#index(road);
    for (const road of this.roads) this.#addSlots(road);
  }

  /**
   * Distance from (`x`, `z`) to the edge of the nearest road other than `except` (negative on
   * a road), or Infinity when no road is within about {@link BUCKET} units.
   */
  edgeDistance(x: number, z: number, except?: Road): number {
    const bx = Math.floor(x / BUCKET);
    const bz = Math.floor(z / BUCKET);
    let best = Infinity;
    for (let i = bx - 1; i <= bx + 1; i++) {
      for (let j = bz - 1; j <= bz + 1; j++) {
        for (const s of this.#buckets.get(`${String(i)},${String(j)}`) ?? []) {
          if (s.road !== except) best = Math.min(best, segmentDistance(x, z, s) - s.halfWidth);
        }
      }
    }
    return best;
  }

  /** Whether a road can be built at (`x`, `z`). */
  buildable(x: number, z: number): boolean {
    const { minHeight, maxSlope, step } = this.rules;
    return this.field.height(x, z) >= minHeight && this.field.slope(x, z, step) <= maxSlope;
  }

  /** Whether `p` is off the screen, or at the ends of the generated range (out of view). */
  #offscreen(p: Point): boolean {
    return (
      Math.abs(p.x) >= this.rules.offscreenX ||
      p.z <= this.range.zMin ||
      p.z >= this.range.zMax - this.rules.step
    );
  }

  #mainLine(random: Random): Point[] {
    const { meander, spread, step } = this.rules;
    const x0 = randomIn(random, [-spread, spread]);
    const amplitude = randomIn(random, meander.amplitude);
    const wavelength = randomIn(random, meander.wavelength);
    const phase = random() * Math.PI * 2;
    const wobble = createNoise2D(Math.floor(random() * 1e9));
    const points: Point[] = [];
    for (let z = this.range.zMin; z <= this.range.zMax; z += step) {
      const wave =
        Math.sin((2 * Math.PI * z) / wavelength + phase) + WOBBLE * wobble(z / wavelength, 0.5);
      points.push({ x: x0 + amplitude * wave, z });
    }
    return points;
  }

  /**
   * The buildable runs of a main road line, each made to start and end off the screen: an end
   * on screen gets a turn that leaves the screen sideways (tried earlier and earlier along the
   * run when the ground does not allow it there).
   */
  #mainPieces(line: readonly Point[]): Point[][] {
    const pieces: Point[][] = [];
    let run: Point[] = [];
    const close = (): void => {
      const piece = run.length >= this.rules.minRun ? this.#leaveAtBothEnds(run) : undefined;
      if (piece) pieces.push(piece);
      run = [];
    };
    for (const p of line) {
      if (this.#open(p.x, p.z)) run.push(p);
      else close();
    }
    close();
    return pieces;
  }

  #leaveAtBothEnds(run: Point[]): Point[] | undefined {
    const end = this.#leave(run);
    return end ? this.#leave([...end].reverse())?.reverse() : undefined;
  }

  /** `run`, cut back if needed and ended by a turn that leaves the screen. */
  #leave(run: readonly Point[]): Point[] | undefined {
    const last = run.at(-1);
    if (!last || this.#offscreen(last)) return [...run];
    for (let attempt = 0; attempt <= MAX_RETREATS; attempt++) {
      const i = run.length - 1 - attempt * RETREAT_POINTS;
      const from = run[i];
      if (!from || i + 1 < this.rules.minRun) return undefined;
      const exit = this.#exitTurn(from, heading(run, i));
      if (exit) return [...run.slice(0, i + 1), ...exit];
    }
    return undefined;
  }

  /**
   * Points turning from `from` (heading `start`) towards the nearest side of the screen, then
   * on until off the screen; the other side is tried when that one is not buildable.
   */
  #exitTurn(from: Point, start: number): Point[] | undefined {
    const nearest = from.x >= 0 ? 1 : -1;
    return this.#turnTowards(from, start, nearest) ?? this.#turnTowards(from, start, -nearest);
  }

  #turnTowards(from: Point, start: number, side: number): Point[] | undefined {
    const { step, turnRate, offscreenX } = this.rules;
    // The side's heading (±90°), taken a whole turn from where it is nearest the start heading,
    // so the road turns the short way.
    const side90 = (side * Math.PI) / 2;
    const target = side90 + 2 * Math.PI * Math.round((start - side90) / (2 * Math.PI));
    const maxPoints = Math.ceil((4 * offscreenX) / step);
    const points: Point[] = [];
    let { x, z } = from;
    let h = start;
    for (let k = 0; k < maxPoints; k++) {
      h += Math.max(-turnRate, Math.min(turnRate, target - h));
      x += Math.sin(h) * step;
      z += Math.cos(h) * step;
      if (!this.#open(x, z)) return undefined;
      points.push({ x, z });
      if (side * x >= offscreenX) return points;
    }
    return undefined;
  }

  /**
   * Paths from points of the main roads to past the screen edge, every `crossSpacing`. Each one
   * tries both directions and a few bends, and is dropped if none stays on buildable ground.
   */
  #paths(random: Random, mains: readonly Road[]): RoadPoint[][] {
    const { crossSpacing, crossBend, offscreenX } = this.rules;
    const paths: RoadPoint[][] = [];
    if (mains.length === 0) return paths;
    const { zMin, zMax } = this.range;
    for (
      let z = zMin + randomIn(random, crossSpacing);
      z < zMax;
      z += randomIn(random, crossSpacing)
    ) {
      // A point on screen near `z` of each main road piece that passes there.
      const near = this.rules.step * PATH_START_SLACK;
      const starts = mains.flatMap((main) => {
        const p = main.points.find((q) => q.z >= z && Math.abs(q.x) < offscreenX);
        return p && p.z - z <= near ? [p] : [];
      });
      const start = starts[Math.floor(random() * starts.length)];
      const direction = random() < 0.5 ? -1 : 1;
      const bend = randomIn(random, [-crossBend, crossBend]);
      if (!start) continue;
      const path = PATH_TRIES.map(([d, b]) => this.#pathLine(start, d * direction, b * bend)).find(
        (line) => line.slice(1).every((p) => this.#open(p.x, p.z)),
      );
      if (path) paths.push(path);
    }
    return paths;
  }

  /** A path from `start` to past the screen edge on the `direction` side, bending by `bend`. */
  #pathLine(start: Point, direction: number, bend: number): RoadPoint[] {
    const { step, offscreenX } = this.rules;
    const count = Math.ceil((offscreenX - direction * start.x) / step) + 1;
    return Array.from({ length: count + 1 }, (_, i) => ({
      x: start.x + direction * i * step,
      z: start.z + bend * Math.sin((Math.PI * i) / (2 * count)),
      width: this.#pathWidth(i * step),
    }));
  }

  /**
   * The straight streets of the districts (phase 4 review, see `streetRuns`), as `street`
   * roads of the main road width.
   */
  #addStreets(random: Random): void {
    for (const district of this.#districts) {
      const { runs, blocks } = streetRuns(
        district,
        this.rules,
        random,
        (x, z) => this.buildable(x, z),
        (p) => this.#offscreen(p),
      );
      this.blocks.push(...blocks);
      for (const run of runs) {
        this.#addRoad(
          'street',
          run.map((p) => ({ ...p, width: this.rules.mainWidth })),
        );
      }
    }
  }

  /** Whether winding roads and paths may go at (`x`, `z`): buildable, out of the districts. */
  #open(x: number, z: number): boolean {
    return !this.#districts.some((d) => z >= d.zMin && z <= d.zMax) && this.buildable(x, z);
  }

  /** Width of a path `distance` from its junction: wide at the road, narrowing smoothly. */
  #pathWidth(distance: number): number {
    const { crossWidth, junction } = this.rules;
    const t = smoothstep(0, junction.length, distance);
    return junction.width + (crossWidth - junction.width) * t;
  }

  #addRoad(kind: Road['kind'], points: readonly RoadPoint[]): void {
    const width = kind === 'cross' ? this.rules.crossWidth : this.rules.mainWidth;
    this.roads.push({ index: this.roads.length, kind, width, points });
  }

  #index(road: Road): void {
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      const halfWidth = Math.max(a.width, b.width) / 2;
      const segment = { road, ax: a.x, az: a.z, bx: b.x, bz: b.z, halfWidth };
      const keys = new Set(
        [a, b].map(
          (p) => `${String(Math.floor(p.x / BUCKET))},${String(Math.floor(p.z / BUCKET))}`,
        ),
      );
      for (const key of keys) {
        const bucket = this.#buckets.get(key);
        if (bucket) bucket.push(segment);
        else this.#buckets.set(key, [segment]);
      }
    });
  }

  /** Slots every `slotSpacing` along a road, on both sides. */
  #addSlots(road: Road): void {
    const { slotSpacing } = this.rules;
    let travelled = slotSpacing / 2;
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      const length = Math.hypot(b.x - a.x, b.z - a.z);
      if (length === 0) return;
      const [tx, tz] = [(b.x - a.x) / length, (b.z - a.z) / length];
      for (; travelled < length; travelled += slotSpacing) {
        const t = travelled / length;
        const x = a.x + (b.x - a.x) * t;
        const z = a.z + (b.z - a.z) * t;
        const index = this.slots.length;
        this.slots.push(
          { road, index, x, z, nx: tz, nz: -tx },
          { road, index: index + 1, x, z, nx: -tz, nz: tx },
        );
      }
      travelled -= length;
    });
  }
}

/** World units of road generated before the start and after the end of a level. */
const LEVEL_MARGIN = 3000;

/** The roads of a whole level, a little beyond both ends (the camera sees past them). */
export function levelRoads(field: HeightField, rules: RoadRules, seed: number): RoadNetwork {
  return new RoadNetwork(field, rules, seed, {
    zMin: -LEVEL_MARGIN,
    zMax: field.length + LEVEL_MARGIN,
  });
}
