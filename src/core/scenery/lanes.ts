import { hash2D } from '../math/noise';
import type { RoadPoint } from './road-network';
import type { RoadRules } from './scenery-level';

// Phase 4 review: roads of one lane each way, and 2×2 roads (two lanes each way): the first
// main roads, and some lines of the street grids (avenues).

/** Lanes each way of a road `width` wide. */
export function lanesOf(rules: RoadRules, width: number): 1 | 2 {
  return width >= rules.dual.width ? 2 : 1;
}

/** Width of main road number `index`: the first `dual.mainRoads` are 2×2. */
export function mainRoadWidth(rules: RoadRules, index: number): number {
  return index < rules.dual.mainRoads ? rules.dual.width : rules.mainWidth;
}

/**
 * Width of the street along a line of a street grid (`coord`: X of a column, Z of a row): a
 * share `dual.avenues` of the lines are 2×2 avenues, decided by a hash of the line.
 */
export function streetWidth(rules: RoadRules, coord: number): number {
  return hash2D(Math.round(coord), 17, 101) < rules.dual.avenues
    ? rules.dual.width
    : rules.mainWidth;
}

/** Width of a straight run of a street grid: a row (along X) or a column, as wide as its line. */
export function runWidth(rules: RoadRules, run: readonly { x: number; z: number }[]): number {
  const [a, b] = [run[0], run.at(-1)];
  if (!a || !b) return rules.mainWidth;
  return streetWidth(rules, a.z === b.z ? a.z : a.x);
}

/** `points` of a road `width` wide. */
export function withWidth(points: readonly { x: number; z: number }[], width: number): RoadPoint[] {
  return points.map((p) => ({ ...p, width }));
}
