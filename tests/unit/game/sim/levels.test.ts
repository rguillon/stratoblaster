import { describe, expect, it } from 'vitest';
import { LEVELS } from '../../../../src/game/sim/levels';

describe('LEVELS', () => {
  it('P01-R07: 5 worlds × 5 levels labelled 1-1 … 5-5', () => {
    expect(LEVELS.columns).toBe(5);
    expect(LEVELS.levels).toHaveLength(25);
    expect(LEVELS.levels[0]?.label).toBe('1-1');
    expect(LEVELS.levels[24]?.label).toBe('5-5');
  });

  it('P06-R01: the five World 1 levels are unlocked; worlds 2 to 5 stay locked', () => {
    expect(LEVELS.levels.filter((l) => l.unlocked).map((l) => l.id)).toEqual([
      '1-1',
      '1-2',
      '1-3',
      '1-4',
      '1-5',
    ]);
    expect(LEVELS.levels.filter((l) => l.world > 1).every((l) => !l.unlocked)).toBe(true);
    expect(LEVELS.levels.filter((l) => l.world > 1)).toHaveLength(20);
  });
});
