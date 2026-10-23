import { describe, expect, it } from 'vitest';
import { HeightField, softCap, terrainCeiling } from '../../../../src/core/scenery/height-field';
import type { SceneryLevel, TerrainSection } from '../../../../src/core/scenery/scenery-level';
import { SAMPLE_SCENERY_LEVEL } from '../../../fixtures/sample-scenery';

const STRAIGHT = { x: 0, amplitude: 0, wavelength: 1000 } as const;

function section(overrides: Partial<TerrainSection> = {}): TerrainSection {
  return {
    name: 'test',
    seconds: 10,
    relief: { base: 50, amplitude: 20, frequency: 1 / 200, octaves: 4, style: 'smooth' },
    buildingDensity: 0,
    treeDensity: 0,
    ...overrides,
  };
}

function level(sections: TerrainSection[], transition = 0): SceneryLevel {
  return { ...SAMPLE_SCENERY_LEVEL, scrollSpeed: 10, transition, sections };
}

/** Heights on a grid over [x0, x1] × [z0, z1]. */
function grid(
  field: HeightField,
  [x0, x1]: [number, number],
  [z0, z1]: [number, number],
): number[] {
  const heights: number[] = [];
  for (let x = x0; x <= x1; x += (x1 - x0) / 20) {
    for (let z = z0; z <= z1; z += (z1 - z0) / 20) heights.push(field.height(x, z));
  }
  return heights;
}

describe('HeightField', () => {
  it('P04-R01: is the same for the same seed and changes with the seed', () => {
    const lvl = level([section()]);
    expect(new HeightField(lvl).height(12, 34)).toBe(new HeightField(lvl).height(12, 34));
    expect(new HeightField(lvl, 1).height(12, 34)).not.toBe(new HeightField(lvl, 2).height(12, 34));
  });

  it('P04-R01: smooth relief stays within base ± amplitude', () => {
    const heights = grid(new HeightField(level([section()])), [-500, 500], [0, 100]);
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(30);
    expect(Math.max(...heights)).toBeLessThanOrEqual(70);
    expect(Math.max(...heights) - Math.min(...heights)).toBeGreaterThan(5);
  });

  it('P04-R01: mountains (ridged relief) rise above the base, and peaks stay under maxHeight', () => {
    const relief = {
      base: 0,
      amplitude: 400,
      frequency: 1 / 300,
      octaves: 5,
      style: 'ridged',
      maxHeight: 250,
    } as const;
    const heights = grid(new HeightField(level([section({ relief })])), [-600, 600], [0, 100]);
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(0);
    expect(Math.max(...heights)).toBeLessThan(250);
    expect(Math.max(...heights)).toBeGreaterThan(150);
    expect(softCap(10, 250)).toBe(10);
    expect(softCap(1000, 250)).toBeLessThan(250);
    expect(softCap(5, 0)).toBeLessThan(0.01);
  });

  it('P04-R01: a plateau flattens a band at its height', () => {
    const flatten = { path: STRAIGHT, halfWidth: 100, edge: 50, height: 80, roughness: 0 };
    const field = new HeightField(level([section({ flatten })]));
    for (const h of grid(field, [-90, 90], [0, 100])) expect(h).toBeCloseTo(80);
    expect(field.slope(0, 50)).toBeCloseTo(0);
    expect(field.height(300, 50)).not.toBeCloseTo(80);
  });

  it('P04-R01: a canyon carves its floor along the path, below the ground around it', () => {
    const channel = {
      path: { x: 100, amplitude: 0, wavelength: 500 },
      halfWidth: 20,
      wall: 40,
      floor: -10,
    };
    const field = new HeightField(level([section({ channel })]));
    expect(field.height(100, 30)).toBeLessThan(0);
    expect(field.height(100, 30)).toBeGreaterThan(-12);
    expect(field.height(250, 30)).toBeGreaterThan(25);
    expect(field.slope(100 + 40, 30)).toBeGreaterThan(field.slope(250, 30));
  });

  it('P04-R01, P04-R02: a coast drops the ground under the sea on the sea side', () => {
    const shore = { path: STRAIGHT, landSide: -1, width: 100, seabed: -60 } as const;
    const field = new HeightField(level([section({ shore })]));
    expect(field.height(-300, 10)).toBeGreaterThan(25);
    expect(field.height(300, 10)).toBe(-60);
    expect(field.height(0, 10)).toBeLessThan(field.height(-300, 10));
  });

  it('P04-R01: neighbouring sections blend smoothly; outside the level the ground continues', () => {
    const low = section({
      relief: { base: 0, amplitude: 0, frequency: 1, octaves: 1, style: 'smooth' },
    });
    const high = section({
      relief: { base: 100, amplitude: 0, frequency: 1, octaves: 1, style: 'smooth' },
    });
    const field = new HeightField(level([low, high], 40));
    expect(field.length).toBe(200);
    expect(field.height(0, 50)).toBe(0);
    expect(field.height(0, 100)).toBeCloseTo(50);
    expect(field.height(0, 90)).toBeGreaterThan(0);
    expect(field.height(0, 90)).toBeLessThan(50);
    expect(field.height(0, 110)).toBeGreaterThan(50);
    expect(field.height(0, 150)).toBe(100);
    expect(field.height(0, -500)).toBe(0);
    expect(field.height(0, 5000)).toBe(100);
    expect(field.sectionAt(150).section).toBe(high);
    expect(field.sectionAt(-5).section).toBe(low);
    expect(field.sectionIndexAt(999)).toBe(1);
  });

  it('P04-R03 (review): the ground never rises above its ceiling, whatever the seed', () => {
    const relief = {
      base: 0,
      amplitude: 400,
      frequency: 1 / 300,
      octaves: 5,
      style: 'ridged',
      maxHeight: 250,
    } as const;
    const flatten = { path: STRAIGHT, halfWidth: 50, edge: 20, height: 300, roughness: 2 };
    const lvl = level([section(), section({ relief }), section({ flatten })], 30);
    expect(terrainCeiling(lvl)).toBe(302);
    for (const seed of [1, 2, 3]) {
      const field = new HeightField(lvl, seed);
      expect(field.ceiling).toBe(302);
      expect(Math.max(...grid(field, [-600, 600], [0, 300]))).toBeLessThanOrEqual(field.ceiling);
    }
    expect(terrainCeiling(level([section()]))).toBe(70);
    const shore = { path: STRAIGHT, landSide: 1, width: 10, seabed: 90 } as const;
    expect(terrainCeiling(level([section({ shore })]))).toBe(90);
  });

  it('P04 review: the ground cover of each section blends into the next one', () => {
    const grass = section({ surface: { lush: 1 } });
    const town = section({ surface: { paved: 1 } });
    const field = new HeightField(level([section(), grass, town], 40));
    expect(field.surface(50)).toEqual({ lush: 0, paved: 0 });
    expect(field.surface(150)).toEqual({ lush: 1, paved: 0 });
    expect(field.surface(200).lush).toBeCloseTo(0.5);
    expect(field.surface(200).paved).toBeCloseTo(0.5);
    expect(field.surface(260)).toEqual({ lush: 0, paved: 1 });
  });

  it('a meander line winds around its x', () => {
    const field = new HeightField(level([section()]));
    const path = { x: 30, amplitude: 50, wavelength: 400 };
    const xs = Array.from({ length: 40 }, (_, i) => field.pathX(path, i * 20));
    expect(Math.min(...xs)).toBeLessThan(0);
    expect(Math.max(...xs)).toBeGreaterThan(60);
  });
});
