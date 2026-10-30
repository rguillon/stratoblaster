import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../../src/core/math/rng';
import { SparkBursts } from '../../../../../src/game/view/shots/spark-bursts';

const OPTIONS = {
  count: 12,
  speed: [100, 200],
  spreadDeg: 80,
  drag: 5,
  life: [0.2, 0.4],
  length: [4, 8],
  twinkle: 0.5,
  twinkleHz: [20, 30],
} as const;

describe('SparkBursts', () => {
  it('P03 review: a hit throws `count` sparks back from the hit point, spread around straight down', () => {
    const sparks = new SparkBursts(OPTIONS, createRng(1));
    sparks.emit(100, 200);
    expect(sparks.count).toBe(12);
    const spots = sparks.step(0.01);
    expect(spots).toHaveLength(12);
    for (const s of spots) {
      // Bullets fly up: the sparks go down, within 80° of straight back.
      expect(s.y).toBeLessThan(200);
      expect(Math.abs(Math.abs(s.heading) - Math.PI)).toBeLessThanOrEqual(
        (80 * Math.PI) / 180 + 1e-9,
      );
      expect(s.brightness).toBeGreaterThan(0);
      expect(s.brightness).toBeLessThanOrEqual(1);
    }
  });

  it('slows the sparks down, shortens them, and removes them at the end of their life', () => {
    const sparks = new SparkBursts({ ...OPTIONS, count: 1, life: [0.3, 0.3] }, createRng(2));
    sparks.emit(0, 0);
    const [a] = sparks.step(0.05);
    const [b] = sparks.step(0.05);
    const [c] = sparks.step(0.05);
    if (!a || !b || !c) throw new Error('spark missing');
    const stepAB = Math.hypot(b.x - a.x, b.y - a.y);
    const stepBC = Math.hypot(c.x - b.x, c.y - b.y);
    expect(stepBC).toBeLessThan(stepAB);
    expect(c.length).toBeLessThan(a.length);
    expect(sparks.step(0.2)).toEqual([]);
    expect(sparks.count).toBe(0);
  });

  it('gives the same sparks for the same seed', () => {
    const a = new SparkBursts(OPTIONS, createRng(3));
    const b = new SparkBursts(OPTIONS, createRng(3));
    a.emit(1, 2);
    b.emit(1, 2);
    expect(a.step(0.02)).toEqual(b.step(0.02));
  });
});
