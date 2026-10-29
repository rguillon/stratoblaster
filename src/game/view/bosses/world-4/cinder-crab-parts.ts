import type { OutlinePoint } from '../../../../render/geometry/outline';
import { mirror } from '../../../config/bosses/boss-kit';
import {
  CRAB_ARM,
  CRAB_MORTAR,
  CRAB_PALM_GUN,
  CRAB_SWING,
} from '../../../config/bosses/world-4/cinder-crab';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { flipX } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-limbs';
import { H, offset, SHADE, WHITE } from '../mini-boss-shapes';
import { barrelTo, blot, FORGE, moltenSeam, soot, strut } from './black-sands-kit';
import { glands, SKIN } from './living-forge';

// P10-R11, 4-1: the Cinder Crab's arms (on their shoulders) and outer fingers (on their wrists),
// moving limbs (D-061), its claws and its back mortar (its parts). Logical pixels, nose +Z, Y up;
// the left claw (the screen's left, -X on the playfield) is drawn at +X.
type Vec3 = [number, number, number];

/** The Cinder Crab's orange neon (P10-R11). */
export const CRAB_ORANGE = BOSS_LOOK.neon['cinder-crab'] ?? [1, 0.45, 0.05];

/** The claw's palm seen from above, around the claw's centre (x across, z along). */
const PALM: readonly OutlinePoint[] = [
  [-6, -8],
  [6, -8],
  [7.5, -2],
  [6.5, 6],
  [-6.5, 6],
  [-7.5, -2],
];
/** The palm's heights: its bottom, its waist and its top. */
const PALM_Y = [0, 3, 7.5] as const;
/**
 * A left claw's fingers seen from above (x across, z along), from their roots: the fixed one
 * on the inner side (towards -X) and the moving one on the outer side, each curving in to its
 * tip, as they are shut.
 */
const FIXED_FINGER: readonly OutlinePoint[] = [
  [-2.6, 0],
  [2.4, 0],
  [2, 9],
  [0.6, 16],
  [-1, 17],
  [-2.8, 10],
];
const MOVING_FINGER: readonly OutlinePoint[] = [
  [-2.4, 0],
  [2.8, 0],
  [3, 10],
  [1, 17.5],
  [-0.6, 18],
  [-2, 9],
];
/** The fingers' heights, and how far from the claw's middle line they stand. */
const FINGER_Y = [0.5, 2.5, 5.5] as const;
const FINGER_OUT = 4.6;

/** The side of a claw drawn at `at`: +1 for the left one (at +X), -1 for the right one. */
const sideAt = (at: readonly number[]): number => Math.sign(at[0] ?? 1) || 1;

/** `outline` for the claw on side `s` (+1 the left one), mirrored for the right one. */
const sided = (outline: readonly OutlinePoint[], s: number) => (s > 0 ? outline : flipX(outline));

/**
 * The claw on side `s` (P10-R11), around its centre `at`: an armoured palm with a molten seam
 * across it, an orange light along its outer side, the fixed finger on its inner side and the
 * palm gun between the fingers.
 */
export function claw(p: EnemyParts, at: Vec3): void {
  const { hull, neon, flesh } = p;
  const s = sideAt(at);
  // P16-R05: a swollen flesh palm, bone pincers, a molten gland.
  flesh.bevelSlab(PALM, PALM_Y, [1, 1.6], SKIN.base, { at }, SKIN.panel);
  glands(p, [offset(at, -s * 2.5, PALM_Y[2] - 0.4, 3)], 1.6, FORGE.molten);
  const fixed = offset(at, -s * FINGER_OUT, 0, 5);
  flesh.bevelSlab(sided(FIXED_FINGER, s), FINGER_Y, [0.6, 0.9], SKIN.bone, { at: fixed });
  for (const dz of [5, 10]) {
    hull.box([1.4, 1.6, 1.2], SHADE.edge, { at: offset(fixed, s * 2.2, 1.5, dz) });
  }
  neon.box([0.8, 0.8, 11], CRAB_ORANGE, { at: offset(at, s * 7.3, 2.6, -1.5), yaw: -s * 0.08 });
  moltenSeam(
    neon,
    [
      [at[0] - 5, at[2] - 3],
      [at[0] - 1, at[2] - 1.5],
      [at[0] + 2, at[2] - 4],
      [at[0] + 5, at[2] - 2],
    ],
    PALM_Y[2],
  );
  soot(hull, blot([at[0] + s * 2, at[2] + 2], 2.6, 1, s), PALM_Y[2]);
  const guns = s > 0 ? CRAB_PALM_GUN : mirror(CRAB_PALM_GUN);
  for (const tip of guns) barrelTo(p, tip, [1.6, 9]);
}

/** Where a claw's arm bends and meets its palm (x across, height, z along), the left one. */
const ELBOW = { out: 30, height: 7, z: 22 } as const;

/** The arm on side `s`: a shoulder ball, an armoured upper arm out to the elbow, a forearm. */
function arm(s: number) {
  return ({ hull, neon, flesh }: EnemyParts): void => {
    const [sx, sy] = CRAB_ARM.shoulder;
    const [cx, cy] = CRAB_ARM.claw;
    const shoulder = bossPoint(s * sx, sy, 5);
    const elbow: Vec3 = [s * ELBOW.out, ELBOW.height, ELBOW.z];
    const wrist = offset(bossPoint(s * cx, cy, 4), -s * 1, 0, -6);
    flesh.lathe(
      [
        [0, -1],
        [4, 0.5],
        [4, 3],
        [0, 4.5],
      ],
      7,
      SKIN.panel,
      { at: offset(shoulder, 0, -2, 0) },
    );
    strut(flesh, [shoulder, elbow], [3.2, 2.8], SKIN.base);
    strut(flesh, [elbow, wrist], [2.8, 2.4], SKIN.panel);
    hull.lathe(
      [
        [0, -3],
        [3.4, -1.5],
        [3.4, 1.5],
        [0, 3.2],
      ],
      6,
      H.dark,
      { at: elbow },
    );
    strut(
      neon,
      [offset(shoulder, 0, 3, 0), offset(elbow, 0, 2.8, 0)],
      [0.45, 0.45],
      CRAB_ORANGE,
      4,
    );
    strut(neon, [offset(elbow, 0, 2.5, 0), offset(wrist, 0, 2.4, 0)], [0.4, 0.4], FORGE.molten, 4);
  };
}

/**
 * The moving finger on side `s`, on its wrist, drawn half open (as at rest): it swings from
 * shut to wide open with its joint (D-061), a hot glow along its inner edge.
 */
function finger(s: number) {
  return ({ hull, neon, flesh }: EnemyParts): void => {
    const [wx, wy] = CRAB_ARM.wrist;
    const pivot = bossPoint(s * wx, wy);
    const yaw = (s * CRAB_SWING.fingerDeg * Math.PI) / 180;
    const root = turn([s * FINGER_OUT, 0, 1], yaw);
    const at = offset(pivot, root[0], 0, root[2]);
    flesh.bevelSlab(sided(MOVING_FINGER, s), FINGER_Y, [0.6, 0.9], SKIN.bone, { at, yaw });
    for (const dz of [5, 10, 14]) {
      const tooth = turn([-s * 2.2, 1.5, dz], yaw);
      hull.box([1.4, 1.6, 1.2], SHADE.edge, { at: offset(at, tooth[0], 1.5, tooth[2]), yaw });
    }
    const glow = turn([-s * 1.4, 0, 8], yaw);
    neon.box([0.6, 0.6, 9], FORGE.molten, {
      at: offset(at, glow[0], FINGER_Y[2] - 0.3, glow[2]),
      yaw,
    });
  };
}

/** `[x, y, z]` turned by `yaw` around +Y (as `SolidBuilder` places a yawed solid). */
function turn([x, y, z]: Vec3, yaw: number): Vec3 {
  const [c, k] = [Math.cos(yaw), Math.sin(yaw)];
  return [x * c + z * k, y, -x * k + z * c];
}

/**
 * The arms and moving fingers (D-061): each drawn on its joint, they go and flash with their
 * claw.
 */
export const CRAB_LIMBS: Readonly<Record<string, LimbDrawing>> = {
  'arm-left': { draw: arm(1), part: 'claw-left' },
  'arm-right': { draw: arm(-1), part: 'claw-right' },
  'finger-left': { draw: finger(1), part: 'claw-left' },
  'finger-right': { draw: finger(-1), part: 'claw-right' },
};

/** The mortar's turntable (a lathe profile, bottom to top), and the barrel's bore. */
const TURNTABLE = [
  [8.5, 0],
  [8.5, 1.8],
  [6.5, 4.2],
  [0, 4.8],
] as const;
const BORE = 3.2;

/**
 * The back mortar (P10-R11) around its centre `at`, standing on the carapace at height `base`:
 * a squat turntable with an orange ring, a fat barrel leaning forward over the carapace on its
 * trunnions, its mouth glowing as it loads.
 */
export function mortar(p: EnemyParts, at: Vec3, base: number): void {
  const { hull, neon, charge, muzzle } = p;
  const [mouth] = CRAB_MORTAR;
  if (!mouth) return;
  const tip = bossPoint(...mouth);
  const foot = offset(at, 0, base, 0);
  hull.lathe(TURNTABLE, 8, H.panel, { at: foot, yaw: Math.PI / 8 });
  neon.ring(8.6, 0.6, 8, CRAB_ORANGE, { at: offset(foot, 0, 1, 0), yaw: Math.PI / 8 });
  const pivot = offset(foot, 0, 4.2, 2);
  const [dx, dy, dz] = [tip[0] - pivot[0], tip[1] - pivot[1], tip[2] - pivot[2]];
  const length = Math.hypot(dx, dy, dz);
  const along = (t: number): Vec3 =>
    offset(pivot, (dx * t) / length, (dy * t) / length, (dz * t) / length);
  const light = BORE * 0.7;
  strut(hull, [along(-3), along(length - light)], [BORE + 0.6, BORE], H.dark, 8);
  strut(
    hull,
    [along(length - light - 3), along(length - light)],
    [BORE + 0.9, BORE + 0.9],
    H.panel,
    8,
  );
  strut(charge, [along(length - light), tip], [BORE * 0.85, BORE * 0.85], WHITE, 8);
  muzzle(tip);
  for (const x of [-1, 1]) hull.box([2.6, 4, 4], H.dark, { at: offset(pivot, x * 4.4, -2, 0) });
}
