import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { H, SHADE } from './mini-boss-shapes';

// P07-R05 (phase 7 review: more detail, some asymmetry): surface details of the World 1 mini
// bosses. Logical pixels, nose +Z, Y up. Details are flat-shaded hull pieces a little proud of
// the surface, so they read from above under the ~35° camera.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];
/** A point seen from above: `[x, z]`. */
type Flat = readonly [number, number];

/** A rectangle `w` wide (X) and `d` deep (Z) around the origin. */
export function rect(w: number, d: number): OutlinePoint[] {
  return [
    [-w / 2, -d / 2],
    [w / 2, -d / 2],
    [w / 2, d / 2],
    [-w / 2, d / 2],
  ];
}

/** A plate: `outline` raised `thick` above the surface at height `y`, its top edge chamfered. */
export function plate(
  hull: SolidBuilder,
  outline: readonly OutlinePoint[],
  [y, thick]: readonly [number, number],
  color: Rgb,
  place: Placement = {},
): void {
  hull.bevelSlab(outline, [y - 0.4, y, y + thick], [0, Math.min(thick, 0.7)], color, place);
}

/** A thin raised strip on the surface at height `y`, from `a` to `b`: a seam, a cable, a rail. */
export function seam(
  hull: SolidBuilder,
  [ax, az]: Flat,
  [bx, bz]: Flat,
  [y, width, height]: readonly [number, number, number],
  color: Rgb = H.dark,
): void {
  const [dx, dz] = [bx - ax, bz - az];
  hull.box([width, height, Math.hypot(dx, dz)], color, {
    at: [(ax + bx) / 2, y, (az + bz) / 2],
    yaw: Math.atan2(dx, dz),
  });
}

/** Strips along a path of points at height `y`, `width` wide: a cable run, a pipe. */
export function cable(
  hull: SolidBuilder,
  path: readonly Flat[],
  y: number,
  width: number,
  color: Rgb = H.dark,
): void {
  path.slice(1).forEach((b, i) => {
    const a = path[i];
    if (a) seam(hull, a, b, [y, width, width * 0.8], color);
  });
}

/** A vent at `at` (its top surface), `w` by `d`, turned by `yaw`: a dark recess, `slats` slats. */
export function vent(
  hull: SolidBuilder,
  at: Vec3,
  [w, d]: readonly [number, number],
  slats: number,
  yaw = 0,
): void {
  hull.box([w, 0.3, d], H.dark, { at, yaw });
  const pitch = d / slats;
  for (let i = 0; i < slats; i++) {
    const along = (i + 0.5) * pitch - d / 2;
    const [sx, sz] = [Math.sin(yaw) * along, Math.cos(yaw) * along];
    hull.box([w * 0.86, 0.7, pitch * 0.4], H.panel, {
      at: [at[0] + sx, at[1], at[2] + sz],
      yaw,
    });
  }
}

/** Hazard stripes on a `w` by `d` patch at `at`: `count` bands across, paint and dark metal. */
export function hazard(
  hull: SolidBuilder,
  at: Vec3,
  [w, d]: readonly [number, number],
  count: number,
  yaw = 0,
): void {
  const band = w / count;
  for (let i = 0; i < count; i++) {
    const across = (i + 0.5) * band - w / 2;
    const [sx, sz] = [Math.cos(yaw) * across, -Math.sin(yaw) * across];
    const color = i % 2 === 0 ? SHADE.hazard : H.dark;
    hull.box([band, 0.4, d], color, { at: [at[0] + sx, at[1], at[2] + sz], yaw });
  }
}

/** An antenna mast standing at `at`, `height` tall, a light of `color` on its tip. */
export function mast(
  { hull, neon }: { readonly hull: SolidBuilder; readonly neon: SolidBuilder },
  at: Vec3,
  height: number,
  color: Rgb,
): void {
  hull.cylinder(0.9, 1.2, 6, H.panel, { at });
  hull.cylinder(0.45, height, 4, H.dark, { at }, 0.3);
  hull.box([3.2, 0.5, 0.5], H.panel, { at: [at[0], at[1] + height * 0.65, at[2]] });
  neon.box([0.9, 0.9, 0.9], color, { at: [at[0], at[1] + height, at[2]] });
}

/** A radar dish at `at`, `radius` wide, tipped back by `tilt` and turned by `yaw`. */
export function dish(hull: SolidBuilder, at: Vec3, radius: number, tilt: number, yaw = 0): void {
  hull.cylinder(0.8, 2, 4, H.dark, { at });
  const bowl = [
    [0.3, 0],
    [radius, radius * 0.35],
    [radius * 0.8, radius * 0.45],
    [0, radius * 0.2],
  ] as const;
  hull.lathe(bowl, 8, SHADE.edge, { at: [at[0], at[1] + 2, at[2]], pitch: tilt, yaw });
}

/** Small lights of `color` at each point, `size` across. */
export function lamps(neon: SolidBuilder, points: readonly Vec3[], size: number, color: Rgb): void {
  for (const at of points) neon.box([size, size * 0.6, size], color, { at });
}
