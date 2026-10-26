import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { WRAITH_EYE_LENS, WRAITH_POD_GUNS } from '../../../config/bosses/world-4/ash-wraith';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { ashDrift, ASH_THIN, EMBER } from './ash-plains-soot';

// P10-R11, 4-2: the Ash Wraith's parts: its two shroud pods (ducted fans under ragged shrouds)
// and its eye cannon (a mount on the nose, the eye itself on a turret). Logical pixels, nose +Z,
// Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Wraith's pale cyan neon (P10-R11). */
export const WRAITH_CYAN: Rgb = BOSS_LOOK.neon['ash-wraith'] ?? [0.55, 0.95, 1];

/** A pod's duct around its fan: an open lathe, wider at its lip (around the pod's centre). */
const DUCT = [
  [9.4, -1.5],
  [11, -0.5],
  [11.2, 3.4],
  [10, 5],
] as const;
/** A torn strip of the shroud hanging off a duct (seen from above, from its root outwards). */
const TATTER = [
  [-1.6, 0],
  [1.6, 0],
  [1, 4.6],
  [0.2, 3.4],
  [-0.8, 5.4],
] as const;

/** Torn strips of the shroud around a duct at `at`, out towards the back and the side `s`. */
function tatters(hull: EnemyParts['hull'], at: Vec3, s: number): void {
  for (const [k, yaw] of [Math.PI * 0.75, Math.PI, Math.PI * 1.2, s * Math.PI * 0.55].entries()) {
    const root = offset(at, Math.sin(yaw) * 10.6, 3.6 - (k % 2) * 0.8, Math.cos(yaw) * 10.6);
    hull.slab(TATTER, [0, 0.4], k % 2 === 0 ? ASH_THIN : H.panel, { at: root, yaw, pitch: -0.25 });
  }
}

/**
 * A shroud pod around its centre `at` (P10-R11): a ducted fan, its lip ringed with pale cyan
 * neon, torn grey shroud strips trailing off it, ash on its lip, a gun housing under its front
 * with the two barrels of its fans.
 */
export function shroudPod(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  hull.lathe(DUCT, 10, H.panel, { at, yaw: Math.PI / 10 }, false);
  hull.cylinder(9.4, 0.5, 10, H.dark, { at: offset(at, 0, 0.2, 0) });
  hull.cylinder(2.4, 3, 6, H.base, { at: offset(at, 0, 0.6, 0) });
  p.rotor(offset(at, 0, 3, 0), 8.4);
  neon.ring(11.3, 0.7, 10, WRAITH_CYAN, { at: offset(at, 0, 3.9, 0), yaw: Math.PI / 10 });
  tatters(hull, at, s);
  ashDrift(hull, offset(at, s * 8.6, 5, -5), 2.6, at[0]);
  hull.box([9, 3, 6], H.base, { at: offset(at, 0, 0.3, 9) }, H.panel);
  // The right pod (screen right) is on the model's -X side.
  const guns = s < 0 ? WRAITH_POD_GUNS : mirror(WRAITH_POD_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(1.1, 5.6, 6, H.dark, { at: [x, y, z - 6.2], pitch: QUARTER });
    charge.cylinder(1.15, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** The eye's mount on the nose: an armoured collar (a lathe profile around its pivot). */
const COLLAR = [
  [8.6, 0],
  [9.4, 1.6],
  [8, 3.2],
  [6.4, 3.4],
] as const;

/** The eye cannon's mount around its pivot `at` (P10-R11): a collar on the nose, a cyan ring. */
export function eyeMount({ hull, neon }: EnemyParts, at: Vec3): void {
  hull.lathe(COLLAR, 9, H.panel, { at, yaw: Math.PI / 9 });
  neon.ring(9.5, 0.5, 9, WRAITH_CYAN, { at: offset(at, 0, 1.2, 0), yaw: Math.PI / 9 });
  hull.cylinder(6.2, 3.3, 9, H.dark, { at });
  for (const yaw of [Math.PI * 0.8, Math.PI * 1.2]) {
    hull.box([1.2, 1.2, 5], SHADE.edge, {
      at: offset(at, Math.sin(yaw) * 8, 2.6, Math.cos(yaw) * 8),
      yaw,
    });
  }
}

/** The eye's ball (a lathe profile around its pivot): a faceted, flattened sphere. */
const BALL = [
  [0, 3],
  [4.6, 3.6],
  [6, 5.6],
  [5, 7.8],
  [2.6, 9],
  [0, 9.2],
] as const;

/**
 * The eye cannon (P10-R11), turning on its mount: a dark armoured ball, a heavy lid over it, the
 * lens barrel reaching forward, its pale iris and lens lit as the laser charges.
 */
export function eyeTurret(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const [m] = WRAITH_EYE_LENS;
  const tip = m ? bossPoint(...m) : at;
  hull.lathe(BALL, 9, H.base, { at });
  hull.box([7, 1.2, 5], H.dark, { at: offset(at, 0, 8.2, -1.5), pitch: -0.18 }, ASH_THIN);
  const forward = { pitch: QUARTER };
  hull.cylinder(2.6, 6, 8, H.dark, { at: [tip[0], tip[1], at[2] + 3.2], ...forward }, 2.2);
  hull.cylinder(
    1.8,
    tip[2] - at[2] - 9.8,
    8,
    H.panel,
    { at: [tip[0], tip[1], at[2] + 9.2], ...forward },
    1.6,
  );
  neon.ring(2.9, 0.6, 8, WRAITH_CYAN, { at: [tip[0], tip[1], at[2] + 5.6], ...forward });
  neon.ring(2.1, 0.4, 8, EMBER, { at: [tip[0], tip[1], tip[2] - 2.6], ...forward });
  charge.cylinder(1.5, 0.6, 8, WHITE, { at: offset(tip, 0, 0, -0.6), ...forward });
  muzzle(tip, 'laser');
}
