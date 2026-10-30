import { describe, expect, it } from 'vitest';
import { LEVELS } from '../../../../src/game/sim/levels';

describe('LEVELS', () => {
  it('P01-R07: 4 worlds × 5 levels labelled 1-1 … 4-5', () => {
    expect(LEVELS.columns).toBe(5);
    expect(LEVELS.levels).toHaveLength(20);
    expect(LEVELS.levels[0]?.label).toBe('1-1');
    expect(LEVELS.levels[19]?.label).toBe('4-5');
  });

  it('P06-R01, P08-R01, P09-R01, P10-R01: every level of Worlds 1 to 4 is unlocked', () => {
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
      // P10-R01: World 4 is unlocked too.
      '4-1',
      '4-2',
      '4-3',
      '4-4',
      '4-5',
    ]);
  });
});
