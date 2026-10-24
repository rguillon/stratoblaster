import { expect } from 'vitest';
import { HeightField } from '../../src/core/scenery/height-field';
import { RoadNetwork, type Road } from '../../src/core/scenery/road-network';
import type { RoadRules, SceneryLevel } from '../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../fixtures/sample-scenery';

/* Road networks of the sample level, for the road tests. */

export const RULES: RoadRules = {
  ...SAMPLE_SCENERY_LEVEL.roads,
  mainRoads: 2,
  spread: 40,
  meander: { amplitude: [20, 50], wavelength: [300, 600] },
  crossSpacing: [80, 160],
  crossBend: 20,
};
export const RANGE = { zMin: 0, zMax: 1000 };
/** The sample level without its cliff: the low ground all along. */
export const FLAT: SceneryLevel = {
  ...SAMPLE_SCENERY_LEVEL,
  sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
    ...s,
    relief: SAMPLE_SCENERY_LEVEL.sections[0]?.relief ?? s.relief,
  })),
};

export function network(
  level: SceneryLevel = SAMPLE_SCENERY_LEVEL,
  rules = RULES,
  seed = 3,
): RoadNetwork {
  return new RoadNetwork(new HeightField(level), rules, seed, RANGE);
}

/** Whether a road end is out of view: past the screen edge, or at the ends of the range. */
export function offscreen(rules: RoadRules, p: { x: number; z: number } | undefined): boolean {
  if (!p) return false;
  return Math.abs(p.x) >= rules.offscreenX || p.z <= RANGE.zMin || p.z >= RANGE.zMax - rules.step;
}

/**
 * A street is straight (across or along the level), inside its district's Z range, and each end
 * is off the screen or on another road.
 */
export function checkStreet(
  n: RoadNetwork,
  street: Road,
  [zMin, zMax]: readonly [number, number],
): void {
  const xs = new Set(street.points.map((p) => p.x.toFixed(6)));
  const zs = new Set(street.points.map((p) => p.z.toFixed(6)));
  expect(xs.size === 1 || zs.size === 1).toBe(true);
  const z = street.points.map((p) => p.z);
  expect(Math.min(...z)).toBeGreaterThanOrEqual(zMin - 1e-6);
  expect(Math.max(...z)).toBeLessThanOrEqual(zMax + 1e-6);
  for (const end of [street.points[0], street.points.at(-1)]) {
    if (end && !offscreen(RULES, end)) {
      expect(n.edgeDistance(end.x, end.z, street)).toBeLessThanOrEqual(0);
    }
  }
}
