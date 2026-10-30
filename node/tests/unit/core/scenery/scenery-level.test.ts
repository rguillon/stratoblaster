import { describe, expect, it } from 'vitest';
import {
  layoutSections,
  levelDuration,
  levelLength,
} from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL as LEVEL } from '../../../fixtures/sample-scenery';

describe('scenery level layout', () => {
  it('P04-R06: places the sections end to end, each seconds × speed long', () => {
    expect(layoutSections(LEVEL).map(({ start, end }) => [start, end])).toEqual([
      [0, 200],
      [200, 400],
    ]);
    expect(levelDuration(LEVEL)).toBe(20);
    expect(levelLength(LEVEL)).toBe(400);
  });

  it('rejects levels without sections, speed or section length', () => {
    expect(() => layoutSections({ ...LEVEL, sections: [] })).toThrow(RangeError);
    expect(() => layoutSections({ ...LEVEL, scrollSpeed: 0 })).toThrow(RangeError);
    const [first] = LEVEL.sections;
    if (!first) throw new Error('no section');
    expect(() => layoutSections({ ...LEVEL, sections: [{ ...first, seconds: 0 }] })).toThrow(
      RangeError,
    );
  });
});
