import type { Muzzle } from '../../../../core/entities/muzzle';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { H, QUARTER, WHITE } from '../mini-boss-shapes';

// P08-R10: the World 2 frost on the Avalanche and the Glacier Colossus (2-4), and the barrels
// drawn to their muzzles. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Snow and ice crust on the tops of the hull: pale blue-white. */
export const FROST: Rgb = [0.75, 0.82, 0.9];
/** Old, packed snow, a little greyer. */
export const PACKED: Rgb = [0.58, 0.63, 0.7];
/** Icicles and clear ice: a paler, bluer white. */
export const ICE: Rgb = [0.62, 0.78, 0.92];

/** Icicles hanging from each point, `length` long (each a thin four-sided spike). */
export function icicles(hull: SolidBuilder, points: readonly Vec3[], length: number): void {
  points.forEach((at, i) => {
    // Every other one shorter, so a row does not read as a comb.
    const l = length * (i % 2 === 0 ? 1 : 0.6);
    hull.cylinder(l * 0.18, l, 4, ICE, { at, pitch: Math.PI, yaw: i * 0.7 }, 0);
  });
}

/** A snow cap: `outline` (seen from above) lying `thick` deep on a top surface at height `y`. */
export function snowCap(
  hull: SolidBuilder,
  outline: readonly OutlinePoint[],
  y: number,
  thick: number,
  color: Rgb = FROST,
): void {
  hull.bevelSlab(outline, [y - 0.3, y, y + thick], [0, thick * 0.8], color);
}

/**
 * A gun barrel pointing down the screen (+Z), drawn back from its muzzle `tip` (a design's
 * `Muzzle`): a dark barrel `length` long, a charge light at its mouth, and the muzzle's marker
 * (phase 7 review, D-057), firing `kind`.
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
