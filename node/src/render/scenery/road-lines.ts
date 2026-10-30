import {
  cachedStreetLines,
  inCrossing,
  roadZSpan,
  type StreetLine,
} from '../../core/scenery/road-traffic';
import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { HeightSource } from './terrain-geometry';

// Phase 4 review: a yellow line along the middle of the streets (stopping where they cross) and
// of the main roads (dashed); on wider roads (2×2 to 4×4), a double yellow line and white dashed
// lines between the lanes. Painted just above the road surface.

type Rgb = readonly [number, number, number];

/** How the road markings are painted. */
export interface CentreLineLook {
  readonly color: Rgb;
  /** Colour of the lines between the lanes of 2×2 roads. */
  readonly laneColor: Rgb;
  readonly width: number;
  /** Length of the dashes, and of the gaps between them. */
  readonly dash: number;
  /** Height above the road surface. */
  readonly lift: number;
}

/** Lines are drawn in pieces this long, so they follow the ground and stop cleanly. */
const PIECE = 2;

interface Painter {
  readonly geo: ColoredGeometry;
  readonly ground: HeightSource;
  readonly look: CentreLineLook;
  /** Height of the road surface above the ground. */
  readonly roadLift: number;
}

/** A line along a road: its offset from the centre line, its colour, and whether it is dashed. */
interface Stripe {
  readonly offset: number;
  readonly color: Rgb;
  readonly dashed: boolean;
}

/** The lines painted on `road`. */
function stripes(road: Road, look: CentreLineLook): Stripe[] {
  if (road.lanes === 1) return [{ offset: 0, color: look.color, dashed: road.kind === 'main' }];
  const lane = road.width / (2 * road.lanes);
  // Between the lanes of each side, `lane` apart from the middle.
  const between = Array.from({ length: road.lanes - 1 }, (_, i) => (i + 1) * lane).flatMap(
    (offset) => [-offset, offset].map((o) => ({ offset: o, color: look.laneColor, dashed: true })),
  );
  return [
    { offset: -look.width, color: look.color, dashed: false },
    { offset: look.width, color: look.color, dashed: false },
    ...between,
  ];
}

/** Lines are cut into pieces of {@link PIECE}; pieces in a row merge while the ground under
 * them stays this close to straight (reviewer, 2026-10-28: far fewer quads on flat cities). */
const FLAT = 0.02;

type Point = readonly [number, number];

/** One flat quad of `stripe` from (ax, az) to (bx, bz) of the centre line, at heights ha, hb. */
function quad(
  paint: Painter,
  stripe: Stripe,
  [ax, az]: Point,
  [bx, bz]: Point,
  ha: number,
  hb: number,
): void {
  const { geo, look } = paint;
  const length = Math.hypot(bx - ax, bz - az) || 1;
  const [ux, uz] = [(bz - az) / length, -(bx - ax) / length];
  const [nx, nz] = [ux * (look.width / 2), uz * (look.width / 2)];
  const [sx, sz] = [ux * stripe.offset, uz * stripe.offset];
  const base = geo.positions.length / 3;
  const lift = paint.roadLift + look.lift;
  for (const [x, z, h] of [
    [ax + sx - nx, az + sz - nz, ha],
    [ax + sx + nx, az + sz + nz, ha],
    [bx + sx - nx, bz + sz - nz, hb],
    [bx + sx + nx, bz + sz + nz, hb],
  ] as const) {
    geo.positions.push(x, h + lift, z);
    geo.colors.push(...stripe.color, 1);
  }
  // Front faces up, as the road ribbons.
  geo.indices.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
}

/** Ground height under `stripe` at the centre-line point `p` of a piece going along (dx, dz). */
function heightUnder(paint: Painter, stripe: Stripe, [x, z]: Point, [dx, dz]: Point): number {
  return paint.ground.height(x + dz * stripe.offset, z - dx * stripe.offset);
}

/**
 * Paints `stripe` over the pieces between the centre-line points `at[0..n]`, one quad for as many
 * pieces in a row as the ground under them stays straight.
 */
function paintRun(paint: Painter, stripe: Stripe, at: readonly Point[], dir: Point): void {
  const heights = at.map((p) => heightUnder(paint, stripe, p, dir));
  const h = (k: number) => heights[k] ?? 0;
  const pt = (k: number) => at[k] ?? [0, 0];
  let from = 0;
  while (from < at.length - 1) {
    let to = from + 1;
    while (to + 1 < at.length && straight(heights, from, to + 1)) to++;
    quad(paint, stripe, pt(from), pt(to), h(from), h(to));
    from = to;
  }
}

/** Whether the heights between `from` and `to` lie on the line between theirs. */
function straight(heights: readonly number[], from: number, to: number): boolean {
  const [a, b] = [heights[from] ?? 0, heights[to] ?? 0];
  for (let k = from + 1; k < to; k++) {
    const expected = a + ((b - a) * (k - from)) / (to - from);
    if (Math.abs((heights[k] ?? 0) - expected) > FLAT) return false;
  }
  return true;
}

/** Whether each of the `pieces` pieces of a segment of `road` touches a street crossing it. */
function crossed(
  road: Road,
  lines: readonly StreetLine[],
  at: (k: number) => Point,
  pieces: number,
): boolean[] {
  const ends = Array.from(
    { length: pieces + 1 },
    (_, k) => road.kind === 'street' && inCrossing(lines, road.index, ...at(k), 0.5),
  );
  return Array.from({ length: pieces }, (_, k) => ends[k] === true || ends[k + 1] === true);
}

/** Paints the lines of the segment from `a` to `b` of `road`, `start` along it. */
function paintSegment(
  paint: Painter,
  road: Road,
  [a, b]: readonly [RoadPoint, RoadPoint],
  lines: readonly StreetLine[],
  start: number,
): void {
  const length = Math.hypot(b.x - a.x, b.z - a.z);
  const pieces = Math.max(1, Math.round(length / PIECE));
  const dir = [(b.x - a.x) / (length || 1), (b.z - a.z) / (length || 1)] as const;
  const at = (k: number): Point => [
    a.x + ((b.x - a.x) * k) / pieces,
    a.z + ((b.z - a.z) * k) / pieces,
  ];
  const blocked = crossed(road, lines, at, pieces);
  // Dashes and gaps by the distance along the road.
  const gap = (k: number) =>
    Math.floor((start + (length * (k + 0.5)) / pieces) / paint.look.dash) % 2 === 1;
  for (const stripe of stripes(road, paint.look)) {
    let run: Point[] = [];
    for (let k = 0; k <= pieces; k++) {
      if (k < pieces && !blocked[k] && !(stripe.dashed && gap(k))) run.push(at(k));
      else if (run.length > 0) {
        paintRun(paint, stripe, [...run, at(k)], dir);
        run = [];
      }
    }
  }
}

/**
 * Appends to `geo` the lines of the streets and main roads whose segments start in
 * [zMin, zMax), so neighbouring terrain chunks paint each segment once.
 */
export function paintCentreLines(
  paint: Painter,
  roads: readonly Road[],
  zMin: number,
  zMax: number,
): void {
  const lines = cachedStreetLines(roads);
  for (const road of roads) {
    if (road.kind === 'cross') continue;
    // P13-R04: a road with no point in the range has no segment starting there.
    const [zLow, zHigh] = roadZSpan(road);
    if (zHigh < zMin || zLow >= zMax) continue;
    let along = 0;
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      if (a.z >= zMin && a.z < zMax) paintSegment(paint, road, [a, b], lines, along);
      along += Math.hypot(b.x - a.x, b.z - a.z);
    });
  }
}
