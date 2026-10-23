import type { Road } from './road-network';

// Phase 4 review: where streets cross each other (the centre line stops there, and a street
// meeting another goes on under it).

/** A straight street, from its first to its last point. */
export interface StreetLine {
  readonly road: number;
  readonly ax: number;
  readonly az: number;
  readonly bx: number;
  readonly bz: number;
  readonly width: number;
}

/** The streets of `roads` as straight lines (streets are straight, see `streetRuns`). */
export function streetLines(roads: readonly Road[]): StreetLine[] {
  return roads.flatMap((road) => {
    const [a, b] = [road.points[0], road.points.at(-1)];
    if (road.kind !== 'street' || !a || !b) return [];
    return [{ road: road.index, ax: a.x, az: a.z, bx: b.x, bz: b.z, width: road.width }];
  });
}

function distance(line: StreetLine, x: number, z: number): number {
  const [dx, dz] = [line.bx - line.ax, line.bz - line.az];
  const t = Math.max(
    0,
    Math.min(1, ((x - line.ax) * dx + (z - line.az) * dz) / (dx * dx + dz * dz || 1)),
  );
  return Math.hypot(line.ax + t * dx - x, line.az + t * dz - z);
}

/** Whether (x, z) of street `road` is within `margin` of the edge of another street. */
export function inCrossing(
  lines: readonly StreetLine[],
  road: number,
  x: number,
  z: number,
  margin: number,
): boolean {
  return lines.some((l) => l.road !== road && distance(l, x, z) < l.width / 2 + margin);
}

/** Width of the widest other street that (x, z) of street `road` lies on, if any. */
export function meetingWidth(
  lines: readonly StreetLine[],
  road: number,
  x: number,
  z: number,
): number | undefined {
  const widths = lines
    .filter((l) => l.road !== road && distance(l, x, z) < 0.5)
    .map((l) => l.width);
  return widths.length > 0 ? Math.max(...widths) : undefined;
}
