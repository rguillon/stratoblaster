import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SectionPoint, SolidBuilder } from '../../../render/geometry/solids';

type Vec3 = [number, number, number];

/** A point `r` from the model's centre in the direction `angle` (radians from +Z towards +X). */
export function radial(angle: number, r: number, y: number): Vec3 {
  return [Math.sin(angle) * r, y, Math.cos(angle) * r];
}

/** `count` angles evenly spread around the circle, the first one on +Z (the nose). */
export function around(count: number): number[] {
  return Array.from({ length: count }, (_, i) => (2 * Math.PI * i) / count);
}

/** The outline moved by `dx` across. */
export function shiftX(outline: readonly OutlinePoint[], dx: number): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [x + dx, z]);
}

/** The outline mirrored left to right (for the other wing). */
export function flipX(outline: readonly OutlinePoint[]): OutlinePoint[] {
  return outline.map(([x, z]): OutlinePoint => [-x, z]);
}

/** Both sides: -1 (left) and 1 (right). */
export const SIDES = [-1, 1] as const;

/**
 * Loft cross-sections (`SolidBuilder.loft`), counter-clockwise seen from the nose. A hull: flat
 * belly and back, its widest point a chine low on the sides.
 */
export const HULL_SECTION: readonly SectionPoint[] = [
  [0.55, 0],
  [1, 0.4],
  [0.6, 1],
  [-0.6, 1],
  [-1, 0.4],
  [-0.55, 0],
];

/**
 * A fighter's fuselage: chines low on the sides, then shoulders and a ridge on its back where a
 * canopy is painted ({@link canopyPaint}) instead of stuck on as another solid.
 */
export const FIGHTER_SECTION: readonly SectionPoint[] = [
  [0.5, 0],
  [1, 0.3],
  [0.6, 0.6],
  [0.3, 0.85],
  [0, 1],
  [-0.3, 0.85],
  [-0.6, 0.6],
  [-1, 0.3],
  [-0.5, 0],
];

/** The sides of {@link FIGHTER_SECTION} on its back, from shoulder to shoulder. */
const CANOPY_SIDES = new Set([2, 3, 4, 5]);

/** Paints the back of a {@link FIGHTER_SECTION} loft `color` between the given stations. */
export function canopyPaint(
  bands: readonly number[],
  color: readonly [number, number, number],
): (side: number, band: number) => readonly [number, number, number] | undefined {
  return (side, band) => (CANOPY_SIDES.has(side) && bands.includes(band) ? color : undefined);
}

/** A round-ish pod or boom: a hexagon. */
export const POD_SECTION: readonly SectionPoint[] = [
  [0.5, 0],
  [1, 0.5],
  [0.5, 1],
  [-0.5, 1],
  [-1, 0.5],
  [-0.5, 0],
];

/** A canopy or dorsal ridge sitting on a hull: open at the bottom (loft it with `open`). */
export const CANOPY_SECTION: readonly SectionPoint[] = [
  [1, 0],
  [0.7, 0.6],
  [0, 1],
  [-0.7, 0.6],
  [-1, 0],
];

/**
 * Two eye slits on either side of `center`, `gap` apart, each `length` long and `width` deep,
 * their outer ends swept back by `slant` radians: a frown seen from above.
 */
export function angryEyes(
  [cx, cz]: OutlinePoint,
  gap: number,
  [length, width]: readonly [number, number],
  slant: number,
): OutlinePoint[][] {
  return SIDES.map((s) => {
    const inner: OutlinePoint = [cx + (s * gap) / 2, cz];
    const outer: OutlinePoint = [
      inner[0] + s * length * Math.cos(slant),
      cz - length * Math.sin(slant),
    ];
    return [inner, outer, [outer[0], outer[1] - width], [inner[0], inner[1] - width]];
  });
}

/** A flat convex outline at height `y`, facing up: a light painted on a hull (2 triangles a quad). */
export function decal(
  builder: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  color: readonly [number, number, number],
): void {
  const area = outline.reduce((sum, [x1, z1], i) => {
    const [x2, z2] = outline[(i + 1) % outline.length] ?? [x1, z1];
    return sum + x1 * z2 - x2 * z1;
  }, 0);
  // Facing up (+Y) takes clockwise corners in (x, z).
  const corners = area > 0 ? [...outline].reverse() : outline;
  builder.face(
    corners.map(([x, z]): Vec3 => [x, y, z]),
    color,
  );
}

/**
 * A two-point section on side `side` of `section`, from `t0` to `t1` of its length, lifted
 * `lift` times off the axis: lofted with `open`, a stripe painted along that side of a hull.
 */
export function sideStripe(
  section: readonly SectionPoint[],
  side: number,
  [t0, t1]: readonly [number, number],
  lift = 1.04,
): SectionPoint[] {
  const [ua, va] = section[side] ?? [0, 0];
  const [ub, vb] = section[(side + 1) % section.length] ?? [0, 0];
  const at = (t: number): SectionPoint => [(ua + (ub - ua) * t) * lift, va + (vb - va) * t];
  return [at(t0), at(t1)];
}

/**
 * P16-R03: a lean rounded section for the basic kinds' swollen bodies (`segmentedBody`): a flat
 * belly, round flanks and a soft back, in seven facets.
 */
export const LOBE_SECTION: readonly SectionPoint[] = [
  [0.4, 0],
  [1, 0.35],
  [0.75, 0.85],
  [0, 1],
  [-0.75, 0.85],
  [-1, 0.35],
  [-0.4, 0],
];
