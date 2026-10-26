import { describe, expect, it } from 'vitest';
import { LEVELS } from '../../../../src/game/sim/levels';

describe('LEVELS', () => {
  it('P01-R07: 5 worlds × 5 levels labelled 1-1 … 5-5', () => {
    expect(LEVELS.columns).toBe(5);
    expect(LEVELS.levels).toHaveLength(25);
    expect(LEVELS.levels[0]?.label).toBe('1-1');
    expect(LEVELS.levels[24]?.label).toBe('5-5');
  });

  it('P06-R01, P08-R01: the World 1 and World 2 levels are unlocked; worlds 3 to 5 stay locked', () => {
    expect(LEVELS.levels.filter((l) => l.unlocked).map((l) => l.id)).toEqual([
      '1-1',
      '1-2',
      '1-3',
      '1-4',
      '1-5',
      '2-1',
      '2-2',
      '2-3',
      '2-4',
      '2-5',
      // P09-R01: World 3 is unlocked too.
      '3-1',
      '3-2',
      '3-3',
      '3-4',
      '3-5',
    ]);
    expect(LEVELS.levels.filter((l) => l.world > 3).every((l) => !l.unlocked)).toBe(true);
    expect(LEVELS.levels.filter((l) => l.world > 3)).toHaveLength(10);
  });
});
