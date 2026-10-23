import { hash2D } from '../math/noise';
import type { GroundArea, PropPlacement } from './prop-placement';
import type { Road, RoadPoint } from './road-network';
import type { CarRules } from './scenery-level';

// Phase 4 review: cars on the streets and main roads, and where streets cross each other (no
// car stands there, and the centre line stops there).

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

/** Unit direction of a road at its point `i`. */
export function roadDirection(points: readonly RoadPoint[], i: number): [number, number] {
  const a = points[Math.max(0, i - 1)];
  const b = points[Math.min(points.length - 1, i + 1)];
  if (!a || !b) return [0, 1];
  const length = Math.hypot(b.x - a.x, b.z - a.z) || 1;
  return [(b.x - a.x) / length, (b.z - a.z) / length];
}

/** The car standing at point `i` of `road`, if any, in its lane and facing its way. */
function carAt(
  road: Road,
  i: number,
  rules: CarRules,
  seed: number,
): Omit<PropPlacement, 'y'> | undefined {
  const p = road.points[i];
  const r = (draw: number): number => hash2D(road.index * 7 + draw, i, seed * 13 + 5);
  if (!p || r(0) >= rules.density) return undefined;
  const [dx, dz] = roadDirection(road.points, i);
  // Right-hand traffic: a car on the right of the road's direction drives along it.
  const side = r(1) < 0.5 ? 1 : -1;
  const kind = rules.kinds[Math.floor(r(2) * rules.kinds.length)];
  if (kind === undefined) return undefined;
  return {
    kind,
    x: p.x + dz * side * rules.laneOffset,
    z: p.z - dx * side * rules.laneOffset,
    rotation: Math.atan2(dx, dz) + (side > 0 ? 0 : Math.PI),
    scale: rules.scale,
  };
}

/**
 * Cars of `rules` on the streets and main roads (not the paths) whose position lies in `area`,
 * none where streets cross. Decided by a hash of the road and point, so the same place always
 * gets the same cars, whatever area is asked for.
 */
export function placeCars(
  roads: readonly Road[],
  height: (x: number, z: number) => number,
  rules: CarRules,
  seed: number,
  area: GroundArea,
): PropPlacement[] {
  const inArea = (x: number, z: number): boolean =>
    x >= area.xMin && x < area.xMax && z >= area.zMin && z < area.zMax;
  const lines = streetLines(roads);
  const cars: PropPlacement[] = [];
  for (const road of roads) {
    if (road.kind === 'cross') continue;
    for (let i = 0; i < road.points.length; i++) {
      const car = carAt(road, i, rules, seed);
      if (!car || !inArea(car.x, car.z)) continue;
      if (road.kind === 'street' && inCrossing(lines, road.index, car.x, car.z, rules.length)) {
        continue;
      }
      cars.push({ ...car, y: height(car.x, car.z) + rules.lift });
    }
  }
  return cars;
}
