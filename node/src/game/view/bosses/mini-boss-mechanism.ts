import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { H, SHADE } from './mini-boss-shapes';

// P07-R05 (phase 7 review: fat armour over a complex mechanism): the machinery seen through the
// gaps between the World 1 mini bosses' armour plates. Logical pixels, nose +Z, Y up. Darker
// than the armour, and set a little lower, so it reads in the gaps under the ~35° camera.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Gear metal: darker than the hull's panels, lighter than its shadows. */
export const GEAR: Rgb = [0.07, 0.07, 0.085];

/** A cog lying flat at `at`: a toothed disc `radius` wide with `teeth` teeth, and its hub. */
export function cog(hull: SolidBuilder, at: Vec3, radius: number, teeth: number, yaw = 0): void {
  const outline = Array.from({ length: teeth * 2 }, (_, k): OutlinePoint => {
    const a = (Math.PI * k) / teeth;
    const r = k % 2 === 0 ? radius : radius * 0.78;
    return [Math.sin(a) * r, Math.cos(a) * r];
  });
  hull.slab(outline, [0, radius * 0.3], GEAR, { at, yaw }, H.panel);
  hull.cylinder(radius * 0.32, radius * 0.5, 6, SHADE.edge, { at });
}

/** The pitch and yaw that turn a solid's +Y axis along `from` → `to`, and the distance. */
function aim([ax, ay, az]: Vec3, [bx, by, bz]: Vec3) {
  const [dx, dy, dz] = [bx - ax, by - ay, bz - az];
  const length = Math.hypot(dx, dy, dz);
  return { length, pitch: Math.acos(dy / length), yaw: Math.atan2(dx, dz) };
}

/** A hydraulic ram from `from` to `to`: a fat dark cylinder, then its bright piston rod. */
export function ram(hull: SolidBuilder, from: Vec3, to: Vec3, radius: number): void {
  const { length, pitch, yaw } = aim(from, to);
  hull.cylinder(radius, length * 0.55, 6, GEAR, { at: from, pitch, yaw });
  hull.cylinder(radius * 0.45, length, 4, SHADE.edge, { at: from, pitch, yaw });
  hull.cylinder(radius * 1.2, radius * 1.2, 6, H.dark, { at: to, pitch, yaw });
}

/** A ribbed conduit from `from` to `to`: a pipe with `ribs` collars along it. */
export function conduit(
  hull: SolidBuilder,
  from: Vec3,
  to: Vec3,
  radius: number,
  ribs: number,
): void {
  const { length, pitch, yaw } = aim(from, to);
  hull.cylinder(radius, length, 4, H.dark, { at: from, pitch, yaw });
  for (let i = 1; i <= ribs; i++) {
    const t = i / (ribs + 1);
    const at: Vec3 = [
      from[0] + (to[0] - from[0]) * t,
      from[1] + (to[1] - from[1]) * t,
      from[2] + (to[2] - from[2]) * t,
    ];
    hull.cylinder(radius * 1.5, radius * 0.7, 6, GEAR, { at, pitch, yaw });
  }
}

/** A glowing line deep in a gap, from `from` to `to`: a lit coolant or power conduit. */
export function glowLine(
  neon: SolidBuilder,
  from: Vec3,
  to: Vec3,
  width: number,
  color: Rgb,
): void {
  const { length, pitch, yaw } = aim(from, to);
  neon.cylinder(width / 2, length, 4, color, { at: from, pitch, yaw });
}
