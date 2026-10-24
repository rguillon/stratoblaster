import { smoothstep } from '../math/noise';
import { randomIn, type Random } from '../math/rng';
import type { Road, RoadPoint } from './road-network';
import type { RoadRules } from './scenery-level';

/** What laying the paths needs from the road network. */
export interface PathGround {
  readonly rules: RoadRules;
  /** Z range covered by the roads. */
  readonly range: { readonly zMin: number; readonly zMax: number };
  /** Whether a path may go at (`x`, `z`): buildable, out of the districts. */
  open(x: number, z: number): boolean;
  /** The edge of the nearest road `which` accepts, within about 64 units. */
  nearest(
    x: number,
    z: number,
    which: (road: Road) => boolean,
  ): { readonly distance: number; readonly road?: Road };
  /** Adds a path to the network. */
  lay(points: readonly RoadPoint[]): void;
}

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

/**
 * Paths from points of the main roads to past the screen edge, every `crossSpacing` (P04-R07).
 * Each one tries both directions and a few bends, and is dropped if none stays on buildable
 * ground (and, without crossings, clear of the roads and the paths laid before it).
 */
export function layPaths(ground: PathGround, random: Random, mains: readonly Road[]): void {
  const { crossSpacing, crossBend, offscreenX, step } = ground.rules;
  if (mains.length === 0) return;
  const { zMin, zMax } = ground.range;
  for (
    let z = zMin + randomIn(random, crossSpacing);
    z < zMax;
    z += randomIn(random, crossSpacing)
  ) {
    // A point on screen near `z` of each main road piece that passes there.
    const near = step * PATH_START_SLACK;
    const starts = mains.flatMap((main) => {
      const p = main.points.find((q) => q.z >= z && Math.abs(q.x) < offscreenX);
      return p && p.z - z <= near ? [{ main, p }] : [];
    });
    const start = starts[Math.floor(random() * starts.length)];
    const direction = random() < 0.5 ? -1 : 1;
    const bend = randomIn(random, [-crossBend, crossBend]);
    if (!start) continue;
    const path = PATH_TRIES.map(([d, b]) =>
      pathThrough(ground, pathLine(ground.rules, start.p, d * direction, b * bend), start.main),
    ).find((line) => line !== undefined);
    if (path) ground.lay(path);
  }
}

/** A path checked point by point (`noCrossings`). */
interface Walk {
  /** How far from every road but the one it joins a path keeps. */
  readonly clear: number;
  /** Whether it is clear of its own road yet. */
  left: boolean;
  /** Distance to the road it is running into, once near it. */
  closing: number;
}

/**
 * `line` if a path can go there from its road `from`: on open ground and, without crossings,
 * `gap` clear of every road and path, except where it ends on another main road or street
 * (cut there). Undefined if it cannot.
 */
function pathThrough(ground: PathGround, line: RoadPoint[], from: Road): RoadPoint[] | undefined {
  const gap = ground.rules.noCrossings?.gap;
  if (gap === undefined) {
    return line.slice(1).every((p) => ground.open(p.x, p.z)) ? line : undefined;
  }
  const walk: Walk = { clear: ground.rules.crossWidth / 2 + gap, left: false, closing: Infinity };
  for (let i = 1; i < line.length; i++) {
    const p = line[i];
    const verdict = p ? pathPoint(ground, walk, p, from) : 'blocked';
    if (verdict === 'blocked') return undefined;
    if (verdict === 'end') return line.slice(0, i + 1);
  }
  return line;
}

/** Whether a path goes on through `p`, ends there on another road, or is blocked. */
function pathPoint(
  ground: PathGround,
  walk: Walk,
  p: RoadPoint,
  from: Road,
): 'on' | 'end' | 'blocked' {
  if (!ground.open(p.x, p.z)) return 'blocked';
  // Off its own road for good once clear of it.
  const own = ground.nearest(p.x, p.z, (road) => road === from).distance;
  if (own >= walk.clear) walk.left = true;
  else if (walk.left) return 'blocked';
  const other = ground.nearest(p.x, p.z, (road) => road !== from);
  if (other.distance >= walk.clear) return 'on';
  // Near another road: only a main road or a street, which it must run straight into.
  if (other.road?.kind === 'cross' || other.distance > walk.closing) return 'blocked';
  if (other.distance <= 0) return 'end';
  walk.closing = other.distance;
  return 'on';
}

/** A path from `start` to past the screen edge on the `direction` side, bending by `bend`. */
function pathLine(
  rules: RoadRules,
  start: { readonly x: number; readonly z: number },
  direction: number,
  bend: number,
): RoadPoint[] {
  const { step, offscreenX } = rules;
  const count = Math.ceil((offscreenX - direction * start.x) / step) + 1;
  return Array.from({ length: count + 1 }, (_, i) => ({
    x: start.x + direction * i * step,
    z: start.z + bend * Math.sin((Math.PI * i) / (2 * count)),
    width: pathWidth(rules, i * step),
  }));
}

/** Width of a path `distance` from its junction: wide at the road, narrowing smoothly. */
function pathWidth({ crossWidth, junction }: RoadRules, distance: number): number {
  const t = smoothstep(0, junction.length, distance);
  return junction.width + (crossWidth - junction.width) * t;
}
