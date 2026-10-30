import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';

// P08-R10: the frost on the 2-1 bosses (World 2 theme: dark metal with neon, plus frost, ice
// and snow). Logical pixels, nose +Z, Y up. Pale vertex colours on the hull's top faces.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Frost shades: snow caps, frosted panels, clear blue ice. */
export const FROST = {
  /** Snow and ice crust on top faces. */
  snow: [0.75, 0.82, 0.9] as Rgb,
  /** A frosted panel: hull metal under a thin rime. */
  panel: [0.42, 0.48, 0.56] as Rgb,
  /** Clear ice: icicles, chunks of floe stuck on the hull. */
  ice: [0.5, 0.66, 0.82] as Rgb,
};

/** An icicle hanging from `at`, `length` long: a thin four-sided cone pointing down. */
export function icicle(hull: SolidBuilder, at: Vec3, length: number): void {
  hull.cylinder(length * 0.22, length, 4, FROST.ice, { at, pitch: Math.PI }, 0);
}

/** Icicles under every `every`-th corner of `outline` at height `y`, of varying lengths. */
export function icicles(
  hull: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  every: number,
): void {
  outline.forEach(([x, z], i) => {
    if (i % every === 0) icicle(hull, [x * 0.97, y, z * 0.97], 2.5 + (i % 3));
  });
}

/** A chunk of floe ice stuck on the hull at `at`, `size` across: a low faceted lump. */
export function iceChunk(hull: SolidBuilder, at: Vec3, size: number): void {
  const lump = [
    [size, 0],
    [size * 1.1, size * 0.35],
    [size * 0.6, size * 0.8],
    [0, size * 0.9],
  ] as const;
  hull.lathe(lump, 5, FROST.ice, { at, yaw: size });
}
