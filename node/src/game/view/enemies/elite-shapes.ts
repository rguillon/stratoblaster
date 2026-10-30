import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from './enemy-mesh';

// Shapes shared by the elite models (P05-R19 to P05-R23). Logical pixels, nose +Z, Y up; a
// design point (x, y) facing down the screen is model (-x, height, -y) (`bossPoint`).

type Vec3 = readonly [number, number, number];
type Rgb = readonly [number, number, number];

export const H = ENEMY_LOOK.hull;
export const WHITE: Rgb = [1, 1, 1];
export const QUARTER = Math.PI / 2;

/*
 * Something pointing `aim` (radians clockwise on screen from the nose, a part's `aim`) is drawn
 * with that same yaw: facing down the screen, the two agree.
 */

/** The point `d` from `at` along `yaw` (radians from +Z towards +X), at the same height. */
export function ahead([x, y, z]: Vec3, yaw: number, d: number): [number, number, number] {
  return [x + Math.sin(yaw) * d, y, z + Math.cos(yaw) * d];
}

/**
 * A gun barrel pointing `yaw`, ending at `tip`, `radius` thick and `length` long: dark steel,
 * a charge light at its mouth, the muzzle (`kind`) marked at the tip.
 */
export function barrel(
  p: EnemyParts,
  tip: Vec3,
  yaw: number,
  [radius, length]: readonly [number, number],
  kind = 'gun',
): void {
  const place = (back: number) => ({ at: ahead(tip, yaw, -back), pitch: QUARTER, yaw });
  p.hull.cylinder(radius, length, 6, H.dark, place(length + 0.5));
  p.charge.cylinder(radius * 1.08, 0.5, 6, WHITE, place(0.5));
  p.muzzle(tip, kind);
}

/** A neon strip `length` long, centred `d` from `at` along `yaw`, `width` wide, raised `lift`. */
export function strip(
  neon: SolidBuilder,
  at: Vec3,
  yaw: number,
  [d, length, width]: readonly [number, number, number],
  color: Rgb,
): void {
  const [x, y, z] = ahead(at, yaw, d);
  neon.box([width, 0.5, length], color, { at: [x, y, z], yaw });
}
