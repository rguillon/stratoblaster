import {
  carapace,
  curve,
  organ,
  ribs,
  tendril,
  vein,
  type SegmentedBody,
} from '../../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';

// P16-R05, P16-R06: the Cyber-Organic pieces of the World 3 bosses (the jungle and its river):
// living bodies grown over by the jungle, metal grafted on. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** The flesh shades (P16-R01). */
export const F = ENEMY_LOOK.flesh;

/** A jungle-green flesh, dark enough for the ground (P14-R04): moss-skinned bodies. */
export const JUNGLE_FLESH: Rgb = [0.05, 0.1, 0.045];

/**
 * A spine down a back (P16-R05): a pulsing vein along `path` and, at each of `at` (z), a rib
 * arch `halfWidth` out over it from `y`, in bone.
 */
export function spine(
  p: EnemyParts,
  path: readonly Vec3[],
  arches: { at: readonly number[]; halfWidth: number; y: number; height: number },
  glow: Rgb,
): void {
  vein(p.vein, path, 1.2, glow);
  ribs(p.flesh, arches.at, { ...arches, thickness: 0.7 }, F.bone);
}

/** A ridged shell (P16-R01) over a back: plates of `color`, darker seams between them. */
export function shell(
  p: EnemyParts,
  body: SegmentedBody,
  color: Rgb = F.teal,
  place: { at?: Vec3; yaw?: number } = {},
): void {
  const seam: Rgb = [color[0] * 0.45, color[1] * 0.45, color[2] * 0.45];
  carapace(p.flesh, body, [color, seam], place);
}

/** A glowing gland (P16-R01) of `radius` sitting at `at`, pulsing with the veins. */
export function gland(p: EnemyParts, at: Vec3, radius: number, glow: Rgb): void {
  organ(p.vein, radius, 5, glow, { at }, 0.6);
}

/** A swollen flesh sac (P16-R01) of `radius` at `at`, `stretch` times as tall. */
export function sac(p: EnemyParts, at: Vec3, radius: number, color: Rgb, stretch = 0.7): void {
  organ(p.flesh, radius, 6, color, { at: [at[0], at[1] - radius * stretch, at[2]] }, stretch);
}

/** A sinew from `from` to `to` bowed by `bow`: a tapering flesh tendril, `radius` thick. */
export function sinew(
  p: EnemyParts,
  [from, to]: readonly [Vec3, Vec3],
  bow: Vec3,
  radius: number,
  color: Rgb = F.sinew,
): void {
  tendril(p.flesh, curve(from, to, bow, 3), [radius, radius * 0.4], 4, color);
}

/** A vein from `from` to `to` bowed by `bow`, `width` across, pulsing (P16-R07). */
export function veinTo(
  p: EnemyParts,
  [from, to]: readonly [Vec3, Vec3],
  bow: Vec3,
  glow: Rgb,
  width = 0.9,
): void {
  vein(p.vein, curve(from, to, bow, 3), width, glow);
}
