import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { levelRoads, RoadNetwork, type Road } from '../../../../src/core/scenery/road-network';
import type { RoadRules, SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const RULES: RoadRules = {
  ...SAMPLE_SCENERY_LEVEL.roads,
  mainRoads: 2,
  spread: 40,
  meander: { amplitude: [20, 50], wavelength: [300, 600] },
  crossSpacing: [80, 160],
  crossBend: 20,
};
const RANGE = { zMin: 0, zMax: 1000 };

function network(level: SceneryLevel = SAMPLE_SCENERY_LEVEL, rules = RULES, seed = 3): RoadNetwork {
  return new RoadNetwork(new HeightField(level), rules, seed, RANGE);
}

/** Whether a road end is out of view: past the screen edge, or at the ends of the range. */
function offscreen(rules: RoadRules, p: { x: number; z: number } | undefined): boolean {
  if (!p) return false;
  return Math.abs(p.x) >= rules.offscreenX || p.z <= RANGE.zMin || p.z >= RANGE.zMax - rules.step;
}

/** A level whose ground rises steeply in the middle: main roads cannot go through. */
const RIDGE: SceneryLevel = {
  ...SAMPLE_SCENERY_LEVEL,
  transition: 4,
  sections: [
    { ...SAMPLE_SCENERY_LEVEL.sections[0], name: 'low', seconds: 20 },
    {
      ...SAMPLE_SCENERY_LEVEL.sections[0],
      name: 'cliff',
      seconds: 5,
      relief: { base: 10, amplitude: 300, frequency: 1 / 20, octaves: 2, style: 'smooth' },
    },
    { ...SAMPLE_SCENERY_LEVEL.sections[0], name: 'low again', seconds: 25 },
  ] as SceneryLevel['sections'],
};

describe('RoadNetwork', () => {
  it('P04-R07: generates winding main roads over the range and paths branching off them', () => {
    const roads = network().roads;
    const mains = roads.filter((r) => r.kind === 'main');
    const paths = roads.filter((r) => r.kind === 'cross');
    expect(mains.length).toBeGreaterThanOrEqual(2);
    expect(paths.length).toBeGreaterThan(4);
    for (const main of mains) {
      const xs = main.points.map((p) => p.x);
      expect(Math.max(...xs) - Math.min(...xs)).toBeGreaterThan(10);
      expect(main.points.every((p) => p.width === RULES.mainWidth)).toBe(true);
    }
    const mainPoints = mains.flatMap((m) => m.points);
    for (const path of paths) {
      const start = path.points[0];
      if (!start) throw new Error('empty path');
      // A path starts on a main road.
      expect(mainPoints.some((p) => p.x === start.x && p.z === start.z)).toBe(true);
    }
  });

  it('P04-R07: is random, but the same for the same seed', () => {
    const key = (n: RoadNetwork) => JSON.stringify(n.roads.map((r) => r.points));
    expect(key(network())).toBe(key(network()));
    expect(key(network(SAMPLE_SCENERY_LEVEL, RULES, 4))).not.toBe(key(network()));
  });

  it('P04 review: every road and path starts and ends off the screen, on buildable ground', () => {
    for (const n of [network(), network(RIDGE)]) {
      expect(n.roads.length).toBeGreaterThan(0);
      for (const road of n.roads) {
        const [first, last] = [road.points[0], road.points.at(-1)];
        // A path starts at its junction with a main road; everything else starts off screen.
        if (road.kind === 'main') expect(offscreen(RULES, first)).toBe(true);
        expect(offscreen(RULES, last)).toBe(true);
        for (const p of road.points.slice(1)) expect(n.buildable(p.x, p.z)).toBe(true);
      }
    }
  });

  it('P04 review: a main road that cannot go on turns off the screen and comes back after', () => {
    const n = network(RIDGE, { ...RULES, mainRoads: 1 });
    const mains = n.roads.filter((r) => r.kind === 'main');
    expect(mains).toHaveLength(2);
    const [before, after] = mains as [Road, Road];
    expect(Math.abs(before.points.at(-1)?.x ?? 0)).toBeGreaterThanOrEqual(RULES.offscreenX);
    expect(Math.abs(after.points[0]?.x ?? 0)).toBeGreaterThanOrEqual(RULES.offscreenX);
    expect(before.points.at(-1)?.z ?? 0).toBeLessThan(after.points[0]?.z ?? 0);
  });

  it('P04 review: paths widen where they meet the road, and narrow back to their width', () => {
    const paths = network().roads.filter((r) => r.kind === 'cross');
    for (const path of paths) {
      const widths = path.points.map((p) => p.width);
      expect(widths[0]).toBe(RULES.junction.width);
      expect(widths.at(-1)).toBe(RULES.crossWidth);
      widths.slice(1).forEach((w, i) => {
        expect(w).toBeLessThanOrEqual(widths[i] ?? Infinity);
      });
    }
  });

  it('P04-R07: no road where the ground is under the sea', () => {
    const sunk: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
        ...s,
        relief: { ...s.relief, base: -10 },
      })),
    };
    expect(network(sunk).roads).toEqual([]);
    expect(network(sunk).slots).toEqual([]);
  });

  it('P04-R07: slots line both sides of the roads, every slotSpacing', () => {
    const straight = network(SAMPLE_SCENERY_LEVEL, SAMPLE_SCENERY_LEVEL.roads);
    const main = straight.roads[0];
    const slots = straight.slots.filter((s) => s.road === main);
    expect(slots.length).toBeGreaterThan(40);
    const [a, b, c] = slots;
    if (!a || !b || !c) throw new Error('missing slots');
    expect(a.z).toBeCloseTo(SAMPLE_SCENERY_LEVEL.roads.slotSpacing / 2);
    expect(b.z).toBe(a.z);
    expect(a.nx + b.nx).toBeCloseTo(0);
    expect(Math.abs(a.nx)).toBeCloseTo(1);
    expect(c.z - a.z).toBeCloseTo(SAMPLE_SCENERY_LEVEL.roads.slotSpacing);
  });

  it('measures the distance to the nearest road edge, except one road', () => {
    const straight = network(SAMPLE_SCENERY_LEVEL, {
      ...SAMPLE_SCENERY_LEVEL.roads,
      crossSpacing: [5000, 5000],
    });
    const main = straight.roads[0];
    // One straight road along X = 0, 6 wide.
    expect(straight.edgeDistance(10, 100)).toBeCloseTo(7);
    expect(straight.edgeDistance(0, 100)).toBeCloseTo(-3);
    expect(straight.edgeDistance(10, 100, main)).toBe(Infinity);
    expect(straight.edgeDistance(500, 100)).toBe(Infinity);
  });

  it('levelRoads covers the whole level and beyond both ends', () => {
    const field = new HeightField(SAMPLE_SCENERY_LEVEL);
    const roads = levelRoads(field, SAMPLE_SCENERY_LEVEL.roads, 1).roads;
    const zs = roads.filter((r) => r.kind === 'main').flatMap((r) => r.points.map((p) => p.z));
    expect(Math.min(...zs)).toBeLessThan(-1000);
    expect(Math.max(...zs)).toBeGreaterThan(field.length + 1000);
  });
});
