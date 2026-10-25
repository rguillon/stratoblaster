import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { flipX } from '../enemies/enemy-shapes';

// P07-R05: shapes shared by the World 1 final bosses (Storm Petrel, Gull Mothership, Mesa
// Fortress). Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** `at` moved by `[dx, dy, dz]`. */
export function shift(
  at: readonly number[],
  [dx, dy, dz]: readonly [number, number, number],
): Vec3 {
  return [(at[0] ?? 0) + dx, (at[1] ?? 0) + dy, (at[2] ?? 0) + dz];
}

/**
 * A whole symmetric outline from its right half (+X), which runs from a point on the axis at the
 * front to a point on the axis at the back: the left half is its mirror image.
 */
export function mirrored(right: readonly OutlinePoint[]): OutlinePoint[] {
  return [...right, ...flipX(right).reverse().slice(1, -1)];
}

/** The outline mirrored left to right when `side` is -1, as it is when `side` is 1. */
export function sided(outline: readonly OutlinePoint[], side: number): readonly OutlinePoint[] {
  return side > 0 ? outline : flipX(outline);
}

/**
 * A light strip `width` wide from `a` to `b` (seen from above), between heights `y0` and `y1`:
 * neon along a wing's edge or a slit in an armour plate.
 */
export function strip(
  builder: SolidBuilder,
  [ax, az]: OutlinePoint,
  [bx, bz]: OutlinePoint,
  width: number,
  heights: readonly [number, number],
  color: Rgb,
): void {
  const length = Math.hypot(bx - ax, bz - az) || 1;
  const [nx, nz] = [((az - bz) / length) * (width / 2), ((bx - ax) / length) * (width / 2)];
  const outline: OutlinePoint[] = [
    [ax + nx, az + nz],
    [bx + nx, bz + nz],
    [bx - nx, bz - nz],
    [ax - nx, az - nz],
  ];
  builder.slab(outline, heights, color);
}

/** Strips along the edges of a polyline `points` (open: the last point does not join the first). */
export function edgeStrips(
  builder: SolidBuilder,
  points: readonly OutlinePoint[],
  width: number,
  heights: readonly [number, number],
  color: Rgb,
): void {
  points.slice(1).forEach((b, i) => {
    const a = points[i];
    if (a) strip(builder, a, b, width, heights, color);
  });
}

/**
 * Gun barrels pointing forward (+Z) from `at`, `gap` apart, `length` long, with a charge light
 * at each muzzle (it brightens as the next shot charges).
 */
export function barrels(
  { hull, charge }: EnemyParts,
  at: Vec3,
  [count, gap]: readonly [number, number],
  [radius, length]: readonly [number, number],
): void {
  for (let i = 0; i < count; i++) {
    const x = (i - (count - 1) / 2) * gap;
    const place = { at: shift(at, [x, 0, 0]), pitch: QUARTER };
    hull.cylinder(radius, length, 6, H.dark, place, radius * 0.8);
    charge.cylinder(radius * 0.9, radius * 1.4, 6, WHITE, {
      at: shift(at, [x, 0, length]),
      pitch: QUARTER,
    });
  }
}

/** A turret's armoured base and dome (a lathe profile, around its centre). */
const TURRET_DOME = [
  [1, 0],
  [1, 0.35],
  [0.78, 0.75],
  [0.4, 1],
  [0, 1.05],
] as const;

/**
 * A gun turret `radius` wide on its base at `at`: a faceted dome, a neon ring around its base,
 * and `count` barrels pointing forward from its front.
 */
export function turret(
  p: EnemyParts,
  at: Vec3,
  radius: number,
  [count, neon]: readonly [number, Rgb],
): void {
  const height = radius * 0.55;
  const dome = TURRET_DOME.map(([r, y]) => [r * radius, y * height] as const);
  p.hull.lathe(dome, 8, H.panel, { at });
  p.neon.ring(radius * 1.02, radius * 0.1, 8, neon, { at: shift(at, [0, height * 0.2, 0]) });
  p.hull.box([radius * 0.5, radius * 0.08, radius * 0.4], H.dark, {
    at: shift(at, [0, height * 1.02, -radius * 0.2]),
  });
  const gun = shift(at, [0, height * 0.5, radius * 0.6]);
  barrels(p, gun, [count, radius * 0.38], [radius * 0.13, radius * 0.9]);
}

/**
 * Missile tips standing in a launcher at `at`, `rows` × `cols` of them `pitch` apart, pointing up
 * (towards the camera) out of their tubes; the tips light up as a salvo charges.
 */
export function missileTips(
  { hull, charge }: EnemyParts,
  at: Vec3,
  [rows, cols]: readonly [number, number],
  [spacing, radius]: readonly [number, number],
): void {
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = (c - (cols - 1) / 2) * spacing;
      const z = (r - (rows - 1) / 2) * spacing;
      const tube = shift(at, [x, 0, z]);
      hull.ring(radius * 1.3, radius * 0.9, 6, H.dark, { at: tube });
      charge.cylinder(radius, radius * 2.2, 6, WHITE, { at: shift(tube, [0, radius * 0.4, 0]) }, 0);
    }
  }
}

/**
 * An open hatch at `at` in a deck: a dark well `[w, d]` big, its two doors swung up on either
 * side (along Z), and a glowing floor that brightens as the next launch charges.
 */
export function openHatch(
  { hull, charge }: EnemyParts,
  at: Vec3,
  [w, d]: readonly [number, number],
): void {
  hull.box([w, 0.3, d], H.dark, { at });
  charge.box([w * 0.7, 0.3, d * 0.8], WHITE, { at: shift(at, [0, 0.12, 0]) });
  for (const s of [-1, 1]) {
    // A door hinged on the well's side, leaning outwards.
    const door = [
      [0, -d / 2],
      [w * 0.42, -d / 2],
      [w * 0.42, d / 2],
      [0, d / 2],
    ] as const;
    hull.slab(door, [-0.4, 0.4], H.panel, {
      at: shift(at, [(s * w) / 2, 0.3, 0]),
      roll: 1,
      yaw: s > 0 ? 0 : Math.PI,
    });
  }
}
