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

  it('P04 review: square-plan buildings stand at the setback and pack without overlapping', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const square = { id: 'block', weight: 1, footprint: 8, frontage: 5, scale: [1, 1] } as const;
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [
        { ...flat, seconds: 20, streets: { rows: [30, 40], columns: [30, 40], links: 1 } },
      ],
      props: { ...SAMPLE_SCENERY_LEVEL.props, groups: [{ id: 'g', weight: 1, kinds: [square] }] },
    };
    const p = placer(level);
    const blocks = p.place(AREA).filter((b) => b.kind === 'block');
    expect(blocks.length).toBeGreaterThan(20);
    for (const b of blocks) {
      // The front of the square is at the setback from its street's edge.
      expect(p.roads.edgeDistance(b.x, b.z)).toBeCloseTo(5 + p.roads.setback, 5);
    }
    blocks.forEach((a, i) => {
      for (const b of blocks.slice(i + 1)) {
        const apart = Math.max(Math.abs(a.x - b.x), Math.abs(a.z - b.z));
        expect(apart).toBeGreaterThanOrEqual(10 - 1e-6);
      }
    });
  });

  it('P04 review: a slot whose building does not fit tries a smaller kind of the group', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const huge = { id: 'block', weight: 1, footprint: 400, scale: [1, 1] } as const;
    const small = { id: 'stick', weight: 0, footprint: 4, scale: [1, 1] } as const;
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [{ ...flat, seconds: 20, trees: [] }],
      props: {
        ...SAMPLE_SCENERY_LEVEL.props,
        groups: [{ id: 'g', weight: 1, kinds: [huge, small] }],
      },
    };
    const props = placer(level).place(AREA);
    expect(props.length).toBeGreaterThan(0);
    expect(props.every((p) => p.kind === 'stick')).toBe(true);
  });

  it('P04 review: blocks get a podium covering them, with towers on its roof', () => {
    const [flat] = SAMPLE_SCENERY_LEVEL.sections;
    if (!flat) throw new Error('no section');
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: [
        {
          ...flat,
          seconds: 20,
          trees: [],
          streets: { rows: [50, 60], columns: [50, 60], links: 1 },
          blocks: { podiums: ['pod'], podiumHeight: [5, 5], towers: [4, 4] },
        },
      ],
    };
    const p = placer(level);
    const props = p.place(AREA);
    const podiums = props.filter((q) => q.kind === 'pod');
    expect(podiums.length).toBeGreaterThan(5);
    for (const podium of podiums) {
      const [w, h, d] = podium.size ?? [0, 0, 0];
      const block = p.roads.blocks.find(
        (b) =>
          Math.abs((b.xMin + b.xMax) / 2 - podium.x) < 1e-6 &&
          Math.abs((b.zMin + b.zMax) / 2 - podium.z) < 1e-6,
      );
      if (!block) throw new Error('podium off its block');
      expect(w).toBeCloseTo(block.xMax - block.xMin);
      expect(d).toBeCloseTo(block.zMax - block.zMin);
      expect(h).toBeGreaterThanOrEqual(5);
      // Towers stand on the roof, inside the block.
      const towers = props.filter(
        (q) =>
          q.kind === 'block' &&
          q.x > block.xMin &&
          q.x < block.xMax &&
          q.z > block.zMin &&
          q.z < block.zMax,
      );
      expect(towers.length).toBeGreaterThan(0);
      for (const tower of towers) expect(tower.y).toBeCloseTo(podium.y + h);
    }
    // No street-front buildings in a section whose blocks are filled.
    expect(props.filter((q) => q.kind === 'block').length).toBeLessThanOrEqual(4 * podiums.length);
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
