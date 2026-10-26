import { BOSS_LOOK } from '../../../config/boss-look';
import {
  DRILL_HEIGHT,
  DRILL_REACH,
  RIG_DRILL,
  RIG_DRILL_GUN,
  RIG_SHOULDER,
  RIG_SIDES,
  RIG_VENT_TOP,
  sideSign,
  type RigSide,
} from '../../../config/bosses/world-4/geyser-rig';
import { mirror } from '../../../config/bosses/boss-kit';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import { lamps, rect, vent } from '../mini-boss-greebles';
import { conduit, ram } from '../mini-boss-mechanism';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { segment } from '../world-3/toucan-jungle';
import { ashDrift, EMBER, SCORCH, SOOT } from './ash-plains-soot';

// P10-R11, 4-2: the Geyser Rig's parts: its two drill heads on their swinging arms (moving limbs,
// D-061), its two steam vents and its drone hangar. Logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Rig's yellow neon (P10-R11). */
export const RIG_YELLOW: Rgb = BOSS_LOOK.neon['geyser-rig'] ?? [1, 0.88, 0.1];
/** Height of the rig's deck. */
export const DECK_Y = 7;

/** The model-space points of the `side` drill arm at rest: its shoulder and its drill head. */
function armPoints(side: RigSide): [shoulder: Vec3, head: Vec3] {
  const s = sideSign(side);
  return [
    bossPoint(s * RIG_SHOULDER[0], RIG_SHOULDER[1], DRILL_HEIGHT.shoulder),
    bossPoint(s * RIG_DRILL[0], RIG_DRILL[1], DRILL_HEIGHT.head),
  ];
}

/** The `side` drill arm, on its shoulder joint: a heavy boom, a ram along it, a yellow line. */
function drillArm(side: RigSide) {
  return ({ hull, neon }: EnemyParts): void => {
    const [shoulder, head] = armPoints(side);
    const back = offset(head, 0, 1, -7);
    hull.cylinder(5.4, DRILL_HEIGHT.shoulder + 2 - DECK_Y, 8, H.dark, {
      at: offset(shoulder, 0, DECK_Y - DRILL_HEIGHT.shoulder, 0),
    });
    hull.cylinder(4.4, 2.6, 8, H.panel, { at: offset(shoulder, 0, 2, 0) }, 3.6);
    segment(hull, [shoulder, back], [3.6, 3], H.base, 6);
    segment(hull, [offset(shoulder, 0, 3, 0), offset(back, 0, 2.6, 0)], [1.4, 1.2], SHADE.edge, 4);
    segment(
      neon,
      [offset(shoulder, 0, 4.3, 0), offset(back, 0, 3.8, 0)],
      [0.4, 0.35],
      RIG_YELLOW,
      4,
    );
    ram(
      hull,
      offset(shoulder, -sideSign(side) * 4, -1, 2),
      offset(back, -sideSign(side) * 3, -2, -3),
      1.4,
    );
  };
}

/** The limbs of the two drill arms: each boom on its shoulder joint. */
export function armLimbs(): Record<string, LimbDrawing> {
  return Object.fromEntries(RIG_SIDES.map((side) => [`arm-${side}`, { draw: drillArm(side) }]));
}

/**
 * A drill head around its centre `at` (P10-R11): a ribbed motor housing, a long fluted bit glowing
 * hot at its root, and the gun on top of the housing that fires aimed bursts.
 */
export function drillHead(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const forward = { pitch: QUARTER };
  const bitRoot = at[2] + 6;
  hull.cylinder(7.4, 14, 8, H.base, { at: offset(at, 0, 0, -8), ...forward, yaw: 0 });
  for (const dz of [-6, 0])
    hull.cylinder(8, 1.6, 8, H.panel, { at: offset(at, 0, 0, dz), ...forward });
  neon.ring(8.1, 0.6, 8, RIG_YELLOW, { at: offset(at, 0, 0, 3.4), ...forward });
  neon.ring(5.2, 1, 8, EMBER, { at: [at[0], at[1], bitRoot], ...forward });
  hull.cylinder(
    5.6,
    DRILL_REACH - 6,
    8,
    SHADE.edge,
    { at: [at[0], at[1], bitRoot], ...forward },
    0,
  );
  for (const k of [0, 1, 2]) {
    const roll = (k * 2 * Math.PI) / 3;
    const flute = offset(at, Math.cos(roll) * 3.6, Math.sin(roll) * 3.6, 9);
    hull.box([1.2, 1.2, 12], SOOT, { at: flute, roll, yaw: -Math.cos(roll) * 0.12 });
  }
  const s = Math.sign(at[0]);
  const guns = s > 0 ? RIG_DRILL_GUN : mirror(RIG_DRILL_GUN);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([5, 3.8, 8], H.panel, { at: [x, y - 2.4, z - 10] }, H.base);
    hull.cylinder(1.4, 7.4, 6, H.dark, { at: [x, y, z - 8], pitch: QUARTER });
    charge.cylinder(1.45, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** A vent stack's flared top (a lathe profile, from the deck up, around the stack's centre). */
const STACK = [
  [6.4, 0],
  [6, 3],
  [4.6, 5],
  [4, 12],
  [5.4, 14.6],
  [5.8, 16.4],
] as const;

/**
 * A steam vent around its centre `at` (P10-R11): a scorched stack rising from a valve block, its
 * flared mouth ringed with yellow neon, hot metal glowing in it, ash settled round its foot.
 */
export function steamVent(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  const [m] = s > 0 ? RIG_VENT_TOP : mirror(RIG_VENT_TOP);
  const top = m ? bossPoint(...m) : offset(at, 0, 24, 0);
  hull.box([15, 3, 15], H.base, { at: offset(at, 0, DECK_Y - 1, 0) }, H.panel);
  hull.lathe(STACK, 8, SCORCH, { at: offset(at, 0, DECK_Y + 1.4, 0), yaw: Math.PI / 8 }, false);
  neon.ring(5.9, 0.6, 8, RIG_YELLOW, { at: offset(top, 0, -2.6, 0), yaw: Math.PI / 8 });
  hull.cylinder(5.2, 0.4, 8, SOOT, { at: offset(top, 0, -4.2, 0) });
  neon.ring(3.4, 1.2, 8, EMBER, { at: offset(top, 0, -3.6, 0) });
  charge.cylinder(2.6, 0.6, 8, WHITE, { at: offset(top, 0, -0.6, 0) });
  muzzle(top, 'ring');
  for (const side of SIDES) {
    hull.cylinder(1.6, 3, 6, H.dark, { at: offset(at, side * 6, DECK_Y + 2, 5), roll: QUARTER });
  }
  conduit(hull, offset(at, s * -6, DECK_Y + 2, -2), offset(at, s * -15, DECK_Y + 2, -2), 1.2, 2);
  ashDrift(hull, offset(at, s * 5.5, DECK_Y + 2, -6), 2.6, at[0]);
}

/**
 * The drone hangar around its centre `at` (P10-R11): a bay jutting from the bow, its open door
 * framed in yellow, where its Hornets leave from; warning lamps either side.
 */
export function hangar({ hull, neon }: EnemyParts, at: Vec3): void {
  hull.bevelSlab(rect(28, 24), [DECK_Y - 5, DECK_Y, DECK_Y + 6], [1, 1.5], H.base, { at }, H.panel);
  hull.box([18, 6, 0.8], H.dark, { at: offset(at, 0, DECK_Y - 2, 11.8) });
  neon.box([20, 0.8, 0.6], RIG_YELLOW, { at: offset(at, 0, DECK_Y + 4, 12.2) });
  for (const s of SIDES) {
    neon.box([0.8, 6, 0.6], RIG_YELLOW, { at: offset(at, s * 9.8, DECK_Y - 2, 12.2) });
    lamps(neon, [offset(at, s * 12, DECK_Y + 6, 9)], 1.2, EMBER);
  }
  vent(hull, offset(at, 0, DECK_Y + 6, -3), [14, 9], 4);
  ashDrift(hull, offset(at, 8, DECK_Y + 6, 4), 2.4, 1.7);
  ashDrift(hull, offset(at, -8, DECK_Y + 6, -6), 2, 0.4);
}
