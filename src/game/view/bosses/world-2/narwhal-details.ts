import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { lamps, mast, plate, rect, seam } from '../mini-boss-greebles';
import { FROST } from './floe-breaker-frost';

// P08-R10, 2-1: the Narwhal's hull dressing (phase 7 review: detail and some asymmetry, World 2
// frost). Logical pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;
/** Light metal: worn edges, rails. */
const EDGE = [0.24, 0.24, 0.27] as const;
/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED = [1, 0.1, 0.12] as const;
const STARBOARD_GREEN = [0.2, 1, 0.35] as const;

type Rgb = readonly [number, number, number];

/** The hull's half width at `z` (between its stations), for the dressing along its flanks. */
function flank(z: number): number {
  return z < -40 ? 14 + (z + 40) * 0.3 : z > 30 ? 16.5 - (z - 30) * 0.3 : 17.5;
}

/**
 * Along both flanks: rows of dark free-flood slots, the hull's ring seams, its bow planes; on its
 * belly a sonar window lit teal.
 */
export function hullDressing({ hull, neon }: EnemyParts, n: Rgb): void {
  for (const s of SIDES) {
    for (let z = -44; z <= 34; z += 8) {
      if (z > -6 && z < 14) continue;
      hull.box([0.6, 1.4, 3.6], H.dark, { at: [s * (flank(z) + 0.1), 1.6, z] });
    }
    const bowPlane = [
      [s * 11, 44],
      [s * 19, 40],
      [s * 19, 36],
      [s * 11, 36],
    ] as const;
    hull.bevelSlab(bowPlane, [4.5, 5.5, 6.5], [0.3, 0.6], H.base, {}, FROST.panel);
  }
  // Ring seams across its back.
  for (const [z, top] of [
    [-40, 15],
    [-24, 16.4],
    [32, 16.2],
  ] as const) {
    seam(hull, [-6.5, z], [6.5, z], [top, 0.6, 0.6], H.dark);
  }
  neon.box([5, 0.5, 6], n, { at: [0, -5.6, 40] });
}

/**
 * On its back: a frozen crust on the forward deck, a railing, a capstan, an escape hatch,
 * whip antennas off-centre, navigation lamps on the sail.
 */
export function deckDressing(p: EnemyParts, n: Rgb): void {
  const { hull, neon } = p;
  const crust = [
    [-4, 33],
    [3, 34],
    [5, 41],
    [1, 45],
    [-4, 42],
  ] as const;
  hull.slab(crust, [12.5, 16.4], FROST.ice, {}, FROST.snow);
  for (const s of SIDES) seam(hull, [s * 5.5, -36], [s * 5.5, -12], [16.4, 0.5, 0.9], EDGE);
  hull.cylinder(1.6, 2.2, 8, EDGE, { at: [-3, 15.6, -33] });
  hull.cylinder(2.2, 0.6, 8, H.dark, { at: [-3, 17.8, -33] });
  plate(hull, rect(4, 4), [17.4, 0.5], H.panel, { at: [-3, 0, -13] });
  mast(p, [-3, 27, -1], 5, n);
  mast(p, [2.5, 15, -40], 4, n);
  lamps(neon, [[5.2, 20, 8]], 1.2, PORT_RED);
  lamps(neon, [[-5.2, 20, 8]], 1.2, STARBOARD_GREEN);
  // The sail's front windows, lit teal.
  neon.box([4, 0.9, 0.4], n, { at: [0, 21.6, 22.1] });
}
