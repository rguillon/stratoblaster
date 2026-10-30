import { describe, expect, it } from 'vitest';
import { createRng } from '../../../../src/core/math/rng';
import { TITLE_LOOK } from '../../../../src/game/config/title-look';
import { buildCityChunk, buildRain, buildSkyline } from '../../../../src/game/view/city-geometry';
import type { ColoredGeometry } from '../../../../src/render/geometry/gradient-shapes';

function axis(geo: ColoredGeometry, offset: number): number[] {
  return geo.positions.filter((_, i) => i % 3 === offset);
}

function expectWellFormed(geo: ColoredGeometry): void {
  const vertices = geo.positions.length / 3;
  expect(geo.colors.length).toBe(vertices * 4);
  expect(geo.indices.length % 3).toBe(0);
  expect(Math.max(...geo.indices)).toBeLessThan(vertices);
}

describe('buildCityChunk', () => {
  const { city } = TITLE_LOOK;

  it('P01-R05: builds the same city for the same seed', () => {
    const a = buildCityChunk(city, createRng(1));
    const b = buildCityChunk(city, createRng(1));
    expect(a.lights.positions).toEqual(b.lights.positions);
    expect(buildCityChunk(city, createRng(2)).lights.positions).not.toEqual(a.lights.positions);
  });

  it('P01-R05: dark buildings line both sides of the street, inside the chunk', () => {
    const { structure } = buildCityChunk(city, createRng(1));
    expectWellFormed(structure);
    const zs = axis(structure, 2);
    expect(Math.min(...zs)).toBeGreaterThanOrEqual(0);
    expect(Math.max(...zs)).toBeLessThanOrEqual(city.length);
    // Apart from the ground (Y = 0), nothing stands in the street.
    const xs = axis(structure, 0);
    const ys = axis(structure, 1);
    xs.forEach((x, i) => {
      if ((ys[i] ?? 0) > 0) expect(Math.abs(x)).toBeGreaterThanOrEqual(city.streetHalfWidth);
    });
    expect(xs.some((x) => x < -city.streetHalfWidth)).toBe(true);
    expect(xs.some((x) => x > city.streetHalfWidth)).toBe(true);
  });

  it('P01-R05: neon lights (windows, signs, trims, lanes) are bright, buildings are dark', () => {
    const { structure, lights } = buildCityChunk(city, createRng(1));
    expectWellFormed(lights);
    expect(lights.indices.length / 6).toBeGreaterThan(500);
    const brightest = (geo: ColoredGeometry) =>
      Math.max(...geo.colors.filter((_, i) => i % 4 !== 3));
    expect(brightest(structure)).toBeLessThan(0.1);
    expect(brightest(lights)).toBeGreaterThan(0.9);
    // Above the lane lines, only blade signs hang into the street, from the facades.
    const xs = axis(lights, 0);
    const ys = axis(lights, 1);
    const maxSign = city.signs.width[1] + 0.1;
    xs.forEach((x, i) => {
      if ((ys[i] ?? 0) > 0.1 && Math.abs(x) < city.streetHalfWidth - 0.2) {
        expect(Math.abs(x)).toBeGreaterThanOrEqual(city.streetHalfWidth - maxSign - 0.01);
      }
    });
  });
});

describe('buildSkyline', () => {
  it('P01-R05: covers the whole width with towers, and lit windows in front of them', () => {
    const { skyline } = TITLE_LOOK;
    const { structure, lights } = buildSkyline(skyline, createRng(1));
    expectWellFormed(structure);
    expectWellFormed(lights);
    const xs = axis(structure, 0);
    expect(Math.min(...xs)).toBe(-skyline.halfWidth);
    expect(Math.max(...xs)).toBeGreaterThanOrEqual(skyline.halfWidth);
    expect(lights.indices.length).toBeGreaterThan(0);
    expect(new Set(axis(lights, 2))).toEqual(new Set([-0.05]));
  });
});

describe('buildRain', () => {
  it('P01-R05: draws each drop twice, one rain height apart, so the loop has no gap', () => {
    const rain = { ...TITLE_LOOK.rain, count: 3 };
    const geo = buildRain(rain, createRng(1));
    expectWellFormed(geo);
    expect(geo.indices.length / 6).toBe(6);
    const ys = axis(geo, 1);
    // Vertices 0-3: first copy of drop 0; vertices 4-7: its second copy.
    expect(ys[4] ?? NaN).toBeCloseTo((ys[0] ?? NaN) + rain.height);
  });
});
