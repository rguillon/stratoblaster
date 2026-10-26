import type { Muzzle } from '../../../../core/entities/muzzle';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { H, QUARTER, WHITE } from '../mini-boss-shapes';

// P09-R09, 3-1: the river growth on the Mangrove Croc and the River Leviathan (GD-61, the World
// 3 theme: dark metal with neon, plus moss, vines and stone). Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Swamp shades: moss, vines, river stone, old bone-white teeth. */
export const SWAMP = {
  moss: [0.09, 0.15, 0.05] as Rgb,
  mossLight: [0.14, 0.2, 0.07] as Rgb,
  vine: [0.05, 0.1, 0.035] as Rgb,
  stone: [0.17, 0.16, 0.14] as Rgb,
  tooth: [0.42, 0.4, 0.34] as Rgb,
  mud: [0.1, 0.08, 0.05] as Rgb,
};

/** A patch of moss lying on a hull at height `y`: a thin, lumpy slab over `outline`. */
export function moss(hull: SolidBuilder, outline: readonly OutlinePoint[], y: number): void {
  hull.slab(outline, [y - 0.3, y + 0.6], SWAMP.moss, {}, SWAMP.mossLight);
}

/**
 * A vine hanging from `from` to `to`, sagging `sag` below the line between them: two thin
 * stems meeting at the low point, a leaf there.
 */
export function vine(hull: SolidBuilder, from: Vec3, to: Vec3, sag: number): void {
  const low: Vec3 = [(from[0] + to[0]) / 2, (from[1] + to[1]) / 2 - sag, (from[2] + to[2]) / 2];
  for (const [a, b] of [
    [from, low],
    [low, to],
  ] as const) {
    const [dx, dy, dz] = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const length = Math.hypot(dx, dy, dz);
    const place = { at: a, pitch: Math.acos(dy / length), yaw: Math.atan2(dx, dz) };
    hull.cylinder(0.45, length, 3, SWAMP.vine, place);
  }
  hull.box([2.2, 0.3, 1.4], SWAMP.mossLight, { at: low, yaw: from[0] - to[0] });
}

/** Armour scutes along a ridge: a short row of low pyramids, `size` wide, at `points`. */
export function scutes(hull: SolidBuilder, points: readonly Vec3[], size: number): void {
  for (const at of points) hull.cylinder(size, size * 0.8, 4, H.panel, { at, yaw: QUARTER / 2 }, 0);
}

/** A mossy river stone set into a hull: a squat, faceted lump. */
export function stone(hull: SolidBuilder, at: Vec3, size: number, turn = 0): void {
  hull.cylinder(size, size * 0.55, 5, SWAMP.stone, { at, yaw: turn }, size * 0.6);
  hull.cylinder(size * 0.6, size * 0.15, 5, SWAMP.moss, {
    at: [at[0], at[1] + size * 0.55, at[2]],
    yaw: turn,
  });
}

/**
 * A barrel along +Z ending at the muzzle `tip` (playfield, `bossPoint`), `[radius, length]`:
 * its dark tube, a charge light at its mouth, and the muzzle's mark (of `kind`).
 */
export function barrelTo(
  { hull, charge, muzzle }: EnemyParts,
  tip: Muzzle,
  [radius, length]: readonly [number, number],
  kind = 'gun',
): void {
  const [x, y, z] = bossPoint(...tip);
  const light = radius * 1.2;
  hull.cylinder(radius, length, 6, H.dark, { at: [x, y, z - light - length], pitch: QUARTER });
  charge.cylinder(radius * 0.92, light, 6, WHITE, { at: [x, y, z - light], pitch: QUARTER });
  muzzle([x, y, z], kind);
}
