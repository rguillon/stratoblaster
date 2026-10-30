import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal } from '../enemies/enemy-shapes';

// P07-R05 (phase 7 review: more detail): small surface details shared by the World 1 final
// bosses: plates, vents, rivets, hazard stripes, masts and lights. Logical pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;

type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** `color` scaled by `k` (darker below 1, lighter above). */
export function tone([r, g, b]: Rgb, k: number): Rgb {
  return [r * k, g * k, b * k];
}

/** The hull shades used for details, from the darkest to the palest. */
export const SHADE = {
  dark: H.dark,
  base: H.base,
  mid: tone(H.base, 1.3),
  panel: H.panel,
  light: tone(H.panel, 1.35),
  pale: tone(H.panel, 1.9),
  scorch: [0.05, 0.04, 0.035] as Rgb,
} as const;

/** A rectangle `[w, d]` big around `[cx, cz]`, turned `yaw` radians (seen from above). */
export function rect(
  [cx, cz]: OutlinePoint,
  [w, d]: readonly [number, number],
  yaw = 0,
): OutlinePoint[] {
  const [c, s] = [Math.cos(yaw), Math.sin(yaw)];
  const corner = (u: number, v: number): OutlinePoint => [cx + u * c + v * s, cz - u * s + v * c];
  return [
    corner(-w / 2, -d / 2),
    corner(w / 2, -d / 2),
    corner(w / 2, d / 2),
    corner(-w / 2, d / 2),
  ];
}

/**
 * An armour plate a little proud of a flat surface at height `y`: the outline, `thick` thick,
 * its top edges chamfered.
 */
export function plate(
  builder: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  color: Rgb,
  thick = 0.5,
  place: Placement = {},
): void {
  builder.bevelSlab(outline, [y - 0.2, y - 0.2, y + thick], [0, thick * 0.7], color, place);
}

/** Flat decals at height `y`: one outline each, all of `color` (2 triangles a quad). */
export function decals(
  builder: SolidBuilder,
  outlines: readonly (readonly OutlinePoint[])[],
  y: number,
  color: Rgb,
): void {
  for (const outline of outlines) decal(builder, outline, y, color);
}

/**
 * A vent grille at height `y`: a dark frame `[w, d]` around `[cx, cz]` and `count` slats across
 * it (along X), turned `yaw`.
 */
export function grille(
  builder: SolidBuilder,
  at: OutlinePoint,
  [w, d]: readonly [number, number],
  [count, y]: readonly [number, number],
  yaw = 0,
): void {
  decal(builder, rect(at, [w, d], yaw), y, SHADE.dark);
  const step = d / count;
  const [c, s] = [Math.cos(yaw), Math.sin(yaw)];
  for (let i = 0; i < count; i++) {
    const v = -d / 2 + step * (i + 0.5);
    const centre: OutlinePoint = [at[0] + v * s, at[1] + v * c];
    decal(builder, rect(centre, [w * 0.8, step * 0.4], yaw), y + 0.04, SHADE.light);
  }
}

/** `count` points evenly spread from `a` to `b`, both ends included. */
export function along(a: OutlinePoint, b: OutlinePoint, count: number): OutlinePoint[] {
  return Array.from({ length: count }, (_, i): OutlinePoint => {
    const t = count > 1 ? i / (count - 1) : 0.5;
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  });
}

/** A row of small square studs from `a` to `b` at height `y`: rivets, or lights on `neon`. */
export function studs(
  builder: SolidBuilder,
  [a, b]: readonly [OutlinePoint, OutlinePoint],
  [count, size]: readonly [number, number],
  y: number,
  color: Rgb,
): void {
  for (const p of along(a, b, count)) decal(builder, rect(p, [size, size], 0.785), y, color);
}

/**
 * Hazard stripes in a band `[w, d]` around `at` (across X) at height `y`: a dark band and `count`
 * slanted pale stripes on it.
 */
export function hazard(
  builder: SolidBuilder,
  at: OutlinePoint,
  [w, d]: readonly [number, number],
  count: number,
  y: number,
): void {
  const [cx, cz] = at;
  decal(builder, rect(at, [w, d]), y, SHADE.dark);
  const step = w / (count + 0.5);
  for (let i = 0; i < count; i++) {
    const x = cx - w / 2 + step * (i + 0.25);
    const stripe: OutlinePoint[] = [
      [x, cz - d * 0.4],
      [x + step * 0.5, cz - d * 0.4],
      [x + step * 0.75, cz + d * 0.4],
      [x + step * 0.25, cz + d * 0.4],
    ];
    decal(builder, stripe, y + 0.04, SHADE.pale);
  }
}

/** A thin rod from `from` to `to`: a mast stay, a cable, a whip antenna. */
export function rod(
  builder: SolidBuilder,
  from: Vec3,
  to: Vec3,
  radius: number,
  color: Rgb = SHADE.dark,
): void {
  const [dx, dy, dz] = [to[0] - from[0], to[1] - from[1], to[2] - from[2]];
  const length = Math.hypot(dx, dy, dz) || 1;
  const pitch = Math.acos(dy / length);
  const yaw = Math.atan2(dx, dz);
  builder.cylinder(radius, length, 4, color, { at: from, pitch, yaw });
}

/** An antenna mast `height` tall standing at `at`, a neon light on its tip. */
export function mast(p: EnemyParts, at: Vec3, height: number, neon: Rgb): void {
  const [x, y, z] = at;
  p.hull.cylinder(0.7, height, 4, SHADE.dark, { at }, 0.3);
  p.hull.box([3, 0.4, 0.5], SHADE.panel, { at: [x, y + height * 0.65, z] });
  p.neon.box([0.9, 0.9, 0.9], neon, { at: [x, y + height, z] });
}

/** A radar dish `radius` wide on a short post at `at`, tilted `tilt` radians towards `yaw`. */
export function dish(p: EnemyParts, at: Vec3, radius: number, [tilt, yaw]: [number, number]): void {
  const [x, y, z] = at;
  p.hull.cylinder(radius * 0.18, radius * 0.7, 4, SHADE.dark, { at });
  const bowl = [
    [radius * 0.2, 0],
    [radius, radius * 0.35],
    [radius * 0.9, radius * 0.42],
    [0, radius * 0.12],
  ] as const;
  const top: Vec3 = [x, y + radius * 0.6, z];
  p.hull.lathe(bowl, 8, SHADE.light, { at: top, pitch: tilt, yaw });
  rod(p.hull, top, [x + Math.sin(yaw) * radius * 0.25, y + radius * 1.1, z], 0.25);
}

/** Small greeble boxes `[dx, dz, w, h, d]` around `at` (its height is their base): pipes, boxes. */
export function greebles(
  builder: SolidBuilder,
  at: Vec3,
  boxes: readonly (readonly [number, number, number, number, number])[],
  color: Rgb = SHADE.panel,
): void {
  const [x, y, z] = at;
  boxes.forEach(([dx, dz, w, h, d], i) => {
    const top = i % 2 === 0 ? SHADE.light : color;
    builder.box([w, h, d], color, { at: [x + dx, y, z + dz] }, top);
  });
}
