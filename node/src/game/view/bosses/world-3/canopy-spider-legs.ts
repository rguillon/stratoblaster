import { BOSS_LOOK } from '../../../config/boss-look';
import {
  endOf,
  LEG_GUN_REACH,
  LEG_HEIGHT,
  LEG_REST,
  LEGS,
  sideOf,
  type Leg,
} from '../../../config/bosses/world-3/canopy-spider';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import { H, offset, QUARTER, WHITE } from '../mini-boss-shapes';
import { moss, sagging, segment, vine } from './toucan-jungle';
import { F, gland } from './jungle-flesh';

// P09-R09, 3-2: the Canopy Spider's legs: an upper leg on each hip and a lower leg on each knee
// (moving limbs, D-061), stepping in turn, and the gun pods at their feet (its parts). Logical
// pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Spider's red neon (its eyes, the lines along its legs). */
export const SPIDER_RED: Rgb = BOSS_LOOK.neon['canopy-spider'] ?? [1, 0.12, 0.15];

/** The model-space points of `leg` at rest: its hip, knee and foot, at their heights. */
export function legPoints(leg: Leg): [hip: Vec3, knee: Vec3, foot: Vec3] {
  const s = sideOf(leg);
  const [hip, knee, foot] = LEG_REST[endOf(leg)].map(([x, y]) => [s * x, y] as const);
  const at = (p: readonly [number, number] | undefined, h: number): Vec3 =>
    bossPoint(p?.[0] ?? 0, p?.[1] ?? 0, h);
  return [at(hip, LEG_HEIGHT.hip), at(knee, LEG_HEIGHT.knee), at(foot, LEG_HEIGHT.foot)];
}

/** A knee: a faceted ball of armour, a red light on top. */
function kneeJoint({ hull, neon }: EnemyParts, knee: Vec3): void {
  hull.lathe(
    [
      [0, -3.6],
      [3.4, -2],
      [3.8, 0.6],
      [2.6, 3],
      [0, 3.8],
    ],
    7,
    H.panel,
    { at: knee },
  );
  neon.box([1.2, 0.6, 1.2], SPIDER_RED, { at: offset(knee, 0, 3.6, 0) });
}

/** `leg`'s upper leg, on its hip: an armoured strut rising to the knee, a red line along it. */
function upperLeg(leg: Leg) {
  return (p: EnemyParts): void => {
    const { hull, flesh, neon } = p;
    const [hip, knee] = legPoints(leg);
    // P16-R06: a jointed leg of purple chitin over sinew, a metal knee joint grafted on.
    segment(flesh, [hip, knee], [3.4, 2.6], F.purple, 6);
    segment(flesh, [offset(hip, 0, 2.6, 0), offset(knee, 0, 2.2, 0)], [1.6, 1.2], F.sinew, 4);
    segment(neon, [offset(hip, 0, 3.7, 0), offset(knee, 0, 3.2, 0)], [0.45, 0.4], SPIDER_RED, 4);
    hull.cylinder(4.2, 3, 7, H.dark, { at: offset(hip, 0, -1.5, 0) }, 3.6);
    kneeJoint(p, knee);
    moss(hull, offset(knee, 0, 3.4, 0), 2.6, hip[0] + hip[2]);
  };
}

/** `leg`'s lower leg, on its knee: a tapering shin dropping to its foot, a vine around it. */
function lowerLeg(leg: Leg) {
  return ({ hull, flesh, neon }: EnemyParts): void => {
    const [, knee, foot] = legPoints(leg);
    const ankle = offset(foot, 0, 5, 0);
    segment(flesh, [knee, ankle], [2.6, 1.7], F.purple, 6);
    segment(neon, [offset(knee, 0, 2.2, 0), offset(ankle, 0, 1.4, 0)], [0.4, 0.3], SPIDER_RED, 4);
    // Spines along its back.
    for (const t of [0.3, 0.6]) {
      const at: Vec3 = [
        knee[0] + (ankle[0] - knee[0]) * t,
        knee[1] + (ankle[1] - knee[1]) * t + 1.6,
        knee[2] + (ankle[2] - knee[2]) * t,
      ];
      flesh.cylinder(0.7, 2.6, 4, F.bone, { at }, 0);
    }
    vine(hull, sagging(offset(knee, 0, -1, 0), offset(ankle, 0, -1.4, 0), 4, 2.4), 0.4);
  };
}

/** The limbs of the four legs: an upper leg on each hip and a lower leg on each knee. */
export function legLimbs(): Record<string, LimbDrawing> {
  const limbs: Record<string, LimbDrawing> = {};
  for (const leg of LEGS) {
    limbs[`hip-${leg}`] = { draw: upperLeg(leg) };
    limbs[`knee-${leg}`] = { draw: lowerLeg(leg) };
  }
  return limbs;
}

/** A gun pod's armoured foot (a lathe profile around its centre). */
const FOOT = [
  [4, 0],
  [6.4, 1.6],
  [6, 4.4],
  [3.6, 6.6],
  [0, 7.2],
] as const;

/**
 * A leg's gun pod at its foot `at` (P09-R09): an armoured foot gripping the canopy with three
 * claws, a red ring around it, and a gun pointing forward that fires aimed spreads.
 */
export function legGunPod(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  const foot = offset(at, 0, LEG_HEIGHT.foot - 3, 0);
  // P16-R06: a swollen flesh foot gripping with bone claws, its gun a grafted metal pod.
  p.flesh.lathe(FOOT, 7, F.crimson, { at: foot });
  gland(p, offset(foot, 0, 5.2, 0), 2, SPIDER_RED);
  neon.ring(6.5, 0.7, 7, SPIDER_RED, { at: offset(foot, 0, 1.8, 0) });
  for (const yaw of [s * 1.2, s * 2.2, Math.PI]) {
    const out = offset(foot, Math.sin(yaw) * 7, 0, Math.cos(yaw) * 7);
    p.flesh.box([1.6, 1.4, 5], F.bone, { at: out, yaw, pitch: 0.35 });
  }
  const tip: Vec3 = [at[0], LEG_HEIGHT.foot, at[2] + LEG_GUN_REACH];
  hull.box([4.4, 3.4, 5], H.base, { at: offset(tip, 0, -1.7, -9.5) }, H.panel);
  hull.cylinder(1.3, 6.4, 6, H.dark, { at: offset(tip, 0, 0, -7), pitch: QUARTER });
  charge.cylinder(1.35, 0.6, 6, WHITE, { at: offset(tip, 0, 0, -0.6), pitch: QUARTER });
  muzzle(tip);
}
