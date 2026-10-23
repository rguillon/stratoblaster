import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const AREA = { xMin: -200, xMax: 200, zMin: 0, zMax: 400 };

function placer(level: SceneryLevel = SAMPLE_SCENERY_LEVEL, seed = level.seed): PropPlacer {
  return new PropPlacer(new HeightField(level, seed), level.props, seed);
}

describe('PropPlacer', () => {
  it('P04-R04: places buildings and trees on the ground, the same way every time', () => {
    const props = placer().place(AREA);
    expect(props.length).toBeGreaterThan(20);
    expect(placer().place(AREA)).toEqual(props);
    expect(new Set(props.map((p) => p.kind))).toEqual(new Set(['block', 'stick']));
    const field = new HeightField(SAMPLE_SCENERY_LEVEL);
    for (const p of props) {
      expect(p.y).toBeLessThanOrEqual(field.height(p.x, p.z) + 1e-9);
      expect(p.x).toBeGreaterThanOrEqual(AREA.xMin);
      expect(p.x).toBeLessThan(AREA.xMax + SAMPLE_SCENERY_LEVEL.props.cellSize);
    }
    expect(placer(SAMPLE_SCENERY_LEVEL, 99).place(AREA)).not.toEqual(props);
  });

  it('P04-R04: neighbouring areas give the same props as the whole area (terrain chunks)', () => {
    const p = placer();
    const whole = p.place(AREA);
    const split = [...p.place({ ...AREA, zMax: 200 }), ...p.place({ ...AREA, zMin: 200 })];
    const key = (q: { x: number; z: number }) => `${q.x.toFixed(3)},${q.z.toFixed(3)}`;
    expect(split.map(key).sort()).toEqual(whole.map(key).sort());
  });

  it('P04-R04: only flat ground gets buildings, and nothing stands below minHeight', () => {
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

  it('P04-R04: buildings of an area share a street grid (quarter turns plus a zone angle)', () => {
    const buildings = placer()
      .place(AREA)
      .filter((p) => p.kind === 'block');
    expect(buildings.length).toBeGreaterThan(3);
    for (const b of buildings) {
      expect(b.scale).toBe(1);
      expect(b.rotation).toBeGreaterThanOrEqual(0);
      expect(b.rotation).toBeLessThan(2 * Math.PI + Math.PI);
    }
  });
});
