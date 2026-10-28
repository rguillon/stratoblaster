import { describe, expect, it } from 'vitest';
import {
  isBoulevard,
  lanesOf,
  mainRoadWidth,
  streetWidth,
} from '../../../../src/core/scenery/lanes';
import type { RoadRules } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const RULES: RoadRules = {
  ...SAMPLE_SCENERY_LEVEL.roads,
  mainWidth: 6,
  dual: { width: 12, mainRoads: 1, avenues: 0.3 },
};

describe('2×2 roads', () => {
  it('P04 review: the first main roads are 2×2, with two lanes each way', () => {
    expect(mainRoadWidth(RULES, 0)).toBe(12);
    expect(mainRoadWidth(RULES, 1)).toBe(6);
    expect(lanesOf(RULES, 12)).toBe(2);
    expect(lanesOf(RULES, 6)).toBe(1);
  });

  it('P04 review: a share of the street lines are 2×2 avenues, the same along a whole line', () => {
    const widths = Array.from({ length: 400 }, (_, i) => streetWidth(RULES, i * 37.3));
    const share = widths.filter((w) => w === 12).length / widths.length;
    expect(share).toBeGreaterThan(0.2);
    expect(share).toBeLessThan(0.4);
    expect(streetWidth(RULES, 120.0004)).toBe(streetWidth(RULES, 120));
    expect(streetWidth({ ...RULES, dual: { ...RULES.dual, avenues: 0 } }, 120)).toBe(6);
  });
});

describe('boulevards (reviewer, 2026-10-28)', () => {
  const WIDE: RoadRules = {
    ...RULES,
    boulevards: [
      { lanes: 3, width: 18, share: 0.15 },
      { lanes: 4, width: 24, share: 0.1 },
    ],
  };

  it('a share of the street lines are 3×3 and 4×4 boulevards, the same along a whole line', () => {
    const widths = Array.from({ length: 1000 }, (_, i) => streetWidth(WIDE, i * 37.3));
    const share = (w: number) => widths.filter((x) => x === w).length / widths.length;
    expect(share(18)).toBeGreaterThan(0.1);
    expect(share(18)).toBeLessThan(0.2);
    expect(share(24)).toBeGreaterThan(0.05);
    expect(share(24)).toBeLessThan(0.15);
    expect(share(12)).toBeGreaterThan(0.2);
    expect(lanesOf(WIDE, 18)).toBe(3);
    expect(lanesOf(WIDE, 24)).toBe(4);
    expect(isBoulevard(WIDE, 24)).toBe(true);
    expect(isBoulevard(WIDE, 12)).toBe(false);
    // Without boulevards, the same lines as before are avenues.
    for (let i = 0; i < 200; i++)
      expect(streetWidth(RULES, i * 41)).toBe(streetWidth(RULES, i * 41));
  });
});
