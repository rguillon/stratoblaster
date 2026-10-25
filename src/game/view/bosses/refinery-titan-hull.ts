import type { LoftStation, Placement, SolidBuilder } from '../../../render/geometry/solids';
import { HULL_SECTION, sideStripe } from '../enemies/enemy-shapes';

// P07-R05: the Refinery Titan's heavy hull, and plates laid on its faces. Model space: logical
// pixels, nose +Z (down the screen), Y up towards the camera.

type Rgb = readonly [number, number, number];

/** The heavy hull (loft stations: z, half width, bottom, top), tail to nose. */
export const TITAN_HULL: readonly LoftStation[] = [
  [-62, 24, -5, 9],
  [-50, 29, -6, 12],
  [-34, 34, -7, 15],
  [-8, 36, -8, 16],
  [12, 34, -7.5, 15],
  [32, 29, -6.5, 13],
  [50, 20, -5, 9],
  [62, 11, -4, 6],
  [68, 5, -3, 3.5],
];

/** A station of no size, for an empty list. */
const FLAT: LoftStation = [0, 0, 0, 0];

/** The loft station of `stations` at `z`, interpolated between its neighbours. */
export function stationAt(stations: readonly LoftStation[], z: number): LoftStation {
  const found = stations.findIndex(([sz]) => sz >= z);
  const next = Math.max(1, found < 0 ? stations.length - 1 : found);
  const a = stations[next - 1] ?? FLAT;
  const b = stations[next] ?? a;
  if (b[0] === a[0]) return [z, a[1], a[2], a[3]];
  const t = (z - a[0]) / (b[0] - a[0]);
  const mix = (p: number, q: number): number => p + (q - p) * t;
  return [z, mix(a[1], b[1]), mix(a[2], b[2]), mix(a[3], b[3])];
}

/** The stations of `stations` from `z0` to `z1`, both ends interpolated. */
export function cutStations(
  stations: readonly LoftStation[],
  [z0, z1]: readonly [number, number],
): LoftStation[] {
  const inside = stations.filter(([z]) => z > z0 && z < z1);
  return [stationAt(stations, z0), ...inside, stationAt(stations, z1)];
}

/**
 * A plate laid on side `side` of the hull's section (1: upper +X flank, 2: back, 3: upper -X
 * flank), from `t0` to `t1` across that side and from `z0` to `z1` along the hull, `lift` off it.
 */
export function hullPlate(
  builder: SolidBuilder,
  side: number,
  across: readonly [number, number],
  along: readonly [number, number],
  color: Rgb,
  lift = 1.03,
): void {
  // The back is flat: a plate on it is lifted up, the flanks' plates outwards.
  const place: Placement = side === 2 ? { at: [0, 0.08, 0] } : {};
  const section = sideStripe(HULL_SECTION, side, across, side === 2 ? 1 : lift);
  builder.loft(section, cutStations(TITAN_HULL, along), color, place, { open: true });
}
