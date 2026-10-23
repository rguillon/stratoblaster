import { createNoise2D, hash2D } from '../../core/math/noise';
import type { TextureLook } from './scenery-look';

type Rgb = readonly [number, number, number];

/** Largest lattice period the noise supports (its permutation table size). */
const MAX_PERIOD = 256;

/**
 * Fractal noise on a `size × size` grid that tiles seamlessly: octave `k` has `frequency × 2^k`
 * cycles across the grid, each with its own wrapping lattice. Values are in [-1, 1].
 */
export function tileableFbm(
  size: number,
  frequency: number,
  octaves: number,
  seed: number,
): Float32Array {
  const values = new Float32Array(size * size);
  let total = 0;
  for (let k = 0; k < octaves; k++) {
    const period = Math.round(frequency * 2 ** k);
    if (period < 1 || period > MAX_PERIOD) break;
    const noise = createNoise2D(seed + k, period);
    const amplitude = 0.5 ** k;
    total += amplitude;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const i = y * size + x;
        values[i] = (values[i] ?? 0) + amplitude * noise((x / size) * period, (y / size) * period);
      }
    }
  }
  return total > 0 ? values.map((v) => v / total) : values;
}

/** Ranks of `values` scaled to [0, 1]: the same order, but evenly spread (histogram equalised). */
export function equalize(values: Float32Array): Float32Array {
  const order = Array.from(values.keys()).sort((a, b) => (values[a] ?? 0) - (values[b] ?? 0));
  const out = new Float32Array(values.length);
  const last = Math.max(1, values.length - 1);
  order.forEach((index, rank) => {
    out[index] = rank / last;
  });
  return out;
}

function byte(v: number): number {
  return Math.round(Math.min(1, Math.max(0, v)) * 255);
}

function mixRgb(a: Rgb, b: Rgb, t: number): [number, number, number] {
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
}

/** Colour of a ground texture for a noise value `n` in [0, 1]. */
function groundColor(look: TextureLook, n: number): [number, number, number] {
  const [dark, base, light] = look.colors;
  return n < 0.5 ? mixRgb(dark, base, n * 2) : mixRgb(base, light, (n - 0.5) * 2);
}

/** How far the ground noise spreads from the base colour towards the dark and light ones. */
const GROUND_CONTRAST = 1.2;

/** RGBA8 pixels of a tiling ground texture (P04-R01). */
export function buildGroundTexture(size: number, look: TextureLook, seed: number): Uint8Array {
  const noise = tileableFbm(size, look.frequency, look.octaves, seed).map((v) =>
    Math.min(1, Math.max(0, 0.5 + v * GROUND_CONTRAST)),
  );
  const bands = tileableFbm(size, look.frequency / 2, 2, seed + 50);
  const pixels = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const i = y * size + x;
      // Strata: bands along X whose phase wanders with a second noise; a whole number of bands
      // across the texture keeps it tiling.
      const band = Math.sin(((y / size) * look.frequency * 2 + (bands[i] ?? 0)) * Math.PI * 2);
      const n = (noise[i] ?? 0) * (1 - look.strata) + look.strata * (band * 0.5 + 0.5);
      const speck = hash2D(x, y, seed) < look.speckle;
      const rgb = speck ? look.speckleColor : groundColor(look, n);
      pixels.set([byte(rgb[0]), byte(rgb[1]), byte(rgb[2]), 255], i * 4);
    }
  }
  return pixels;
}

/**
 * RGBA8 pixels of a tiling noise texture: R fine noise (`frequency` cycles), G coarse noise
 * (a quarter of it), both evenly spread over [0, 1].
 */
export function buildNoiseTexture(size: number, frequency: number, seed: number): Uint8Array {
  const fine = equalize(tileableFbm(size, frequency, 4, seed));
  const coarse = equalize(tileableFbm(size, Math.max(1, frequency / 4), 3, seed + 10));
  const pixels = new Uint8Array(size * size * 4);
  for (let i = 0; i < size * size; i++) {
    pixels.set([byte(fine[i] ?? 0), byte(coarse[i] ?? 0), 0, 255], i * 4);
  }
  return pixels;
}

/**
 * RGBA8 pixels of a tiling normal map of small waves (P04-R02): the slope of a fractal height
 * map, `strength` times steeper, encoded as tangent-space normals.
 */
export function buildWaterNormalMap(
  size: number,
  options: { readonly frequency: number; readonly octaves: number; readonly strength: number },
  seed: number,
): Uint8Array {
  const heights = tileableFbm(size, options.frequency, options.octaves, seed);
  const at = (x: number, y: number): number =>
    heights[((y + size) % size) * size + ((x + size) % size)] ?? 0;
  const pixels = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (at(x + 1, y) - at(x - 1, y)) * options.strength;
      const dy = (at(x, y + 1) - at(x, y - 1)) * options.strength;
      const length = Math.hypot(dx, dy, 1);
      const n = [-dx / length, -dy / length, 1 / length];
      pixels.set([...n.map((c) => byte(c * 0.5 + 0.5)), 255], (y * size + x) * 4);
    }
  }
  return pixels;
}
