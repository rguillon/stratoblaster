import { describe, expect, it } from 'vitest';
import { createRng, pick, randomIn } from '../../../../src/core/math/rng';

describe('createRng', () => {
  it('gives the same sequence for the same seed, and another one for another seed', () => {
    const a = createRng(42);
    const b = createRng(42);
    const c = createRng(43);
    const seqA = [a(), a(), a()];
    expect([b(), b(), b()]).toEqual(seqA);
    expect([c(), c(), c()]).not.toEqual(seqA);
  });

  it('returns numbers in [0, 1)', () => {
    const random = createRng(7);
    for (let i = 0; i < 1000; i++) {
      const x = random();
      expect(x).toBeGreaterThanOrEqual(0);
      expect(x).toBeLessThan(1);
    }
  });
});

describe('randomIn', () => {
  it('maps [0, 1) onto [min, max)', () => {
    expect(randomIn(() => 0, [2, 6])).toBe(2);
    expect(randomIn(() => 0.5, [2, 6])).toBe(4);
  });
});

describe('pick', () => {
  it('chooses an item by the random value', () => {
    expect(pick(() => 0, ['a', 'b'])).toBe('a');
    expect(pick(() => 0.99, ['a', 'b'])).toBe('b');
  });

  it('refuses an empty list', () => {
    expect(() => pick(() => 0, [])).toThrow(RangeError);
  });
});
