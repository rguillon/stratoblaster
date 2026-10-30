import { describe, expect, it } from 'vitest';
import { buildLevelGrid, firstUnlockedLevel } from '../../../../src/core/content/level-catalog';

describe('buildLevelGrid', () => {
  it('P01-R07: builds worlds × levels entries labelled world-level, row by row', () => {
    const catalog = buildLevelGrid(2, 3, ['1-1', '2-3']);
    expect(catalog.columns).toBe(3);
    expect(catalog.levels.map((l) => l.label)).toEqual(['1-1', '1-2', '1-3', '2-1', '2-2', '2-3']);
    expect(catalog.levels.filter((l) => l.unlocked).map((l) => l.id)).toEqual(['1-1', '2-3']);
    expect(catalog.levels[4]).toEqual({
      id: '2-2',
      label: '2-2',
      world: 2,
      level: 2,
      unlocked: false,
    });
  });

  it('rejects empty or fractional grids', () => {
    expect(() => buildLevelGrid(0, 5, [])).toThrow(RangeError);
    expect(() => buildLevelGrid(5, 0, [])).toThrow(RangeError);
    expect(() => buildLevelGrid(1.5, 5, [])).toThrow(RangeError);
  });
});

describe('firstUnlockedLevel', () => {
  it('returns the index of the first unlocked level, or 0 when all are locked', () => {
    expect(firstUnlockedLevel(buildLevelGrid(2, 2, ['2-1']))).toBe(2);
    expect(firstUnlockedLevel(buildLevelGrid(2, 2, []))).toBe(0);
  });
});
