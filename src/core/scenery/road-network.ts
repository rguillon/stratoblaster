import { createNoise2D } from '../math/noise';
import { createRng, randomIn, type Random } from '../math/rng';
import type { HeightField } from './height-field';
import { lanesOf, mainRoadWidth, runWidth, withWidth, type Lanes } from './lanes';
import { layPaths, type PathGround } from './road-paths';
import type { RoadRules } from './scenery-level';
import { findDistricts, laidDistricts, type District } from './districts';
import { streetRuns, type Block } from './street-grid';
import { addSlots, SegmentIndex, type RoadSnapshot } from './road-segments';

export type { RoadSnapshot } from './road-segments';

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
  /** Lanes each way: 2 on 2×2 roads (phase 4 review), 3 or 4 on boulevards. */
  readonly lanes: Lanes;
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

/** A main road to follow at a distance, on one side (`noCrossings`). */
interface Follow {
  readonly line: readonly Point[];
  /** -1: on its left (-X), 1: on its right. */
  readonly side: number;
  readonly width: number;
  readonly gap: number;
}

/** Irregular wobble of a main road, as a share of its meander amplitude. */
const WOBBLE = 0.3;
/** When a road cannot leave the screen from its end, it tries again this many points earlier… */
const RETREAT_POINTS = 4;
/** …at most this many times, then the piece is dropped. */
const MAX_RETREATS = 40;
/** Heading of the segment ending at `points[i]`, in radians from +Z, positive towards +X. */
function heading(points: readonly Point[], i: number): number {
  const a = points[Math.max(0, i - 1)];
  const b = points[i];
  return a && b ? Math.atan2(b.x - a.x, b.z - a.z) : 0;
}

/** Rounding left out when a slope is known to be under the steepest a road takes. */
const SLOPE_SLACK = 1e-9;

/** Accepts every road. */
const anyRoad = (): boolean => true;

/** What a {@link RoadNetwork} starts from, besides its ground and rules. */
export interface RoadNetworkOptions {
  /** The roads made before (e.g. in a worker, P13-R03): taken as they are, not generated. */
  readonly made?: RoadSnapshot | undefined;
  /** Where the level's runout starts, if it has one: its streets are laid by `addRunout`. */
  readonly runoutFrom?: number | undefined;
  /** The street grids start no lower than this (the winding roads keep out of them below too). */
  readonly streetsFrom?: number | undefined;
}

/**
 * Randomly generated roads and paths of a level (P04-R07). Main roads wind along the whole
 * level. Where the ground is under `minHeight` (the sea) or steeper than `maxSlope`, a main road
 * turns off the screen before it and comes back from the side after it, so no road ever starts
 * or ends on screen (beyond X = ±`offscreenX`). Paths branch off the main roads at random
 * intervals, widen where they meet them, and run across to past the screen edge; a path that
 * cannot reach it on buildable ground is dropped. Buildings stand only along roads, in slots
 * every `slotSpacing` on both sides. The streets of the runout, past the level's end, are laid
 * apart ({@link addRunout}). Pure and deterministic for a given seed.
 */

export class RoadNetwork {
  #roads: Road[] = [];
  /** The building slots (not kept by {@link snapshot}: only placing the buildings needs them). */
  readonly slots: RoadSlot[] = [];
  /** The blocks between the streets of the districts (phase 4 review). */
  readonly blocks: Block[] = [];
  /** Gap between road edges and building footprints. */
  readonly setback: number;
  /** Roads start and end beyond X = ±offscreenX, out of view. */
  readonly offscreenX: number;
  /** Where the runout starts, if its streets are laid apart (see {@link addRunout}). */
  readonly runoutFrom: number | undefined;
  readonly #segments = new SegmentIndex();
  readonly #seed: number;
  /** Where the street grids start (see `RoadNetworkOptions.streetsFrom`). */
  readonly #streetsFrom: number;
  /** Sections with street grids, kept clear of the winding roads and the paths. */
  readonly #districts: District[];
  /** The districts, or parts of them, in the runout: laid by {@link addRunout}. */
  readonly #runout: District[];
  #runoutLaid = false;
  /** Half width of the main road being laid, kept clear of the others (`noCrossings`). */
  #laying: number | undefined;

  constructor(
    private readonly field: HeightField,
    private readonly rules: RoadRules,
    seed: number,
    /** Z range covered by the main roads; their ends there are out of view. */
    private readonly range: { readonly zMin: number; readonly zMax: number },
    { made, runoutFrom, streetsFrom }: RoadNetworkOptions = {},
  ) {
    this.setback = rules.setback;
    this.offscreenX = rules.offscreenX;
    this.runoutFrom = runoutFrom;
    this.#seed = seed;
    this.#streetsFrom = streetsFrom ?? -Infinity;
    this.#districts = findDistricts(field.sections, range);
    const { before, after } = laidDistricts(this.#districts, { streetsFrom, runoutFrom });
    this.#runout = after;
    if (made) {
      this.#restore(made);
      return;
    }
    const random = createRng(seed + 4);
    // Without crossings, the streets come first: the winding roads and the paths keep clear.
    if (rules.noCrossings) this.#addStreets(before, createRng(seed + 5));
    let previous: Follow | undefined;
    for (let i = 0; i < rules.mainRoads; i++) {
      const width = mainRoadWidth(rules, i);
      const line = this.#mainLine(random, width, previous);
      this.#laying = rules.noCrossings ? width / 2 : undefined;
      this.#addMainPieces(line, width);
      this.#laying = undefined;
      previous = this.#follow(line, previous, width);
    }
    const ground: PathGround = {
      rules,
      range,
      open: (x, z) => this.#open(x, z),
      nearest: (x, z, which) => this.#segments.nearest(x, z, which),
      lay: (points) => {
        this.#addRoad('cross', points);
      },
    };
    layPaths(
      ground,
      random,
      this.#roads.filter((road) => road.kind === 'main'),
    );
    if (!rules.noCrossings) this.#addStreets(before, createRng(seed + 5));
    for (const road of this.#roads) addSlots(road, this.rules.slotSpacing, this.slots);
  }

  /** The roads, the runout's last once laid (a new list then: the old one stays as it was). */
  get roads(): readonly Road[] {
    return this.#roads;
  }

  /**
   * Lays the streets of the runout (reviewer, 2026-10-28: after the rest, so the level is ready
   * sooner), or takes those `made` before (e.g. in a worker), and returns them. Their columns
   * start on the last row laid before the runout. Once only: afterwards, it adds nothing.
   */
  addRunout(made?: readonly Road[]): readonly Road[] {
    if (this.#runoutLaid) return [];
    this.#runoutLaid = true;
    const kept = this.#roads;
    this.#roads = [...kept];
    const from = this.runoutFrom ?? Infinity;
    // A column may end where it starts, on the row laid before (but not where that row was cut).
    const joins = (p: Point): boolean =>
      this.#streetEnds(p) || (p.z <= from && this.edgeDistance(p.x, p.z) < 0);
    if (made) for (const road of made) this.#index(road);
    else this.#addStreets(this.#runout, createRng(this.#seed + 6), joins);
    const added = this.#roads.slice(kept.length);
    // The same list when there is nothing more.
    if (added.length === 0) this.#roads = kept;
    else if (!made) for (const road of added) addSlots(road, this.rules.slotSpacing, this.slots);
    return added;
  }

  /**
   * How the next main road follows `line` without crossing it (`noCrossings`): on the side of
   * the screen the first main road leaves free, at least `gap` from its edge.
   */
  #follow(line: readonly Point[], previous: Follow | undefined, width: number): Follow | undefined {
    const gap = this.rules.noCrossings?.gap;
    if (gap === undefined) return undefined;
    const mean = line.reduce((sum, p) => sum + p.x, 0) / Math.max(1, line.length);
    const side = previous?.side ?? (mean >= 0 ? -1 : 1);
    return { line, side, width, gap };
  }

  /**
   * Distance from (`x`, `z`) to the edge of the nearest road other than `except` (negative on
   * a road), or Infinity when no road is within about `BUCKET` units.
   */
  edgeDistance(x: number, z: number, except?: Road): number {
    return this.#segments.nearest(x, z, except ? (road) => road !== except : anyRoad).distance;
  }

  /**
   * Whether (`x`, `z`) is at least `clearance` from every road edge: `edgeDistance(x, z) >=
   * clearance`, faster (reviewer, 2026-10-28: the props ask this a lot).
   */
  clearOf(x: number, z: number, clearance: number): boolean {
    return this.#segments.clearOf(x, z, clearance);
  }

  /** Whether a road can be built at (`x`, `z`). */
  buildable(x: number, z: number): boolean {
    const { minHeight, maxSlope, step } = this.rules;
    if (!(this.field.height(x, z) >= minHeight)) return false;
    // Reviewer, 2026-10-28: where the ground cannot be that steep, the slope is not measured (it
    // is at most √2 times the most it changes along each axis).
    if (Math.SQRT2 * this.field.steepness(x, z, step) < maxSlope - SLOPE_SLACK) return true;
    return this.field.slope(x, z, step) <= maxSlope;
  }

  /** Whether `p` is off the screen, or at the ends of the generated range (out of view). */
  #offscreen(p: Point): boolean {
    return (
      Math.abs(p.x) >= this.rules.offscreenX ||
      p.z <= this.range.zMin ||
      p.z >= this.range.zMax - this.rules.step
    );
  }

  /** Whether a street may end at `p`: off the screen, or where the street grids start. */
  #streetEnds(p: Point): boolean {
    return this.#offscreen(p) || p.z <= this.#streetsFrom;
  }

  /** A main road's centre line: on its own, or following the previous one (`noCrossings`). */
  #mainLine(random: Random, width: number, previous?: Follow): Point[] {
    const { meander, spread, step } = this.rules;
    const x0 = randomIn(random, [-spread, spread]);
    const amplitude = randomIn(random, meander.amplitude);
    const wavelength = randomIn(random, meander.wavelength);
    const phase = random() * Math.PI * 2;
    const wobble = createNoise2D(Math.floor(random() * 1e9));
    const points: Point[] = [];
    for (let z = this.range.zMin, k = 0; z <= this.range.zMax; z += step, k++) {
      const wave =
        Math.sin((2 * Math.PI * z) / wavelength + phase) + WOBBLE * wobble(z / wavelength, 0.5);
      const followed = previous?.line[k];
      if (previous && followed) {
        // From `gap` to `gap + 2 × amplitude` beside the edge of the road it follows.
        const { side, gap } = previous;
        const apart = gap + (previous.width + width) / 2;
        points.push({ x: followed.x + side * (apart + amplitude * (1 + wave / (1 + WOBBLE))), z });
      } else {
        points.push({ x: x0 + amplitude * wave, z });
      }
    }
    return points;
  }

  /**
   * Lays the buildable runs of a main road line, each made to start and end off the screen: an end
   * on screen gets a turn that leaves the screen sideways (tried earlier and earlier along the
   * run when the ground does not allow it there).
   */
  #addMainPieces(line: readonly Point[], width: number): void {
    let run: Point[] = [];
    // Each piece is laid at once, so the next ones keep clear of it (`noCrossings`).
    const close = (): void => {
      const piece = run.length >= this.rules.minRun ? this.#leaveAtBothEnds(run) : undefined;
      if (piece) this.#addRoad('main', withWidth(piece, width));
      run = [];
    };
    for (const p of line) {
      if (this.#open(p.x, p.z)) run.push(p);
      else close();
    }
    close();
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
   * The straight streets of `districts` (phase 4 review, see `streetRuns`), as `street` roads of
   * the main road width, or wider avenues and boulevards. A street may end on a node `outOfView`
   * accepts (by default, out of view: see {@link #streetEnds}).
   */
  #addStreets(
    districts: readonly District[],
    random: Random,
    outOfView = (p: Point): boolean => this.#streetEnds(p),
  ): void {
    for (const district of districts) {
      const { runs, blocks } = streetRuns(
        district,
        this.rules,
        random,
        (x, z) => this.buildable(x, z),
        outOfView,
      );
      this.blocks.push(...blocks);
      for (const run of runs) {
        this.#addRoad('street', withWidth(run, runWidth(this.rules, run)));
      }
    }
  }

  /**
   * Whether winding roads and paths may go at (`x`, `z`): buildable, out of the districts, and
   * clear of the other roads while a main road is laid without crossings.
   */
  #open(x: number, z: number): boolean {
    return (
      !this.#districts.some((d) => z >= d.zMin && z <= d.zMax) &&
      this.buildable(x, z) &&
      (this.#laying === undefined ||
        this.clearOf(x, z, this.#laying + (this.rules.noCrossings?.gap ?? 0)))
    );
  }

  /** The roads made before, indexed as they were when made (in order). */
  #restore(made: RoadSnapshot): void {
    for (const road of made.roads) this.#index(road);
  }

  /**
   * What this network made (P13-R03): its roads only (reviewer, 2026-10-28: the slots and the
   * blocks are only needed to place the buildings, which are made with it).
   */
  snapshot(): RoadSnapshot {
    return { roads: this.#roads };
  }

  #addRoad(kind: Road['kind'], points: readonly RoadPoint[]): void {
    const width = kind === 'cross' ? this.rules.crossWidth : (points[0]?.width ?? 0);
    const lanes = lanesOf(this.rules, width);
    this.#index({ index: this.#roads.length, kind, width, lanes, points });
  }

  #index(road: Road): void {
    this.#roads.push(road);
    this.#segments.add(road);
  }
}

/** World units of road generated before the start and after the end of a level. */
const LEVEL_MARGIN = 3000;

/**
 * …but a street grid the level starts in only begins this far before it (reviewer, 2026-10-28):
 * the camera sees the ground from Z = 0 at the start, and street grids are the costliest roads to
 * lay. The winding roads and paths still begin {@link LEVEL_MARGIN} before (they cost little).
 */
export const STREETS_BEFORE = 400;

/** The roads of a whole level, a little beyond both ends (the camera sees past them). */
export function levelRoads(
  field: HeightField,
  rules: RoadRules,
  seed: number,
  options: Omit<RoadNetworkOptions, 'streetsFrom'> = {},
): RoadNetwork {
  const range = { zMin: -LEVEL_MARGIN, zMax: field.length + LEVEL_MARGIN };
  return new RoadNetwork(field, rules, seed, range, { ...options, streetsFrom: -STREETS_BEFORE });
}
