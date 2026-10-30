import { describe, expect, it } from 'vitest';
import { createNoise2D, fbm, hash2D, ridged, smoothstep } from '../../../../src/core/math/noise';
import { createRng } from '../../../../src/core/math/rng';

const OCTAVES = { octaves: 4, lacunarity: 2, gain: 0.5 };

function samples(f: (x: number, y: number) => number): number[] {
  const values: number[] = [];
  for (let i = 0; i < 400; i++) values.push(f(i * 0.37, i * 0.21 + 3));
  return values;
}

describe('createNoise2D', () => {
  it('P04-R01: is deterministic for a seed, and differs between seeds', () => {
    const a = createNoise2D(5);
    const b = createNoise2D(5);
    const c = createNoise2D(6);
    expect(samples(a)).toEqual(samples(b));
    expect(samples(a)).not.toEqual(samples(c));
  });

  it('stays in [-1, 1], is zero on lattice points and varies smoothly', () => {
    const noise = createNoise2D(1);
    for (const v of samples(noise)) {
      expect(Math.abs(v)).toBeLessThanOrEqual(1);
    }
    expect(noise(3, 7)).toBeCloseTo(0);
    expect(Math.abs(noise(2.5, 1.5) - noise(2.501, 1.5))).toBeLessThan(0.01);
    expect(new Set(samples(noise).map((v) => v.toFixed(2))).size).toBeGreaterThan(50);
  });

  it('tiles with a period', () => {
    const noise = createNoise2D(9, 4);
    expect(noise(0.3, 1.7)).toBeCloseTo(noise(4.3, 1.7));
    expect(noise(0.3, 1.7)).toBeCloseTo(noise(0.3, 5.7));
  });
});

describe('fbm and ridged', () => {
  const noise = createNoise2D(3);

  it('fbm stays in [-1, 1] and averages about 0', () => {
    const values = samples((x, y) => fbm(noise, x, y, OCTAVES));
    for (const v of values) expect(Math.abs(v)).toBeLessThanOrEqual(1);
    expect(Math.abs(values.reduce((a, b) => a + b, 0) / values.length)).toBeLessThan(0.15);
  });

  it('ridged stays in [0, 1]', () => {
    for (const v of samples((x, y) => ridged(noise, x, y, OCTAVES))) {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThanOrEqual(1);
    }
  });

  it('give 0 without octaves', () => {
    expect(fbm(noise, 1, 2, { ...OCTAVES, octaves: 0 })).toBe(0);
    expect(ridged(noise, 1, 2, { ...OCTAVES, octaves: 0 })).toBe(0);
  });
});

describe('smoothstep and hash2D', () => {
  it('smoothstep goes from 0 to 1 between the edges', () => {
    expect(smoothstep(0, 10, -1)).toBe(0);
    expect(smoothstep(0, 10, 5)).toBe(0.5);
    expect(smoothstep(0, 10, 11)).toBe(1);
    expect(smoothstep(4, 4, 3)).toBe(0);
    expect(smoothstep(4, 4, 4)).toBe(1);
  });

  it('hash2D is stable, in [0, 1), and spread', () => {
    expect(hash2D(1, 2, 3)).toBe(hash2D(1, 2, 3));
    const values = Array.from({ length: 1000 }, (_, i) => hash2D(i % 37, Math.floor(i / 37), 11));
    for (const v of values) {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    expect(mean).toBeGreaterThan(0.45);
    expect(mean).toBeLessThan(0.55);
  });
});

describe('createNoise2D, with its tables worked out once (P13-R03)', () => {
  /** The noise as it was before phase 13: cosine and sine on every call. */
  function reference(seed: number, period = 256): (x: number, y: number) => number {
    const random = createRng(seed);
    const perm = Array.from({ length: 256 }, (_, i) => i);
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [perm[i], perm[j]] = [perm[j] ?? 0, perm[i] ?? 0];
    }
    const angles = Array.from({ length: 256 }, () => random() * Math.PI * 2);
    const p = Math.max(1, Math.floor(period));
    const wrap = (i: number) => ((i % p) + p) % p;
    const g = (ix: number, iy: number, dx: number, dy: number) => {
      const a = angles[perm[(wrap(ix) + (perm[wrap(iy) % 256] ?? 0)) % 256] ?? 0] ?? 0;
      return Math.cos(a) * dx + Math.sin(a) * dy;
    };
    const s = (t: number) => t * t * t * (t * (t * 6 - 15) + 10);
    const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
    return (x, y) => {
      const [ix, iy] = [Math.floor(x), Math.floor(y)];
      const [fx, fy] = [x - ix, y - iy];
      const bottom = lerp(g(ix, iy, fx, fy), g(ix + 1, iy, fx - 1, fy), s(fx));
      const top = lerp(g(ix, iy + 1, fx, fy - 1), g(ix + 1, iy + 1, fx - 1, fy - 1), s(fx));
      return Math.max(-1, Math.min(1, lerp(bottom, top, s(fy)) * Math.SQRT2));
    };
  }

  it('P13-R05: gives exactly the values it gave before, tiling or not', () => {
    for (const [seed, period] of [
      [1, 256],
      [42, 256],
      [7, 8],
    ] as const) {
      const [now, before] = [createNoise2D(seed, period), reference(seed, period)];
      for (let x = -20; x < 20; x += 0.37) {
        for (let y = -20; y < 20; y += 0.41) expect(now(x, y)).toBe(before(x, y));
      }
    }
  });
});
