import type { Muzzle } from '../../../../core/entities/muzzle';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';
import { edgeStrips } from '../final-boss-shapes';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';

// P10-R11, 4-1: the heavy industry on the Black sands' bosses (the Cinder Crab and the Steam
// Dreadnought): soot, molten seams glowing between the plates, steam, struts and barrels (GD-61,
// World 4: dark metal with neon, plus soot, heat glow and molten seams). Logical pixels, nose +Z,
// Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Volcanic shades: molten metal in the seams, soot, ash dust, steam lit by the furnaces. */
export const FORGE = {
  molten: [1, 0.3, 0.02] as Rgb,
  ember: [0.75, 0.12, 0.01] as Rgb,
  soot: SHADE.soot,
  ash: [0.2, 0.19, 0.18] as Rgb,
  steam: [0.2, 0.19, 0.19] as Rgb,
};

/**
 * A cylinder from `a` to `b` (radius `r` at `a`, `rb` at `b`, `sides` facets): a strut, a leg,
 * a barrel. Pitched off +Y, then yawed, so that its axis runs along `b - a`.
 */
export function strut(
  builder: SolidBuilder,
  [a, b]: readonly [Vec3, Vec3],
  [r, rb]: readonly [number, number],
  color: Rgb,
  sides = 6,
): void {
  const [dx, dy, dz] = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const length = Math.hypot(dx, dy, dz);
  const pitch = Math.atan2(Math.hypot(dx, dz), dy);
  builder.cylinder(r, length, sides, color, { at: a, pitch, yaw: Math.atan2(dx, dz) }, rb);
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
  hull.ring(radius * 1.25, length * 0.18, 6, H.panel, {
    at: [x, y, z - light - length * 0.35],
    pitch: QUARTER,
  });
  charge.cylinder(radius * 0.92, light, 6, WHITE, { at: [x, y, z - light], pitch: QUARTER });
  muzzle([x, y, z], kind);
}

/** A molten seam along `points` (seen from above) at height `y`: a thin glowing line. */
export function moltenSeam(
  neon: SolidBuilder,
  points: readonly OutlinePoint[],
  y: number,
  width = 0.7,
): void {
  edgeStrips(neon, points, width, [y - 0.15, y + 0.12], FORGE.molten);
}

/** A soot stain over `outline` lying on a hull at height `y`. */
export function soot(hull: SolidBuilder, outline: readonly OutlinePoint[], y: number): void {
  decal(hull, outline, y + 0.04, FORGE.soot);
}

/** A rough, roundish outline `radius` wide around `[x, z]`, stretched `stretch` times along Z. */
export function blot([x, z]: OutlinePoint, radius: number, stretch = 1, seed = 0): OutlinePoint[] {
  return Array.from({ length: 6 }, (_, k): OutlinePoint => {
    const a = (k * Math.PI) / 3 + seed;
    const r = radius * (0.75 + 0.25 * Math.sin(seed * 2.7 + k * 1.9));
    return [x + Math.cos(a) * r, z + Math.sin(a) * r * stretch];
  });
}

/**
 * Puffs of steam trailing back (towards -Z) and rising from `from`: low-poly lumps growing as
 * they go, faintly lit by the furnaces below (drawn as lights, so the hull's tint leaves them).
 */
export function steam(neon: SolidBuilder, from: Vec3, count: number, size: number): void {
  for (let i = 0; i < count; i++) {
    const r = size * (1 + 0.45 * i);
    const at: Vec3 = [from[0] + (i % 2 ? 0.8 : -0.6), from[1] + 1.6 * i, from[2] - 4.5 * i];
    neon.lathe(
      [
        [r * 0.55, 0],
        [r, r * 0.45],
        [r * 0.7, r * 0.95],
        [0, r * 1.1],
      ],
      5,
      FORGE.steam,
      { at, yaw: i * 0.7 },
    );
  }
}

/** Rivets or bolt heads along a row of `points` at height `y`, `size` wide. */
export function bolts(
  hull: SolidBuilder,
  points: readonly OutlinePoint[],
  y: number,
  size: number,
) {
  for (const [x, z] of points) hull.box([size, size * 0.5, size], SHADE.edge, { at: [x, y, z] });
}
