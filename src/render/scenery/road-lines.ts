import { inCrossing, streetLines, type StreetLine } from '../../core/scenery/road-traffic';
import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { HeightSource } from './terrain-geometry';

// Phase 4 review: a yellow line along the middle of the streets (stopping where they cross) and
// of the main roads (dashed); on 2×2 roads, a double yellow line and white dashed lines between
// the lanes. Painted just above the road surface.

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
  const lane = road.width / 4;
  return [
    { offset: -look.width, color: look.color, dashed: false },
    { offset: look.width, color: look.color, dashed: false },
    { offset: -lane, color: look.laneColor, dashed: true },
    { offset: lane, color: look.laneColor, dashed: true },
  ];
}

/** One flat quad of `stripe` along the piece from (ax, az) to (bx, bz) of the centre line. */
function quad(
  paint: Painter,
  stripe: Stripe,
  [ax, az]: readonly [number, number],
  [bx, bz]: readonly [number, number],
): void {
  const { geo, ground, look } = paint;
  const length = Math.hypot(bx - ax, bz - az) || 1;
  const [ux, uz] = [(bz - az) / length, -(bx - ax) / length];
  const [nx, nz] = [ux * (look.width / 2), uz * (look.width / 2)];
  const [sx, sz] = [ux * stripe.offset, uz * stripe.offset];
  const base = geo.positions.length / 3;
  for (const [x, z] of [
    [ax + sx - nx, az + sz - nz],
    [ax + sx + nx, az + sz + nz],
    [bx + sx - nx, bz + sz - nz],
    [bx + sx + nx, bz + sz + nz],
  ] as const) {
    geo.positions.push(x, ground.height(x, z) + paint.roadLift + look.lift, z);
    geo.colors.push(...stripe.color, 1);
  }
  // Front faces up, as the road ribbons.
  geo.indices.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
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
  const painted = stripes(road, paint.look);
  for (let k = 0; k < pieces; k++) {
    const [t0, t1] = [k / pieces, (k + 1) / pieces];
    const from = [a.x + (b.x - a.x) * t0, a.z + (b.z - a.z) * t0] as const;
    const to = [a.x + (b.x - a.x) * t1, a.z + (b.z - a.z) * t1] as const;
    const crossing =
      road.kind === 'street' &&
      (inCrossing(lines, road.index, ...from, 0.5) || inCrossing(lines, road.index, ...to, 0.5));
    // Dashes and gaps by the distance along the road.
    const gap = Math.floor((start + (length * (t0 + t1)) / 2) / paint.look.dash) % 2 === 1;
    for (const stripe of painted) {
      if (!crossing && !(stripe.dashed && gap)) quad(paint, stripe, from, to);
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
  const lines = streetLines(roads);
  for (const road of roads) {
    if (road.kind === 'cross') continue;
    let along = 0;
    road.points.forEach((a, i) => {
      const b = road.points[i + 1];
      if (!b) return;
      if (a.z >= zMin && a.z < zMax) paintSegment(paint, road, [a, b], lines, along);
      along += Math.hypot(b.x - a.x, b.z - a.z);
    });
  }
}
