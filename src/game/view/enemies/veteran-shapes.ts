import type { OutlinePoint } from '../../../render/geometry/outline';
import type { LoftStation, SectionPoint, SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from './enemy-mesh';

// Shapes shared by the veteran models (P05-R14 to P05-R18). Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = readonly [number, number, number];

const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/**
 * A gun barrel from `at` towards the nose, `length` long and `radius` thick, a charge light at
 * its mouth, its muzzle marked just past it (phase 7 review: shots leave from the barrels the
 * player sees).
 */
export function noseGun(
  { hull, charge, muzzle }: EnemyParts,
  at: Vec3,
  length: number,
  radius = 0.55,
): void {
  const [x, y, z] = at;
  hull.cylinder(radius, length, 6, ENEMY_LOOK.hull.dark, { at: [x, y, z], pitch: QUARTER }, radius);
  charge.cylinder(radius * 1.1, 0.8, 6, WHITE, { at: [x, y, z + length], pitch: QUARTER });
  muzzle([x, y, z + length + 0.8]);
}

/** The station of a loft (tail to nose) at `z`, between its two nearest ones. */
export function stationAt(stations: readonly LoftStation[], z: number): LoftStation {
  const after = stations.findIndex((s) => s[0] >= z);
  const b = stations[Math.max(0, after)] ?? stations[0];
  const a = stations[Math.max(0, after - 1)] ?? b;
  if (!a || !b) throw new Error('A loft needs stations');
  const t = b[0] === a[0] ? 0 : (z - a[0]) / (b[0] - a[0]);
  const mix = (i: 1 | 2 | 3): number => a[i] + (b[i] - a[i]) * t;
  return [z, mix(1), mix(2), mix(3)];
}

/** The upper half of a round section (open), from one side over the back to the other. */
const BAND_SECTION: readonly SectionPoint[] = [
  [1, 0.45],
  [0.5, 1],
  [-0.5, 1],
  [-1, 0.45],
];

/**
 * A neon band painted over the back of a loft (`stations`, a {@link POD_SECTION}-like body)
 * from `z0` to `z1`, standing `lift` off it: a stripe across a wasp's abdomen.
 */
export function backBand(
  builder: SolidBuilder,
  stations: readonly LoftStation[],
  [z0, z1]: readonly [number, number],
  color: Rgb,
  lift = 0.12,
): void {
  const raise = ([z, w, bottom, top]: LoftStation): LoftStation => [
    z,
    w + lift,
    bottom,
    top + lift,
  ];
  builder.loft(
    BAND_SECTION,
    [raise(stationAt(stations, z0)), raise(stationAt(stations, z1))],
    color,
    {},
    { open: true },
  );
}

/**
 * A strip `width` wide just outside the edge from `a` to `b` of an outline around the origin:
 * a neon edge light, e.g. along a flying wing's leading edge.
 */
export function edgeStrip(a: OutlinePoint, b: OutlinePoint, width: number): OutlinePoint[] {
  const [dx, dz] = [b[0] - a[0], b[1] - a[1]];
  const d = Math.hypot(dx, dz);
  let [nx, nz] = [dz / d, -dx / d];
  // Away from the centre.
  if (nx * (a[0] + b[0]) + nz * (a[1] + b[1]) < 0) [nx, nz] = [-nx, -nz];
  return [a, b, [b[0] + nx * width, b[1] + nz * width], [a[0] + nx * width, a[1] + nz * width]];
}
