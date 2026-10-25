import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../../render/geometry/solids';

// P08-R10: the World 2 frost on the Fjord Lynx and the Harbour Kraken: snow caps, ice crust and
// icicles over the dark metal (GD-61). Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

/** Packed snow on top faces: pale blue-white. */
export const SNOW: Rgb = [0.78, 0.84, 0.92];
/** Ice crust and icicles: a colder, darker blue. */
export const ICE: Rgb = [0.55, 0.68, 0.82];
/** A frosted panel: metal under a thin rime. */
export const RIME: Rgb = [0.36, 0.4, 0.47];

/** A snow cap: `outline` a little proud of the surface at height `y`, rounded at its edges. */
export function snowCap(
  hull: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  place: Placement = {},
): void {
  hull.bevelSlab(outline, [y - 0.3, y, y + 0.7], [0, 0.5], SNOW, place);
}

/** Icicles hanging under the points given, `length` long at most (they vary a little). */
export function icicles(hull: SolidBuilder, points: readonly Vec3[], length: number): void {
  points.forEach((at, i) => {
    const k = 0.6 + 0.4 * (((i * 7) % 5) / 4);
    hull.cylinder(0.7, length * k, 3, ICE, { at, pitch: Math.PI, yaw: i }, 0);
  });
}

/** `count` points evenly spread from `a` to `b` (ends included). */
export function spread(a: Vec3, b: Vec3, count: number): Vec3[] {
  return Array.from({ length: count }, (_, i): Vec3 => {
    const t = count > 1 ? i / (count - 1) : 0.5;
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  });
}
