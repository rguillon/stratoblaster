import { describe, expect, it } from 'vitest';
import {
  buildGroundTexture,
  buildNoiseTexture,
  buildWaterNormalMap,
  equalize,
  tileableFbm,
} from '../../../../src/render/scenery/procedural-textures';
import type { TextureLook } from '../../../../src/render/scenery/scenery-look';

const LOOK: TextureLook = {
  colors: [
    [0.2, 0.1, 0],
    [0.5, 0.4, 0.3],
    [0.8, 0.7, 0.6],
  ],
  frequency: 4,
  octaves: 3,
  speckle: 0.05,
  speckleColor: [1, 0, 1],
  strata: 0.3,
};

describe('procedural textures', () => {
  it('P04-R01: tileable noise matches across opposite edges', () => {
    const size = 32;
    const values = tileableFbm(size, 4, 3, 1);
    // The next pixel after the right edge is the first one of the row: compare the step across
    // the seam with an ordinary step.
    const row = (x: number) => values[5 * size + x] ?? 0;
    expect(Math.abs(row(size - 1) - row(0))).toBeLessThan(0.3);
    expect(values.every((v) => v >= -1 && v <= 1)).toBe(true);
    expect(tileableFbm(8, 0, 2, 1).every((v) => v === 0)).toBe(true);
  });

  it('equalize spreads values evenly over [0, 1], keeping their order', () => {
    expect([...equalize(new Float32Array([5, -1, 2]))]).toEqual([1, 0, 0.5]);
  });

  it('P04-R01: a ground texture uses its palette and speckles, fully opaque', () => {
    const size = 32;
    const pixels = buildGroundTexture(size, LOOK, 3);
    expect(pixels).toHaveLength(size * size * 4);
    let speckles = 0;
    for (let i = 0; i < size * size; i++) {
      expect(pixels[i * 4 + 3]).toBe(255);
      if (pixels[i * 4] === 255 && pixels[i * 4 + 2] === 255) speckles++;
      else expect(pixels[i * 4] ?? 0).toBeLessThanOrEqual(Math.round(0.8 * 255));
    }
    expect(speckles).toBeGreaterThan(0);
    expect(buildGroundTexture(size, LOOK, 3)).toEqual(pixels);
  });

  it('P04-R03: the noise texture spreads its values over the whole range', () => {
    const pixels = buildNoiseTexture(32, 4, 1);
    const reds = Array.from({ length: 32 * 32 }, (_, i) => pixels[i * 4] ?? 0);
    expect(Math.min(...reds)).toBe(0);
    expect(Math.max(...reds)).toBe(255);
  });

  it('P04-R02: the water normal map holds unit normals pointing up', () => {
    const size = 16;
    const pixels = buildWaterNormalMap(size, { frequency: 2, octaves: 2, strength: 5 }, 4);
    for (let i = 0; i < size * size; i++) {
      const [x, y, z] = [0, 1, 2].map((k) => ((pixels[i * 4 + k] ?? 0) / 255) * 2 - 1);
      expect(Math.hypot(x ?? 0, y ?? 0, z ?? 0)).toBeCloseTo(1, 1);
      expect(z).toBeGreaterThan(0);
    }
  });
});
