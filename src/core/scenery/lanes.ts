import { hash2D } from '../math/noise';
import type { RoadPoint } from './road-network';
import type { RoadRules } from './scenery-level';

// Phase 4 review: roads of one lane each way, and 2×2 roads (two lanes each way): the first
// main roads, and some lines of the street grids (avenues); reviewer, 2026-10-28: 3×3 and 4×4
// boulevards in the street grids.

/** Lanes each way of a road. */
export type Lanes = 1 | 2 | 3 | 4;

/** Lanes each way of a road `width` wide. */
export function lanesOf(rules: RoadRules, width: number): Lanes {
  const boulevard = rules.boulevards?.find((b) => b.width === width);
  if (boulevard) return boulevard.lanes;
  return width >= rules.dual.width ? 2 : 1;
}

/** Whether `width` is a boulevard's (see `RoadRules.boulevards`). */
export function isBoulevard(rules: RoadRules, width: number): boolean {
  return rules.boulevards?.some((b) => b.width === width) ?? false;
}

/** Width of main road number `index`: the first `dual.mainRoads` are 2×2. */
export function mainRoadWidth(rules: RoadRules, index: number): number {
  return index < rules.dual.mainRoads ? rules.dual.width : rules.mainWidth;
}

/**
 * Width of the street along a line of a street grid (`coord`: X of a column, Z of a row),
 * decided by a hash of the line: a share of the lines are boulevards, of each kind in turn, then
 * a share `dual.avenues` 2×2 avenues, the others one lane each way.
 */
export function streetWidth(rules: RoadRules, coord: number): number {
  const h = hash2D(Math.round(coord), 17, 101);
  let from = 0;
  for (const b of rules.boulevards ?? []) {
    if (h < from + b.share) return b.width;
    from += b.share;
  }
  return h < from + rules.dual.avenues ? rules.dual.width : rules.mainWidth;
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
