import { describe, expect, it } from 'vitest';
import {
  boxContrast,
  brightestBut,
  luminanceAt,
  type Pixels,
} from '../../../../src/core/math/pixel-contrast';

/** A `size` × `size` grey image of `byte`, with `paint` applied to some pixels. */
function image(
  size: number,
  byte: number,
  paint: (x: number, y: number) => number | null = () => null,
): Pixels {
  const data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const v = paint(x, y) ?? byte;
      data.set([v, v, v, 255], (y * size + x) * 4);
    }
  }
  return { width: size, height: size, data };
}

describe('pixel contrast (P14-R08)', () => {
  it('P14-R08: reads the luminance of a pixel from its sRGB bytes', () => {
    const img = image(4, 0, (x, y) => (x === 1 && y === 2 ? 255 : null));
    expect(luminanceAt(img, 1, 2)).toBeCloseTo(1);
    expect(luminanceAt(img, 0, 0)).toBe(0);
  });

  it('P14-R08: compares the brightest pixel of a box with the median behind it', () => {
    const background = image(20, 20);
    const frame = image(20, 20, (x, y) => (x === 10 && y === 10 ? 255 : null));
    const behind = luminanceAt(background, 10, 10);
    expect(boxContrast(frame, background, { x: 10, y: 10, radius: 3 })).toBeCloseTo(
      1.05 / (behind + 0.05),
    );
    expect(boxContrast(background, background, { x: 10, y: 10, radius: 3 })).toBeCloseTo(1);
    // Off the image: nothing to measure.
    expect(boxContrast(frame, background, { x: -50, y: -50, radius: 3 })).toBe(1);
  });

  it('P14-R08: a box at the edge is clipped to the image', () => {
    const background = image(10, 0);
    const frame = image(10, 0, (x, y) => (x === 0 && y === 0 ? 255 : null));
    expect(boxContrast(frame, background, { x: 0, y: 0, radius: 2 })).toBeCloseTo(21);
  });

  it('P14-R01: finds the luminance all but a share of the pixels stay under', () => {
    // 100 pixels: 3 white, the rest black.
    const img = image(10, 0, (x, y) => (y === 0 && x < 3 ? 255 : null));
    expect(brightestBut(img, 0.02)).toBeCloseTo(1);
    expect(brightestBut(img, 0.05)).toBe(0);
    expect(brightestBut({ width: 0, height: 0, data: [] }, 0.02)).toBe(0);
  });
});
