import { describe, expect, it } from 'vitest';
import { traceBeam } from '../../../../src/core/systems/beam';
import type { ShotTarget } from '../../../../src/core/entities/shot-target';
import { testBeam } from '../../../helpers/test-weapons';

const LEVELS = testBeam().levels;

function target(id: number, x: number, y: number, health = 10): ShotTarget {
  return { id, x, y, radius: 5, health, maxHealth: 10 };
}

describe('traceBeam', () => {
  it('P03-R02: runs to the top when nothing is in the way', () => {
    const trace = traceBeam(LEVELS, 2, 50, 10, 200, [target(1, 90, 100)]);
    expect(trace.segments).toEqual([{ x: 50, y0: 10, y1: 200, level: 2, width: 4, hit: false }]);
    expect(trace.hits).toEqual([]);
  });

  it('P03-R02: at level 1, stops at the first target', () => {
    const low = target(1, 50, 100);
    const high = target(2, 50, 150);
    const trace = traceBeam(LEVELS, 1, 50, 10, 200, [high, low]);
    expect(trace.segments).toEqual([{ x: 50, y0: 10, y1: 95, level: 1, width: 2, hit: true }]);
    expect(trace.hits.map((h) => h.target)).toEqual([low]);
  });

  it('P03-R02: above level 1, goes through a target and continues one level lower', () => {
    const a = target(1, 50, 100);
    const b = target(2, 52, 150);
    const c = target(3, 48, 180);
    const trace = traceBeam(LEVELS, 2, 50, 10, 300, [c, b, a]);
    expect(trace.segments.map((s) => [s.y0, s.y1, s.level, s.hit])).toEqual([
      [10, 95, 2, true],
      [95, 145, 1, true],
    ]);
    // Level 1 stops at the second target: the third one is not touched.
    expect(trace.hits.map((h) => [h.target.id, h.level])).toEqual([
      [1, 2],
      [2, 1],
    ]);
  });

  it('P03-R02: a level-3 beam that runs out of targets reaches the top', () => {
    const trace = traceBeam(LEVELS, 3, 50, 10, 300, [target(1, 50, 100)]);
    expect(trace.segments.map((s) => [s.y1, s.level, s.hit])).toEqual([
      [95, 3, true],
      [300, 2, false],
    ]);
  });

  it('ignores dead targets, targets below the muzzle and targets off to the side', () => {
    const trace = traceBeam(LEVELS, 1, 50, 10, 200, [
      target(1, 50, 100, 0),
      target(2, 50, 5),
      target(3, 58, 100),
    ]);
    expect(trace.hits).toEqual([]);
  });

  it('touches a target whose edge overlaps the beam width', () => {
    // Level 3: half width 3, target radius 5: up to 8 px off the beam line.
    const trace = traceBeam(LEVELS, 3, 50, 10, 200, [target(1, 57.9, 100)]);
    expect(trace.hits).toHaveLength(1);
  });
});
