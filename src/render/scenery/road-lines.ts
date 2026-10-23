import { inCrossing, streetLines, type StreetLine } from '../../core/scenery/road-traffic';
import type { Road, RoadPoint } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { HeightSource } from './terrain-geometry';

// Phase 4 review: a yellow line along the middle of the streets (stopping where they cross) and
// of the main roads (dashed), painted just above the road surface.

type Rgb = readonly [number, number, number];

/** How the centre lines are painted. */
export interface CentreLineLook {
  readonly color: Rgb;
  readonly width: number;
  /** Length of the dashes of the main roads, and of the gaps between them. */
  readonly dash: number;
  /** Height above the road surface. */
  readonly lift: number;
}

/** The centre line is drawn in pieces this long, so it follows the ground and stops cleanly. */
const PIECE = 2;

interface Painter {
  readonly geo: ColoredGeometry;
  readonly ground: HeightSource;
  readonly look: CentreLineLook;
  /** Height of the road surface above the ground. */
  readonly roadLift: number;
}

/** One flat quad of line from (ax, az) to (bx, bz). */
function quad(paint: Painter, ax: number, az: number, bx: number, bz: number): void {
  const { geo, ground, look } = paint;
  const length = Math.hypot(bx - ax, bz - az) || 1;
  const [nx, nz] = [
    ((bz - az) / length) * (look.width / 2),
    (-(bx - ax) / length) * (look.width / 2),
  ];
  const base = geo.positions.length / 3;
  for (const [x, z] of [
    [ax - nx, az - nz],
    [ax + nx, az + nz],
    [bx - nx, bz - nz],
    [bx + nx, bz + nz],
  ] as const) {
    geo.positions.push(x, ground.height(x, z) + paint.roadLift + look.lift, z);
    geo.colors.push(...look.color, 1);
  }
  // Front faces up, as the road ribbons.
  geo.indices.push(base, base + 1, base + 2, base + 1, base + 3, base + 2);
}

/** Paints the line of the segment from `a` to `b` of `road`, if it starts in [zMin, zMax). */
function paintSegment(
  paint: Painter,
  road: Road,
  [a, b]: readonly [RoadPoint, RoadPoint],
  lines: readonly StreetLine[],
  start: number,
): void {
  const length = Math.hypot(b.x - a.x, b.z - a.z);
  const pieces = Math.max(1, Math.round(length / PIECE));
  for (let k = 0; k < pieces; k++) {
    const [t0, t1] = [k / pieces, (k + 1) / pieces];
    const [ax, az] = [a.x + (b.x - a.x) * t0, a.z + (b.z - a.z) * t0];
    const [bx, bz] = [a.x + (b.x - a.x) * t1, a.z + (b.z - a.z) * t1];
    if (road.kind === 'main') {
      // Dashes and gaps by the distance along the road.
      const along = start + (length * (t0 + t1)) / 2;
      if (Math.floor(along / paint.look.dash) % 2 === 1) continue;
    } else if (
      inCrossing(lines, road.index, ax, az, 0.5) ||
      inCrossing(lines, road.index, bx, bz, 0.5)
    ) {
      continue;
    }
    quad(paint, ax, az, bx, bz);
  }
}

/**
 * Appends to `geo` the centre lines of the streets and main roads whose segments start in
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
