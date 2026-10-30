import { describe, expect, it } from 'vitest';
import { createNoise2D } from '../../../../src/core/math/noise';
import { HeightField, terrainCeiling } from '../../../../src/core/scenery/height-field';
import { crevasseDepth, withLakes } from '../../../../src/core/scenery/ice-sculpt';
import { floatingIn, linePieces } from '../../../../src/core/scenery/float-placement';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../../src/core/scenery/road-network';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const LAKES = { spacing: 200, chance: 1, radius: [40, 40], level: 2, edge: 20 } as const;
const CREVASSES = { spacing: 50, width: 8, depth: 12, angleDeg: 90, warp: 0, share: 1 };

describe('Frozen land sculpting', () => {
  it('P08-R03: frozen lakes are flat basins at their level, with shores rising back', () => {
    // Every square has a lake, centred (room is spacing / 2 - radius - edge = 40, jittered).
    let flat = 0;
    for (let x = -400; x < 400; x += 10) {
      for (let z = 0; z < 800; z += 10) {
        const h = withLakes(LAKES, 3, x, z, 30);
        expect(h).toBeGreaterThanOrEqual(2 - 1e-9);
        expect(h).toBeLessThanOrEqual(30 + 1e-9);
        if (Math.abs(h - 2) < 1e-6) flat++;
      }
    }
    expect(flat).toBeGreaterThan(100);
    expect(withLakes({ ...LAKES, chance: 0 }, 3, 10, 10, 30)).toBe(30);
  });

  it('P08-R07: crevasses are narrow cuts, every spacing, as deep as asked', () => {
    const noise = createNoise2D(5);
    // Lines across the level (angle 90°: x · 1 / spacing): a cut at x = 0, none at x = 25.
    expect(crevasseDepth(CREVASSES, noise, 0, 10)).toBeCloseTo(12);
    expect(crevasseDepth(CREVASSES, noise, 25, 10)).toBe(0);
    expect(crevasseDepth({ ...CREVASSES, share: 0 }, noise, 0, 10)).toBe(0);
  });

  it('P08-R03, P08-R07: a height field with lakes and crevasses, under its ceiling', () => {
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
        ...s,
        lakes: LAKES,
        crevasses: CREVASSES,
      })),
    };
    const field = new HeightField(level);
    const plain = new HeightField(SAMPLE_SCENERY_LEVEL);
    let lower = 0;
    for (let z = 0; z < field.length; z += 7) {
      for (let x = -150; x <= 150; x += 7) {
        expect(field.height(x, z)).toBeLessThanOrEqual(terrainCeiling(level) + 1e-9);
        if (field.height(x, z) < plain.height(x, z) - 1) lower++;
      }
    }
    expect(lower).toBeGreaterThan(0);
  });
});

describe('Floating props and prop lines', () => {
  const sea: SceneryLevel = {
    ...SAMPLE_SCENERY_LEVEL,
    sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
      ...s,
      relief: { ...s.relief, base: -40 },
      floatDensity: 1,
    })),
  };
  const FLOATING = {
    cellSize: 40,
    perCell: 3,
    depth: 5,
    kinds: [
      {
        id: 'floe',
        weight: 1,
        footprint: 6,
        scale: [1, 1] as const,
        drift: { x: 2, z: 1, period: 10 },
      },
    ],
  };

  it('P08-R07: ice floats at the sea level, only where the sea is deep enough', () => {
    const field = new HeightField(sea);
    const area = { xMin: -200, xMax: 200, zMin: 0, zMax: field.length };
    const floes = floatingIn(FLOATING, field, [0, 7], area);
    expect(floes.length).toBeGreaterThan(5);
    for (const p of floes) {
      expect(p.y).toBe(0);
      expect(field.height(p.x, p.z)).toBeLessThanOrEqual(-5);
    }
    // Deterministic, and nothing on land.
    expect(floatingIn(FLOATING, field, [0, 7], area)).toEqual(floes);
    const land = new HeightField(SAMPLE_SCENERY_LEVEL);
    expect(floatingIn(FLOATING, land, [0, 7], area)).toEqual([]);
  });

  it('P08-R07: the placer puts floating props in the areas asked for, with a sea only', () => {
    const level = { ...sea, props: { ...sea.props, floating: FLOATING } };
    const field = new HeightField(level);
    const roads = levelRoads(field, level.roads, level.seed);
    const area = { xMin: -200, xMax: 200, zMin: 0, zMax: field.length };
    const withSea = new PropPlacer(field, level.props, level.seed, roads, 0).place(area);
    const without = new PropPlacer(field, level.props, level.seed, roads).place(area);
    expect(withSea.filter((p) => p.kind === 'floe').length).toBeGreaterThan(0);
    expect(without.filter((p) => p.kind === 'floe')).toEqual([]);
  });

  it('P08-R03: a line of props follows its path, turned along it, on dry gentle ground', () => {
    const field = new HeightField(SAMPLE_SCENERY_LEVEL);
    const line = {
      kind: 'pipe',
      path: { x: 50, amplitude: 0, wavelength: 1000 },
      spacing: 15,
      footprint: 5,
      maxSlope: 1,
    };
    const pieces = linePieces(line, field, 0);
    expect(pieces.length).toBe(Math.ceil(field.length / 15));
    for (const { placement } of pieces) {
      expect(placement.x).toBeCloseTo(50, 0);
      // Straight along Z: the model's X turned onto Z.
      expect(Math.abs(Math.sin(placement.rotation))).toBeCloseTo(1);
    }
    expect(linePieces({ ...line, sections: ['nowhere'] }, field, 0)).toEqual([]);
    const level = {
      ...SAMPLE_SCENERY_LEVEL,
      props: { ...SAMPLE_SCENERY_LEVEL.props, lines: [line] },
    };
    const roads = levelRoads(field, level.roads, level.seed);
    const placed = new PropPlacer(field, level.props, level.seed, roads).place({
      xMin: -200,
      xMax: 200,
      zMin: 0,
      zMax: field.length,
    });
    expect(placed.filter((p) => p.kind === 'pipe').length).toBe(pieces.length);
  });
});
