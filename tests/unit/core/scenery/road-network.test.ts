import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { levelRoads, RoadNetwork } from '../../../../src/core/scenery/road-network';
import type { RoadRules, SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const RULES: RoadRules = {
  ...SAMPLE_SCENERY_LEVEL.roads,
  mainRoads: 2,
  spread: 100,
  meander: { amplitude: [20, 60], wavelength: [300, 600] },
  crossSpacing: [80, 160],
  crossLength: [60, 120],
  crossBend: 20,
};
const RANGE = { zMin: 0, zMax: 1000 };

function network(level: SceneryLevel = SAMPLE_SCENERY_LEVEL, rules = RULES, seed = 3): RoadNetwork {
  return new RoadNetwork(new HeightField(level), rules, seed, RANGE);
}

describe('RoadNetwork', () => {
  it('P04-R07: generates winding main roads over the range and paths branching off them', () => {
    const roads = network().roads;
    const mains = roads.filter((r) => r.kind === 'main');
    const paths = roads.filter((r) => r.kind === 'cross');
    expect(mains).toHaveLength(2);
    expect(paths.length).toBeGreaterThan(4);
    for (const main of mains) {
      expect(main.points[0]?.z).toBe(0);
      expect(main.points.at(-1)?.z).toBeGreaterThan(990);
      expect(main.width).toBe(RULES.mainWidth);
      const xs = main.points.map((p) => p.x);
      expect(Math.max(...xs) - Math.min(...xs)).toBeGreaterThan(10);
    }
    for (const path of paths) {
      const start = path.points[0];
      if (!start) throw new Error('empty path');
      // A path starts on a main road.
      expect(
        Math.min(
          ...mains.map((m) =>
            Math.min(...m.points.map((p) => Math.hypot(p.x - start.x, p.z - start.z))),
          ),
        ),
      ).toBeLessThan(1e-6);
      expect(path.width).toBe(RULES.crossWidth);
    }
  });

  it('P04-R07: is random, but the same for the same seed', () => {
    const key = (n: RoadNetwork) => JSON.stringify(n.roads.map((r) => r.points));
    expect(key(network())).toBe(key(network()));
    expect(key(network(SAMPLE_SCENERY_LEVEL, RULES, 4))).not.toBe(key(network()));
  });

  it('P04-R07: roads break under the sea and on steep ground, and drop short pieces', () => {
    const sunk: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
        ...s,
        relief: { ...s.relief, base: -10 },
      })),
    };
    const roads = network(sunk).roads;
    expect(roads.every((r) => r.points.every((p) => !p.valid))).toBe(true);
    expect(network(sunk).slots).toEqual([]);
    expect(network(SAMPLE_SCENERY_LEVEL, { ...RULES, minRun: 100_000 }).slots).toEqual([]);
  });

  it('P04-R07: slots line both sides of the valid roads, every slotSpacing', () => {
    const straight = network(SAMPLE_SCENERY_LEVEL, SAMPLE_SCENERY_LEVEL.roads);
    const main = straight.roads[0];
    const slots = straight.slots.filter((s) => s.road === main);
    expect(slots.length).toBeGreaterThan(80);
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
    expect(straight.edgeDistance(10, 500)).toBeCloseTo(7);
    expect(straight.edgeDistance(0, 500)).toBeCloseTo(-3);
    expect(straight.edgeDistance(10, 500, main)).toBe(Infinity);
    expect(straight.edgeDistance(500, 500)).toBe(Infinity);
  });

  it('levelRoads covers the whole level and beyond both ends', () => {
    const field = new HeightField(SAMPLE_SCENERY_LEVEL);
    const main = levelRoads(field, SAMPLE_SCENERY_LEVEL.roads, 1).roads[0];
    expect(main?.points[0]?.z).toBeLessThan(-1000);
    expect(main?.points.at(-1)?.z).toBeGreaterThan(field.length + 1000);
  });
});
