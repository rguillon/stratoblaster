import { createRng } from './rng';

/** A smooth 2D noise function returning values in [-1, 1]. */
export type Noise2D = (x: number, y: number) => number;

const TABLE_SIZE = 256;

function smootherstep(t: number): number {
  return t * t * t * (t * (t * 6 - 15) + 10);
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function wrap(i: number, period: number): number {
  return ((i % period) + period) % period;
}

/**
 * Seeded 2D gradient noise (Perlin style). With a `period`, the lattice wraps every `period`
 * units, so the noise tiles seamlessly on a `period × period` square (for textures).
 */
export function createNoise2D(seed: number, period = TABLE_SIZE): Noise2D {
  const random = createRng(seed);
  const perm = Array.from({ length: TABLE_SIZE }, (_, i) => i);
  for (let i = TABLE_SIZE - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [perm[i], perm[j]] = [perm[j] ?? 0, perm[i] ?? 0];
  }
  const angles = Array.from({ length: TABLE_SIZE }, () => random() * Math.PI * 2);
  // P13-R03: each angle's cosine and sine worked out once (the same values, every call).
  const table = Int32Array.from(perm);
  const cos = Float64Array.from(angles, Math.cos);
  const sin = Float64Array.from(angles, Math.sin);
  const p = Math.max(1, Math.floor(period));
  const gradient = (ix: number, iy: number, dx: number, dy: number): number => {
    const h = table[(wrap(ix, p) + (table[wrap(iy, p) % TABLE_SIZE] ?? 0)) % TABLE_SIZE] ?? 0;
    return (cos[h] ?? 1) * dx + (sin[h] ?? 0) * dy;
  };
  return (x, y) => {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    const fx = x - ix;
    const fy = y - iy;
    const u = smootherstep(fx);
    const v = smootherstep(fy);
    const bottom = lerp(gradient(ix, iy, fx, fy), gradient(ix + 1, iy, fx - 1, fy), u);
    const top = lerp(gradient(ix, iy + 1, fx, fy - 1), gradient(ix + 1, iy + 1, fx - 1, fy - 1), u);
    // Gradient noise peaks at about ±0.71 in 2D: scale it to fill [-1, 1].
    return Math.max(-1, Math.min(1, lerp(bottom, top, v) * Math.SQRT2));
  };
}

/** Octave settings of {@link fbm} and {@link ridged}. */
export interface OctaveOptions {
  readonly octaves: number;
  /** Frequency multiplier between octaves (usually 2). */
  readonly lacunarity: number;
  /** Amplitude multiplier between octaves (usually 0.5). */
  readonly gain: number;
}

/** Fractal sum of `noise` octaves, normalised back to [-1, 1]. */
export function fbm(noise: Noise2D, x: number, y: number, options: OctaveOptions): number {
  let sum = 0;
  let amplitude = 1;
  let frequency = 1;
  let total = 0;
  for (let i = 0; i < options.octaves; i++) {
    sum += noise(x * frequency, y * frequency) * amplitude;
    total += amplitude;
    amplitude *= options.gain;
    frequency *= options.lacunarity;
  }
  return total > 0 ? sum / total : 0;
}

/**
 * Ridged fractal noise in [0, 1]: sharp crests where the noise crosses zero, for mountain
 * ranges. Each octave is weighted by the previous one, so detail gathers on the crests.
 */
export function ridged(noise: Noise2D, x: number, y: number, options: OctaveOptions): number {
  let sum = 0;
  let amplitude = 1;
  let frequency = 1;
  let total = 0;
  let weight = 1;
  for (let i = 0; i < options.octaves; i++) {
    const crest = 1 - Math.abs(noise(x * frequency, y * frequency));
    const value = crest * crest * weight;
    weight = Math.min(1, value * 2);
    sum += value * amplitude;
    total += amplitude;
    amplitude *= options.gain;
    frequency *= options.lacunarity;
  }
  return total > 0 ? sum / total : 0;
}

/** 0 below `edge0`, 1 above `edge1`, smooth in between. */
export function smoothstep(edge0: number, edge1: number, x: number): number {
  if (edge0 === edge1) return x < edge0 ? 0 : 1;
  const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

/** A well-mixed 32-bit hash of integer coordinates and a seed, as a number in [0, 1). */
export function hash2D(x: number, y: number, seed: number): number {
  let h =
    Math.imul(x | 0, 0x27d4eb2d) ^ Math.imul(y | 0, 0x165667b1) ^ Math.imul(seed | 0, 0x9e3779b1);
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
