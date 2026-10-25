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
      // Thin blocks at the edges of the district may be too narrow for the smallest tower (5),
      // and the towers of a block across the edge of the area may lie outside it.
      const whole = block.zMin >= AREA.zMin && block.zMax <= AREA.zMax;
      if (whole && Math.min(w, d) >= 12) expect(towers.length).toBeGreaterThan(0);
      for (const tower of towers) expect(tower.y).toBeCloseTo(podium.y + h);
    }
    // No street-front buildings in a section whose blocks are filled.
    expect(props.filter((q) => q.kind === 'block').length).toBeLessThanOrEqual(4 * podiums.length);
  });

  it('P04 review: without podiums, buildings stand on the ground in every part of a block', () => {
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
          blocks: { podiums: [], podiumHeight: [0, 0], towers: [16, 16] },
        },
      ],
    };
    const p = placer(level);
    const props = p.place(AREA);
    const buildings = props.filter((q) => q.kind === 'block');
    expect(buildings.length).toBeGreaterThan(5);
    // On the ground under them, at its lowest so they never float, not on a podium.
    const field = new HeightField(level, level.seed);
    for (const b of buildings) {
      expect(b.y).toBeLessThanOrEqual(field.height(b.x, b.z) + 1e-6);
      expect(b.y).toBeGreaterThan(field.height(b.x, b.z) - 5);
    }
    expect(props.some((q) => q.size !== undefined)).toBe(false);
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

  describe('away from the roads (phase 6 review)', () => {
    const BIG: SceneryLevel['props'] = SAMPLE_SCENERY_LEVEL.props;
    const key = (b: { x: number; z: number }) => `${b.x.toFixed(3)},${b.z.toFixed(3)}`;
    /** The buildings `props` adds to the sample level's. */
    function added(props: Partial<SceneryLevel['props']>, level = SAMPLE_SCENERY_LEVEL) {
      const base = new Set(
        placer(level)
          .place(AREA)
          .filter((b) => b.kind === 'block')
          .map(key),
      );
      const p = placer({ ...level, props: { ...BIG, ...props } });
      const extra = p.place(AREA).filter((b) => b.kind === 'block' && !base.has(key(b)));
      return { p, extra };
    }

    it('lone buildings stand clear of the roads, scattered over the level', () => {
      const { p, extra } = added({ loners: { cell: 30, chance: 1, clearance: 8 } });
      expect(extra.length).toBeGreaterThan(5);
      for (const b of extra)
        expect(p.roads.edgeDistance(b.x, b.z)).toBeGreaterThanOrEqual(13 - 1e-6);
      // A low chance gives fewer, and none where the section has no buildings.
      expect(added({ loners: { cell: 30, chance: 0.2, clearance: 8 } }).extra.length).toBeLessThan(
        extra.length,
      );
      const bare: SceneryLevel = {
        ...SAMPLE_SCENERY_LEVEL,
        sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({ ...s, buildingDensity: 0 })),
      };
      expect(
        placer({ ...bare, props: { ...BIG, loners: { cell: 30, chance: 1, clearance: 8 } } })
          .place(AREA)
          .filter((b) => b.kind === 'block'),
      ).toEqual([]);
    });

    it('hamlets gather buildings close together, turned about the same way, clear of the roads', () => {
      const hamlets = {
        spacing: [120, 160],
        buildings: [4, 6],
        radius: 18,
        gap: 1,
        clearance: 6,
      } as const;
      const { p, extra } = added({ hamlets });
      expect(extra.length).toBeGreaterThanOrEqual(4);
      for (const b of extra) {
        expect(p.roads.edgeDistance(b.x, b.z)).toBeGreaterThanOrEqual(11 - 1e-6);
        // A hamlet at the edge of the area may have its other buildings out of it.
        if (b.z < 2 * hamlets.radius || b.z > AREA.zMax - 2 * hamlets.radius) continue;
        const neighbours = extra.filter(
          (o) => o !== b && Math.hypot(o.x - b.x, o.z - b.z) <= 2 * hamlets.radius,
        );
        expect(neighbours.length).toBeGreaterThan(0);
        // Within the skew of a neighbour's heading, a quarter turn apart at most.
        const quarter = (a: number) => ((a % (Math.PI / 2)) + Math.PI / 2) % (Math.PI / 2);
        const skew = Math.min(
          ...neighbours.map((o) => {
            const d = Math.abs(quarter(o.rotation) - quarter(b.rotation));
            return Math.min(d, Math.PI / 2 - d);
          }),
        );
        expect(skew).toBeLessThanOrEqual(0.3 + 1e-9);
      }
      // Buildings of a hamlet never overlap.
      for (const b of extra) {
        for (const o of extra) {
          if (o !== b) expect(Math.hypot(o.x - b.x, o.z - b.z)).toBeGreaterThan(5);
        }
      }
    });
  });
});
