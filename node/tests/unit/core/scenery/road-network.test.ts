import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import {
  levelRoads,
  RoadNetwork,
  STREETS_BEFORE,
  type Road,
} from '../../../../src/core/scenery/road-network';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { GAME } from '../../../../src/game/index';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';
import { checkStreet, FLAT, network, offscreen, RULES } from '../../../helpers/road-network';

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

  it('P04 review: a district gets straight streets that only end at another street or off screen', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const district: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [
        { ...flat, name: 'open', seconds: 20 },
        {
          ...flat,
          name: 'town',
          seconds: 15,
          streets: { rows: [30, 40], columns: [25, 35], links: 0.6 },
        },
        { ...flat, name: 'open again', seconds: 15 },
      ],
    };
    const n = network(district);
    const streets = n.roads.filter((r) => r.kind === 'street');
    expect(streets.length).toBeGreaterThan(5);
    for (const street of streets) checkStreet(n, street, [400, 700]);
    // The town's first and last rows are full streets.
    for (const z of [400, 700]) {
      const row = streets.filter((r) => r.points.every((p) => Math.abs(p.z - z) < 1e-6));
      const xs = row.flatMap((r) => r.points.map((p) => p.x));
      expect(Math.min(...xs)).toBeLessThan(-RULES.offscreenX);
      expect(Math.max(...xs)).toBeGreaterThan(RULES.offscreenX);
    }
    // The winding roads and the paths stay out of the town.
    for (const road of n.roads.filter((r) => r.kind !== 'street')) {
      for (const p of road.points) expect(p.z < 400 || p.z > 700).toBe(true);
    }
    expect(n.slots.some((slot) => slot.road.kind === 'street')).toBe(true);
  });

  it('P04 review: the blocks between the streets leave no bare ground', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const district: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [
        { ...flat, name: 'open', seconds: 20 },
        {
          ...flat,
          name: 'town',
          seconds: 15,
          streets: { rows: [30, 40], columns: [25, 35], links: 0.7 },
        },
        { ...flat, name: 'open again', seconds: 15 },
      ],
    };
    const n = network(district);
    expect(n.blocks.length).toBeGreaterThan(20);
    const inBlock = (x: number, z: number) =>
      n.blocks.some((b) => x >= b.xMin && x <= b.xMax && z >= b.zMin && z <= b.zMax);
    for (let x = -RULES.offscreenX + 5; x < RULES.offscreenX - 5; x += 3.3) {
      for (let z = 410; z < 690; z += 3.7) {
        // Every point is on a street (or its kerb), or in a block.
        expect(
          inBlock(x, z) || n.edgeDistance(x, z) <= 0.5 + 1e-6,
          `${String(x)}, ${String(z)}`,
        ).toBe(true);
      }
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
    // On flat ground: the sample level's cliff would turn the road off the screen (review).
    const straight = network(FLAT, SAMPLE_SCENERY_LEVEL.roads);
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

  it('reviewer, 2026-10-28: a street grid the level starts in begins only a little before it', () => {
    const scenery = GAME.gameLevels.find((l) => l.id === '4-1')?.scenery;
    if (!scenery) throw new Error('no level 4-1');
    const field = new HeightField(scenery);
    const roads = levelRoads(field, scenery.roads, scenery.seed).roads;
    const zs = roads.flatMap((r) => r.points.map((p) => p.z));
    expect(roads.every((r) => r.kind === 'street')).toBe(true);
    // Within the first tile (phase 15): the streets run along the middles of the tiles.
    expect(Math.min(...zs)).toBeGreaterThanOrEqual(-STREETS_BEFORE);
    expect(Math.min(...zs)).toBeLessThan(-STREETS_BEFORE + 10);
  });
});

describe('clearOf (reviewer, 2026-10-28)', () => {
  it('says the same as edgeDistance, near the roads and away from them', () => {
    const roads = network();
    let near = 0;
    for (let x = -300; x <= 300; x += 7) {
      for (let z = 0; z <= 2000; z += 13) {
        for (const clearance of [0, 3, 10, 30]) {
          const clear = roads.edgeDistance(x, z) >= clearance;
          if (!clear) near++;
          expect(roads.clearOf(x, z, clearance), `${String(x)}, ${String(z)}`).toBe(clear);
        }
      }
    }
    expect(near).toBeGreaterThan(0);
  });
});
