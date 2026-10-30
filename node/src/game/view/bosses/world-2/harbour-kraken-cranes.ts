import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { CRANE_REST, CRANES } from '../../../config/bosses/world-2/harbour-kraken';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import { barrels } from '../final-boss-shapes';
import { curve, organ, tendril } from '../../../../render/geometry/organic';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { icicles, spread } from './fjord-lynx-frost';
import { ICE_FLESH } from './w2-organic';

// P08-R10, 2-2: the Harbour Kraken's crane arms: a boom on each shoulder, a jib on each elbow
// (moving limbs, D-061), and the grab cannons hanging from the jibs' tips. Logical pixels, nose
// +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Kraken's orange neon. */
export const ORANGE_NEON: Rgb = BOSS_LOOK.neon['harbour-kraken'] ?? [1, 0.5, 0.08];
/** Height of the booms over the deck's level, and of the deck. */
export const BOOM_Y = 12;
export const DECK_Y = 4;
/** Where a grab cannon's barrel starts, from the grab's centre, and its radius and length. */
const GRAB_GUN: Vec3 = [0, 4, 5];
const GRAB_BORE: readonly [number, number] = [1.3, 9];

/** A beam from `a` to `b` (on the same level), `w` wide and `h` high, its top `top`. */
export function beam(
  builder: SolidBuilder,
  a: Vec3,
  b: Vec3,
  [w, h]: readonly [number, number],
  [color, top]: readonly [Rgb, Rgb],
): void {
  const [dx, dz] = [b[0] - a[0], b[2] - a[2]];
  builder.box(
    [w, h, Math.hypot(dx, dz)],
    color,
    {
      at: [(a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2],
      yaw: Math.atan2(dx, dz),
    },
    top,
  );
}

/** The model-space points of a crane at rest: its shoulder, elbow and grab, at `y`. */
function cranePoints(crane: string, y: number): Vec3[] {
  const [end, side] = crane.split('-') as ['fore' | 'aft', 'left' | 'right'];
  const s = side === 'left' ? 1 : -1;
  return CRANE_REST[end].map(([x, py]) => offset(bossPoint(s * x, py), 0, y, 0));
}

/** A crane's boom, on its shoulder: a lattice-dark beam, rimed on top, a neon line along it. */
function boom(crane: string) {
  return (p: EnemyParts): void => {
    const { hull, flesh, neon } = p;
    const [shoulder, elbow] = cranePoints(crane, BOOM_Y) as [Vec3, Vec3];
    // P16-R06: a tentacle's thick upper length, metal bands grafted round it.
    tendril(flesh, curve(shoulder, elbow, [0, 2, 0], 3), [3.4, 2.6], 6, ICE_FLESH.crimson);
    for (const t of [0.35, 0.7]) {
      const at = offset(shoulder, (elbow[0] - shoulder[0]) * t, 1.2, (elbow[2] - shoulder[2]) * t);
      hull.ring(3.3, 1.2, 6, H.panel, {
        at,
        pitch: QUARTER,
        yaw: Math.atan2(elbow[0] - shoulder[0], elbow[2] - shoulder[2]),
      });
    }
    beam(
      neon,
      offset(shoulder, 0, 3, 0),
      offset(elbow, 0, 3, 0),
      [0.8, 0.3],
      [ORANGE_NEON, ORANGE_NEON],
    );
    organ(flesh, 3.4, 6, ICE_FLESH.purple, { at: offset(elbow, 0, -2.6, 0) }, 0.7);
    for (const at of spread(shoulder, elbow, 3))
      organ(flesh, 1.2, 5, ICE_FLESH.bone, { at: offset(at, 0, -3, 0) }, 0.5);
    icicles(flesh, spread(shoulder, elbow, 4), 3);
  };
}

/** A crane's jib, on its elbow: a lighter beam out to the winch its grab hangs from. */
function jib(crane: string) {
  return ({ hull, flesh, neon }: EnemyParts): void => {
    const [, elbow, tip] = cranePoints(crane, BOOM_Y + 0.4) as [Vec3, Vec3, Vec3];
    tendril(flesh, curve(elbow, tip, [0, 1.5, 0], 3), [2.6, 1.6], 5, ICE_FLESH.crimson);
    beam(
      neon,
      offset(elbow, 0, 2.4, 0),
      offset(tip, 0, 2.4, 0),
      [0.7, 0.3],
      [ORANGE_NEON, ORANGE_NEON],
    );
    hull.cylinder(2.2, 4.4, 6, H.panel, { at: offset(tip, 2.2, 0.6, 0), roll: Math.PI / 2 });
    icicles(flesh, spread(elbow, tip, 3), 2.5);
  };
}

/** The limbs of the four cranes: a boom on each shoulder and a jib on each elbow. */
export function craneLimbs(): Record<string, LimbDrawing> {
  const limbs: Record<string, LimbDrawing> = {};
  for (const crane of CRANES) {
    limbs[`shoulder-${crane}`] = { draw: boom(crane) };
    limbs[`elbow-${crane}`] = { draw: jib(crane) };
  }
  return limbs;
}

/** A crane's pedestal on the deck at `at` (its shoulder): a drum, a neon ring, a slewing cog. */
export function pedestal({ hull, flesh, neon }: EnemyParts, at: Vec3): void {
  // P16-R06: the root of a tentacle, a swollen ring of muscle with a metal collar.
  flesh.cylinder(6.5, BOOM_Y - 2 - at[1], 7, ICE_FLESH.purple, { at, yaw: Math.PI / 8 }, 5);
  neon.ring(6.3, 0.8, 8, ORANGE_NEON, { at: offset(at, 0, 2, 0), yaw: Math.PI / 8 });
  hull.cylinder(5, 2, 8, SHADE.edge, { at: offset(at, 0, BOOM_Y - 2 - at[1], 0) }, 4.5);
}

/**
 * A grab cannon (P08-R10): a clamshell grab hanging from its jib on a cable, its four tines
 * frosted, a cannon between them firing bursts at the player.
 */
export function grab(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon, charge } = p;
  // P16-R06: a tentacle's clubbed tip, four bone hooks round a grafted cannon.
  flesh.cylinder(1.4, BOOM_Y - 8, 4, ICE_FLESH.crimson, { at: offset(at, 0, 8, 0) }, 2);
  flesh.lathe(
    [
      [6.5, 0],
      [7, 2],
      [5.5, 5],
      [2.5, 6.5],
    ],
    7,
    ICE_FLESH.crimson,
    { at: offset(at, 0, 2, 0), yaw: Math.PI / 8 },
  );
  hull.cylinder(2.6, 0.6, 8, H.panel, { at: offset(at, 0, 8.5, 0) });
  for (let k = 0; k < 4; k++) {
    const yaw = Math.PI / 4 + (k * Math.PI) / 2;
    const out = offset(at, Math.sin(yaw) * 6.5, 1, Math.cos(yaw) * 6.5);
    flesh.cylinder(1.2, 5, 4, ICE_FLESH.bone, { at: out, yaw, pitch: 0.5 }, 0);
  }
  neon.ring(7.1, 0.7, 8, ORANGE_NEON, { at: offset(at, 0, 3.2, 0), yaw: Math.PI / 8 });
  barrels(p, offset(at, ...GRAB_GUN), [1, 0], GRAB_BORE);
  charge.box([1.6, 1, 1.6], WHITE, { at: offset(at, 0, 9.1, 0) });
}
