import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../../src/core/math/rng';
import type { BeamSegment } from '../../../../../src/core/systems/beam';
import { LaserParticles } from '../../../../../src/game/view/shots/laser-particles';

const OPTIONS = { count: 20, speed: [100, 100], radius: [1, 2], spread: 1 } as const;

function segment(y0: number, y1: number, width: number): BeamSegment {
  return { x: 50, y0, y1, level: 1, width, hit: false };
}

describe('LaserParticles', () => {
  it('P03-R02: flows the particles up along the beam and wraps them at its end', () => {
    const particles = new LaserParticles(OPTIONS, createRng(1), 100);
    const beam = [segment(10, 110, 4)];
    const before = particles.step(beam, 0);
    const after = particles.step(beam, 0.1);
    expect(after).toHaveLength(20);
    for (const [i, spot] of after.entries()) {
      expect(spot.y).toBeGreaterThanOrEqual(10);
      expect(spot.y).toBeLessThan(110);
      const moved = (spot.y - (before[i]?.y ?? 0) + 100) % 100;
      expect(moved).toBeCloseTo(10);
      expect(Math.abs(spot.x - 50)).toBeLessThanOrEqual(2);
    }
  });

  it('spreads particles by the width of the segment they are in', () => {
    const particles = new LaserParticles({ ...OPTIONS, count: 200 }, createRng(2), 200);
    const spots = particles.step([segment(0, 100, 20), segment(100, 200, 2)], 0);
    const upper = spots.filter((s) => s.y > 100);
    expect(upper.length).toBeGreaterThan(0);
    for (const s of upper) expect(Math.abs(s.x - 50)).toBeLessThanOrEqual(1);
    expect(spots.some((s) => Math.abs(s.x - 50) > 1)).toBe(true);
  });

  it('draws nothing without a beam', () => {
    const particles = new LaserParticles(OPTIONS, createRng(1), 100);
    expect(particles.step([], 0.1)).toEqual([]);
    expect(particles.step([segment(10, 10, 4)], 0.1)).toEqual([]);
  });
});
