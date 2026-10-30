import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { strip } from '../final-boss-shapes';

// P10-R11: the ash and heavy industry on the 4-2 bosses (the Ash Wraith and the Geyser Rig):
// drifts of grey ash on their plates, soot streaks, glowing molten seams (GD-61, World 4: dark
// metal with neon, plus soot, heat glow, molten seams). Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Ash: a pale grey, and a darker one where it lies thin over the metal. */
export const ASH: Rgb = [0.3, 0.29, 0.28];
export const ASH_THIN: Rgb = [0.19, 0.185, 0.18];
/** Soot: burnt black, a little warm. */
export const SOOT: Rgb = [0.03, 0.025, 0.025];
/** The glow of hot metal in a seam (drawn on the neon builder: always lit). */
export const EMBER: Rgb = [1, 0.38, 0.06];
/** A hot, rusty plate around a vent. */
export const SCORCH: Rgb = [0.17, 0.09, 0.05];

/**
 * A drift of ash `radius` wide lying at `at`: an uneven, low hexagon, paler on top. `seed` turns
 * and bends its outline so no two drifts look alike.
 */
export function ashDrift(hull: SolidBuilder, at: Vec3, radius: number, seed = 0): void {
  const outline = Array.from({ length: 6 }, (_, k): OutlinePoint => {
    const a = (k * Math.PI) / 3 + seed;
    const r = radius * (0.7 + 0.3 * Math.sin(seed * 2.7 + k * 1.9));
    return [Math.cos(a) * r, Math.sin(a) * r];
  });
  hull.bevelSlab(outline, [-0.3, 0, 0.7], [0, radius * 0.3], ASH_THIN, { at }, ASH);
}

/** Soot streaks at height `y`: a thin dark strip along each `[from, to]` (seen from above). */
export function sootStreaks(
  hull: SolidBuilder,
  streaks: readonly (readonly [OutlinePoint, OutlinePoint])[],
  y: number,
  width = 1.6,
): void {
  for (const [a, b] of streaks) strip(hull, a, b, width, [y, y + 0.15], SOOT);
}

/**
 * A molten seam from `a` to `b` (seen from above) at height `y`: a dark groove with a glowing
 * line of hot metal in it.
 */
export function moltenSeam(
  { hull, neon }: { readonly hull: SolidBuilder; readonly neon: SolidBuilder },
  a: OutlinePoint,
  b: OutlinePoint,
  y: number,
  width = 1.4,
): void {
  strip(hull, a, b, width * 1.8, [y, y + 0.12], SOOT);
  strip(neon, a, b, width * 0.6, [y + 0.12, y + 0.3], EMBER);
}
