import { contrastRatio, relativeLuminance, srgbByteToLinear } from './color';

/** An RGBA image read back from the screen: 4 sRGB bytes per pixel, row after row. */
export interface Pixels {
  readonly width: number;
  readonly height: number;
  readonly data: ArrayLike<number>;
}

/** A square of pixels: its centre and half its side, in pixels of the image. */
export interface PixelBox {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
}

/** Relative luminance of the pixel at (`x`, `y`). */
export function luminanceAt(image: Pixels, x: number, y: number): number {
  const i = (y * image.width + x) * 4;
  const byte = (k: number) => srgbByteToLinear(image.data[i + k] ?? 0);
  return relativeLuminance([byte(0), byte(1), byte(2)]);
}

/** Luminances of the pixels of `box` inside the image. */
function boxLuminances(image: Pixels, box: PixelBox): number[] {
  const out: number[] = [];
  const x0 = Math.max(0, Math.round(box.x - box.radius));
  const x1 = Math.min(image.width - 1, Math.round(box.x + box.radius));
  const y0 = Math.max(0, Math.round(box.y - box.radius));
  const y1 = Math.min(image.height - 1, Math.round(box.y + box.radius));
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) out.push(luminanceAt(image, x, y));
  return out;
}

function median(values: readonly number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)] ?? 0;
}

/**
 * How well what is drawn in `box` stands out (phase 14, P14-R08): the contrast ratio between
 * its brightest pixel on `frame` and the median of the same pixels on `background` (the frame
 * drawn without the playfield, i.e. what is behind it). 1 when the box is off the image.
 */
export function boxContrast(frame: Pixels, background: Pixels, box: PixelBox): number {
  const drawn = boxLuminances(frame, box);
  if (drawn.length === 0) return 1;
  return contrastRatio(Math.max(...drawn), median(boxLuminances(background, box)));
}

/**
 * The luminance only `share` (0..1) of the image's pixels are brighter than (P14-R01: the
 * background's brightest, but for a few small lights).
 */
export function brightestBut(image: Pixels, share: number): number {
  const n = image.width * image.height;
  if (n === 0) return 0;
  const values = new Float32Array(n);
  for (let y = 0; y < image.height; y++) {
    for (let x = 0; x < image.width; x++) values[y * image.width + x] = luminanceAt(image, x, y);
  }
  values.sort();
  return values[Math.floor((1 - share) * (n - 1))] ?? 0;
}

/**
 * How readable the frame is (phase 14, P14-R08): the contrast ratio of each kind of object with
 * what is behind it (null when none is on screen), and the luminance of the background's
 * brightest pixels but for the share asked for.
 */
export interface ReadabilityReport {
  readonly player: number | null;
  readonly enemy: number | null;
  readonly enemyBullet: number | null;
  readonly playerShot: number | null;
  readonly backgroundLuminance: number;
}
