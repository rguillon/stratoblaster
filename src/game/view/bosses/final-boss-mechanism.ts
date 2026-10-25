import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../render/geometry/solids';
import { rod } from './final-boss-greebles';

// P07-R05 (phase 7 review: fat armour over a complex mechanism): chunky armour plates and the
// machinery seen through the gaps between them: cogs, rams, cable bundles, ribbed conduits.
// Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The mechanism's shades: darker than the hull, so the gaps read as deep. */
export const MECH = {
  deep: [0.03, 0.03, 0.036] as Rgb,
  metal: [0.085, 0.085, 0.1] as Rgb,
  bright: [0.3, 0.29, 0.33] as Rgb,
} as const;

/**
 * A fat armour plate: the outline as straight walls from `y0` up to just under `y1`, then a
 * `chamfer` wide bevel to its top, so its thickness shows at its edges.
 */
export function armour(
  builder: SolidBuilder,
  outline: readonly OutlinePoint[],
  [y0, y1]: readonly [number, number],
  color: Rgb,
  chamfer = 1.4,
  top: Rgb = color,
): void {
  const waist = Math.max(y0, y1 - chamfer * 0.8);
  builder.bevelSlab(outline, [y0, waist, y1], [0, chamfer], color, {}, top);
}

/**
 * A cog lying flat at `at`: a toothed disc `radius` wide (`teeth` teeth), `thick` thick,
 * turned `yaw`; a lighter hub on it.
 */
export function cog(
  builder: SolidBuilder,
  at: Vec3,
  [radius, thick]: readonly [number, number],
  teeth: number,
  place: Placement = {},
): void {
  const points = teeth * 4;
  const outline = Array.from({ length: points }, (_, k): OutlinePoint => {
    const a = (2 * Math.PI * k) / points;
    const r = k % 4 < 2 ? radius : radius * 0.8;
    return [Math.sin(a) * r, Math.cos(a) * r];
  });
  builder.slab(outline, [0, thick], MECH.metal, { ...place, at }, MECH.bright);
  builder.cylinder(radius * 0.35, thick + 0.4, 6, MECH.bright, { ...place, at });
}

/** A hydraulic ram from `from` to `to`: a fat dark cylinder, then its bright rod. */
export function ram(builder: SolidBuilder, from: Vec3, to: Vec3, radius: number): void {
  const mid: Vec3 = [
    from[0] + (to[0] - from[0]) * 0.55,
    from[1] + (to[1] - from[1]) * 0.55,
    from[2] + (to[2] - from[2]) * 0.55,
  ];
  rod(builder, from, mid, radius, MECH.metal);
  rod(builder, mid, to, radius * 0.55, MECH.bright);
  builder.box([radius * 2.6, radius * 2, radius * 2.6], MECH.deep, { at: from });
}

/** `count` cables side by side (across X, `gap` apart) from `from` to `to`: a cable bundle. */
export function cables(
  builder: SolidBuilder,
  from: Vec3,
  to: Vec3,
  [count, gap, radius]: readonly [number, number, number],
): void {
  for (let i = 0; i < count; i++) {
    const dx = (i - (count - 1) / 2) * gap;
    const color = i % 2 === 0 ? MECH.metal : MECH.deep;
    rod(builder, [from[0] + dx, from[1], from[2]], [to[0] + dx, to[1], to[2]], radius, color);
  }
}

/** A ribbed conduit from `from` to `to`: a pipe with `ribs` collars along it. */
export function conduit(
  builder: SolidBuilder,
  from: Vec3,
  to: Vec3,
  [radius, ribs]: readonly [number, number],
): void {
  rod(builder, from, to, radius, MECH.metal);
  for (let k = 1; k <= ribs; k++) {
    const t = k / (ribs + 1);
    const at: Vec3 = [
      from[0] + (to[0] - from[0]) * t,
      from[1] + (to[1] - from[1]) * t,
      from[2] + (to[2] - from[2]) * t,
    ];
    const step = 0.25 / Math.hypot(to[0] - from[0], to[1] - from[1], to[2] - from[2]);
    const end: Vec3 = [
      at[0] + (to[0] - from[0]) * step * 2,
      at[1] + (to[1] - from[1]) * step * 2,
      at[2] + (to[2] - from[2]) * step * 2,
    ];
    rod(builder, at, end, radius * 1.45, MECH.bright);
  }
}

/** A glowing line deep in a gap from `a` to `b` at height `y`: a lit conduit (neon or charge). */
export function glowLine(
  builder: SolidBuilder,
  [a, b]: readonly [OutlinePoint, OutlinePoint],
  y: number,
  color: Rgb,
): void {
  const [dx, dz] = [b[0] - a[0], b[1] - a[1]];
  const length = Math.hypot(dx, dz) || 1;
  const [nx, nz] = [(-dz / length) * 0.4, (dx / length) * 0.4];
  builder.slab(
    [
      [a[0] + nx, a[1] + nz],
      [b[0] + nx, b[1] + nz],
      [b[0] - nx, b[1] - nz],
      [a[0] - nx, a[1] - nz],
    ],
    [y, y + 0.5],
    color,
  );
}

/** A dark recess floor `outline` at height `y`: the bottom of a gap the mechanism sits in. */
export function well(builder: SolidBuilder, outline: readonly OutlinePoint[], y: number): void {
  builder.slab(outline, [y - 0.4, y], MECH.deep);
}
