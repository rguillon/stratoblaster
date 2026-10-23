import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../../src/core/scenery/road-network';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const AREA = { xMin: -200, xMax: 200, zMin: 0, zMax: 400 };

function placer(level: SceneryLevel = SAMPLE_SCENERY_LEVEL, seed = level.seed): PropPlacer {
  const field = new HeightField(level, seed);
  return new PropPlacer(field, level.props, seed, levelRoads(field, level.roads, seed));
}

describe('PropPlacer', () => {
  it('P04-R04: places buildings and trees on the ground, the same way every time', () => {
    const props = placer().place(AREA);
    expect(props.length).toBeGreaterThan(20);
    expect(placer().place(AREA)).toEqual(props);
    expect(new Set(props.map((p) => p.kind))).toEqual(new Set(['block', 'stick']));
    const field = new HeightField(SAMPLE_SCENERY_LEVEL);
    for (const p of props) expect(p.y).toBeLessThanOrEqual(field.height(p.x, p.z) + 1e-9);
    expect(placer(SAMPLE_SCENERY_LEVEL, 99).place(AREA)).not.toEqual(props);
  });

  it('P04-R07: buildings stand only along the roads, set back from the edge, facing the road', () => {
    const p = placer();
    const { roads, setback } = p.roads;
    const buildings = p.place(AREA).filter((b) => b.kind === 'block');
    expect(buildings.length).toBeGreaterThan(5);
    const footprint = 5;
    for (const b of buildings) {
      const edge = p.roads.edgeDistance(b.x, b.z);
      expect(edge).toBeGreaterThanOrEqual(footprint + setback - 1e-6);
      expect(edge).toBeLessThan(footprint + setback + 1);
      // The model's front (-Z), turned by the rotation, points at the nearest road.
      const [fx, fz] = [-Math.sin(b.rotation), -Math.cos(b.rotation)];
      const ahead = p.roads.edgeDistance(b.x + fx * 3, b.z + fz * 3);
      expect(ahead).toBeLessThan(edge);
    }
    expect(roads.some((r) => r.kind === 'main') && roads.some((r) => r.kind === 'cross')).toBe(
      true,
    );
  });

  it('P04 review: buildings never overlap, even packed along a dense street grid', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const dense: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [
        { ...flat, seconds: 20, streets: { rows: [20, 25], columns: [20, 30], links: 0.8 } },
      ],
    };
    const buildings = placer(dense)
      .place(AREA)
      .filter((b) => b.kind === 'block');
    expect(buildings.length).toBeGreaterThan(20);
    const footprint = 5;
    buildings.forEach((a, i) => {
      for (const b of buildings.slice(i + 1)) {
        expect(Math.hypot(a.x - b.x, a.z - b.z)).toBeGreaterThanOrEqual(2 * footprint);
      }
    });
  });

  it('P04 review: a section may allow only some building groups and tree kinds', () => {
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({ ...s, groups: [], trees: [] })),
    };
    expect(placer(level).place(AREA)).toEqual([]);
    const treesOnly: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({ ...s, groups: [], trees: ['stick'] })),
    };
    const props = placer(treesOnly).place(AREA);
    expect(props.length).toBeGreaterThan(0);
    expect(props.every((p) => p.kind === 'stick')).toBe(true);
  });

  it('P04-R07: trees keep off the roads', () => {
    const p = placer();
    for (const tree of p.place(AREA).filter((t) => t.kind === 'stick')) {
      expect(p.roads.edgeDistance(tree.x, tree.z)).toBeGreaterThanOrEqual(
        SAMPLE_SCENERY_LEVEL.props.treeClearance,
      );
    }
  });

  it('P04-R04: neighbouring areas give the same props as the whole area (terrain chunks)', () => {
    const p = placer();
    const whole = p.place(AREA);
    const split = [...p.place({ ...AREA, zMax: 200 }), ...p.place({ ...AREA, zMin: 200 })];
    const key = (q: { x: number; z: number }) => `${q.x.toFixed(3)},${q.z.toFixed(3)}`;
    expect(split.map(key).sort()).toEqual(whole.map(key).sort());
  });

  it('P04-R04: only flat ground gets props, and nothing stands below minHeight', () => {
    const steep: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
        ...s,
        relief: { base: 100, amplitude: 300, frequency: 1 / 40, octaves: 3, style: 'smooth' },
      })),
      props: { ...SAMPLE_SCENERY_LEVEL.props, maxSlope: 0.01, treeMaxSlope: 0.01 },
    };
    expect(placer(steep).place(AREA)).toEqual([]);
    const underwater: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      props: { ...SAMPLE_SCENERY_LEVEL.props, minHeight: 1000 },
    };
    expect(placer(underwater).place(AREA)).toEqual([]);
  });

  it('P04-R04: a section without density gets no props', () => {
    const empty: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
        ...s,
        buildingDensity: 0,
        treeDensity: 0,
      })),
    };
    expect(placer(empty).place(AREA)).toEqual([]);
  });
});
