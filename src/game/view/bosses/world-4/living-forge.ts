import { curve, organ, ribs, tendril, vein } from '../../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { reactorSac } from '../../enemies/organic-parts';
import { FORGE } from './black-sands-kit';

// P16-R05, P16-R06: the Cyber-Organic pieces of the World 4 bosses (the volcanic, ash and foundry
// world): scorched flesh swollen around metal grafts, molten veins and glands glowing ember.
// Logical pixels, nose +Z, Y up.
type Vec3 = readonly [number, number, number];
type Rgb = readonly [number, number, number];

/** The flesh shades (P16-R01). */
export const FL = ENEMY_LOOK.flesh;
/** Scorched flesh: the World 4 bodies, by role (base body, sinews and muscles, folds). */
export const SKIN = { base: FL.crimson, panel: FL.sinew, dark: FL.membrane, bone: FL.bone };
/** The molten glow of their veins and glands. */
export const MAGMA: Rgb = FORGE.molten;

/** A muscle or sinew from `a` to `b`, bowed up by `bow`, `r` thick at `a` thinning to `rb`. */
export function sinew(
  b: EnemyParts['flesh'],
  [a, c]: readonly [Vec3, Vec3],
  [r, rb]: readonly [number, number],
  color: Rgb = SKIN.panel,
  bow = 1.5,
): void {
  tendril(b, curve(a, c, [0, bow, 0], 3), [r, rb], 5, color);
}

/** Ribs arching over a back at each z of `zs`, bone pale. */
export function backRibs(
  p: EnemyParts,
  zs: readonly number[],
  arch: { halfWidth: number; y: number; height: number; thickness: number },
  color: Rgb = SKIN.bone,
): void {
  ribs(p.flesh, zs, arch, color);
}

/** Glowing glands (pulsing, P16-R07) of `radius` at each point. */
export function glands(p: EnemyParts, at: readonly Vec3[], radius: number, glow: Rgb): void {
  for (const g of at) organ(p.vein, radius, 5, glow, { at: g }, 0.6);
}

/** Fleshy lumps (swollen growths) of `radius` at each point. */
export function lumps(
  p: EnemyParts,
  at: readonly Vec3[],
  radius: number,
  color: Rgb = SKIN.base,
  stretch = 0.7,
): void {
  for (const g of at) organ(p.flesh, radius, 6, color, { at: g }, stretch);
}

/** A molten vein (pulsing) through `points`, `width` across. */
export function magmaVein(
  p: EnemyParts,
  points: readonly Vec3[],
  width: number,
  glow: Rgb = MAGMA,
): void {
  for (let i = 1; i < points.length; i++) {
    const [a, b] = [points[i - 1], points[i]];
    if (a && b) vein(p.vein, curve(a, b, [0, width * 0.6, 0], 2), width, glow);
  }
}

/** Reactors at the back, each set in a glowing flesh sac with a vein forward. */
export function reactorSacs(p: EnemyParts, at: readonly Vec3[], radius: number, glow: Rgb): void {
  for (const r of at) reactorSac(p, r, radius, glow, { flesh: SKIN.base });
}

/** A fleshy shell lofted through `stations` on `section`, its bands alternately `color`, `seam`. */
export function fleshShell(
  b: EnemyParts['flesh'],
  section: Parameters<EnemyParts['flesh']['loft']>[0],
  stations: Parameters<EnemyParts['flesh']['loft']>[1],
  [color, seam]: readonly [Rgb, Rgb] = [SKIN.base, SKIN.dark],
): void {
  b.loft(
    section,
    stations,
    color,
    {},
    { paint: (_s, band) => (band % 2 === 1 ? seam : undefined) },
  );
}
