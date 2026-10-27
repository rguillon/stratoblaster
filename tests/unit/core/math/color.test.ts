import { describe, expect, it } from 'vitest';
import {
  contrastRatio,
  foldIntoFamily,
  hueSaturation,
  inFamily,
  relativeLuminance,
  srgbByteToLinear,
  veiled,
  type ColorFamily,
} from '../../../../src/core/math/color';

const WARM: ColorFamily = { from: 18, to: 58, minSaturation: 0.25 };
const WRAPPING: ColorFamily = { from: 265, to: 5, minSaturation: 0.25 };

describe('colour helpers (phase 14)', () => {
  it('P14-R08: luminance and contrast ratio follow WCAG 2', () => {
    expect(relativeLuminance([1, 1, 1])).toBeCloseTo(1);
    expect(relativeLuminance([0, 0, 0])).toBe(0);
    expect(relativeLuminance([0, 1, 0])).toBeCloseTo(0.7152);
    expect(contrastRatio(1, 0)).toBeCloseTo(21);
    expect(contrastRatio(0, 1)).toBeCloseTo(21);
    expect(contrastRatio(0.3, 0.3)).toBe(1);
    expect(srgbByteToLinear(0)).toBe(0);
    expect(srgbByteToLinear(255)).toBeCloseTo(1);
    expect(srgbByteToLinear(5)).toBeCloseTo(5 / 255 / 12.92);
    expect(srgbByteToLinear(128)).toBeCloseTo(0.2158, 3);
  });

  it('P14-R02: hue and saturation of primaries, secondaries and greys', () => {
    expect(hueSaturation([1, 0, 0])).toEqual({ hue: 0, saturation: 1 });
    expect(hueSaturation([0, 1, 0]).hue).toBeCloseTo(120);
    expect(hueSaturation([0, 0, 1]).hue).toBeCloseTo(240);
    expect(hueSaturation([1, 0, 1]).hue).toBeCloseTo(300);
    expect(hueSaturation([1, 0.5, 0]).hue).toBeCloseTo(30);
    expect(hueSaturation([0.4, 0.4, 0.4])).toEqual({ hue: 0, saturation: 0 });
  });

  it('P14-R02: a family holds the saturated colours of its hue range, wrapping past 0', () => {
    expect(inFamily([1, 0.5, 0], WARM)).toBe(true);
    expect(inFamily([1, 0, 0], WARM)).toBe(false);
    expect(inFamily([1, 0.95, 0.9], WARM)).toBe(false);
    expect(inFamily([1, 0, 1], WRAPPING)).toBe(true);
    expect(inFamily([1, 0, 0.02], WRAPPING)).toBe(true);
    expect(inFamily([1, 0.05, 0], WRAPPING)).toBe(true);
    expect(inFamily([1, 0.3, 0], WRAPPING)).toBe(false);
    expect(inFamily([0, 1, 1], WRAPPING)).toBe(false);
  });

  it('P14-R02: folding moves any colour into the family, keeping order, value and saturation', () => {
    const colors = [
      [0.1, 0.95, 1],
      [0.2, 1, 0.3],
      [1, 0.5, 0.05],
      [0.15, 0.4, 1],
      [1, 0.1, 0.85],
    ] as const;
    const folded = colors.map((c) => foldIntoFamily(c, WRAPPING));
    for (const [i, f] of folded.entries()) {
      expect(inFamily(f, WRAPPING)).toBe(true);
      const before = hueSaturation(colors[i] ?? [0, 0, 0]);
      expect(hueSaturation(f).saturation).toBeCloseTo(before.saturation);
      expect(Math.max(...f)).toBeCloseTo(Math.max(...(colors[i] ?? [0, 0, 0])));
    }
    expect(new Set(folded.map((f) => f.map((c) => c.toFixed(2)).join())).size).toBe(5);
    expect(foldIntoFamily([0.5, 0.5, 0.5], WARM)).toEqual([0.5, 0.5, 0.5]);
  });

  it('P14-R01: a veil pulls a colour towards its own by its opacity', () => {
    expect(veiled([1, 1, 1], { color: [0, 0, 0], opacity: 0.4 })).toEqual([0.6, 0.6, 0.6]);
    const v = veiled([1, 0, 0], { color: [0, 0, 1], opacity: 0.5 });
    expect(v).toEqual([0.5, 0, 0.5]);
    expect(veiled([0.2, 0.3, 0.4], { color: [1, 1, 1], opacity: 0 })).toEqual([0.2, 0.3, 0.4]);
  });
});
