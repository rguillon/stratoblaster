import { describe, expect, it } from 'vitest';
import { HeightField } from '../../../../src/core/scenery/height-field';
import { linePieces, placeLandmark } from '../../../../src/core/scenery/float-placement';
import { PropPlacer } from '../../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../../src/core/scenery/road-network';
import type { SceneryLevel } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

/** The sample level with its ground around the water level, so it is half land, half water. */
const MARSH: SceneryLevel = {
  ...SAMPLE_SCENERY_LEVEL,
  sections: SAMPLE_SCENERY_LEVEL.sections.map((s) => ({
    ...s,
    relief: { ...s.relief, base: 0, amplitude: 6, style: 'smooth' as const },
  })),
};

const STRAIGHT = { x: 30, amplitude: 0, wavelength: 1000 };

describe('Set pieces and lines over water (phase 9)', () => {
  it('P09-R06: a line over water stands on the ground, or at the water level where that is lower', () => {
    const field = new HeightField(MARSH);
    const line = {
      kind: 'pipe',
      path: STRAIGHT,
      spacing: 15,
      footprint: 5,
      maxSlope: 1,
      overWater: true,
    };
    const pieces = linePieces(line, field, 0);
    expect(pieces.length).toBe(Math.ceil(field.length / 15));
    const wet = pieces.filter(({ placement: p }) => field.height(p.x, p.z) <= 0);
    expect(wet.length).toBeGreaterThan(0);
    for (const { placement: p } of pieces) expect(p.y).toBe(Math.max(0, field.height(p.x, p.z)));
    // Without `overWater`, the wet pieces are left out.
    const dry = linePieces({ ...line, overWater: false }, field, 0);
    expect(dry.length).toBe(pieces.length - wet.length);
  });

  it('P09-R06: a set piece stands where it is put, across its path, on the water or the ground', () => {
    const field = new HeightField(MARSH);
    const dam = { kind: 'dam', z: 400, path: STRAIGHT, footprint: [200, 15] as const };
    const onGround = placeLandmark(dam, field, 0);
    expect(onGround.placement).toMatchObject({ kind: 'dam', x: 30, z: 400, scale: 1 });
    expect(onGround.placement.y).toBe(field.height(30, 400));
    // Its width (X) across the straight path: not turned.
    expect(Math.cos(onGround.placement.rotation)).toBeCloseTo(1);
    expect([onGround.halfX, onGround.halfZ]).toEqual([200, 15]);
    const onWater = placeLandmark({ ...dam, onWater: true }, field, 0);
    expect(onWater.placement.y).toBe(Math.max(0, field.height(30, 400)));
    const fixed = placeLandmark(
      { kind: 'plant', z: 300, x: -50, footprint: 12, scale: 1.2 },
      field,
      0,
    );
    expect(fixed.placement).toMatchObject({ x: -50, z: 300, rotation: 0, scale: 1.2 });
    expect([fixed.halfX, fixed.halfZ]).toEqual([12, 12]);
  });

  it('P09-R06: the placer puts the set pieces first; the trees and buildings keep clear of them, however big', () => {
    const level: SceneryLevel = {
      ...SAMPLE_SCENERY_LEVEL,
      props: {
        ...SAMPLE_SCENERY_LEVEL.props,
        landmarks: [{ kind: 'temple', z: 200, x: 0, footprint: [120, 60] }],
      },
    };
    const field = new HeightField(level);
    const roads = levelRoads(field, level.roads, level.seed);
    const placed = new PropPlacer(field, level.props, level.seed, roads).place({
      xMin: -400,
      xMax: 400,
      zMin: 0,
      zMax: field.length,
    });
    expect(placed.filter((p) => p.kind === 'temple')).toHaveLength(1);
    // The sample level is 400 long; its props stand around the set piece but not on it.
    expect(placed.length).toBeGreaterThan(10);
    const near = placed.filter(
      (p) => p.kind !== 'temple' && Math.abs(p.x) < 115 && Math.abs(p.z - 200) < 55,
    );
    expect(near).toEqual([]);
  });
});
