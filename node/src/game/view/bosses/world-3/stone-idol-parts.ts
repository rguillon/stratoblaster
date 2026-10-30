import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { IDOL_EYE, IDOL_THROAT } from '../../../config/bosses/world-3/stone-idol';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { offset, QUARTER, WHITE } from '../mini-boss-shapes';
import { crack, moss, STONE, vine } from './stone-idol-stone';
import { F, veinTo } from './jungle-flesh';

// P09-R09, 3-3: the Stone Idol's parts (its eyes, their turning eyeballs, its mouth). Logical
// pixels, nose +Z (the chin), Y up (towards the camera); the face looks up at the camera.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Stone Idol's neon: the light glowing through its cracks, eyes and mouth. */
export const IDOL_NEON: Rgb = BOSS_LOOK.neon['stone-idol'] ?? [0.95, 0.2, 1];
/** Height of the face's carved surface. */
export const FACE = 12;

/** An eyeball: a polished stone ball (a lathe profile, around its centre's height). */
const EYEBALL = [
  [0, -6.5],
  [4.6, -4.6],
  [6.5, 0],
  [4.6, 4.6],
  [0, 6.5],
] as const;

/**
 * An eye's socket around its centre `at` (P09-R09): a deep, round hollow in the face, its rim
 * cracked and lit, moss on its lower lid. Its eyeball ({@link eyeball}) turns in it.
 */
export function eyeSocket(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  const s = Math.sign(at[0]);
  // P16-R05: a raw flesh eyelid ringed by a stone growth, veins spreading from its corner.
  hull.cylinder(10.5, 1.6, 10, STONE.dark, { at: offset(at, 0, FACE - 0.4, 0) }, 9.5);
  flesh.cylinder(9, 0.3, 10, F.crimson, { at: offset(at, 0, FACE + 1, 0) });
  veinTo(
    p,
    [offset(at, -s * 9, FACE + 0.6, -2), offset(at, -s * 15, FACE + 0.4, -9)],
    [0, 0, 2],
    IDOL_NEON,
  );
  neon.ring(9.7, 0.5, 10, IDOL_NEON, { at: offset(at, 0, FACE + 1.1, 0) });
  // A crack running from the socket's outer corner, and moss on the lower lid.
  const [x, , z] = at;
  crack(
    neon,
    [
      [x + s * 9, z + 3],
      [x + s * 12, z + 8],
      [x + s * 11, z + 13],
    ],
    FACE + 0.2,
    IDOL_NEON,
  );
  moss(hull, offset(at, -s * 4, FACE + 0.8, 9), 3.2, s);
}

/**
 * An eyeball turning in its socket (phase 8 review: it aims its laser): a ball of polished
 * stone, a neon iris facing down the screen and the charge-lit lens its laser leaves from.
 */
export function eyeball(p: EnemyParts, at: Vec3): void {
  const { flesh, vein, charge, muzzle } = p;
  // The right eye (screen right) is on the model's -X side.
  const lasers = at[0] < 0 ? IDOL_EYE : mirror(IDOL_EYE);
  const [tip] = lasers.map((m) => bossPoint(...m));
  if (!tip) return;
  const [x, y, z] = tip;
  const centre: Vec3 = [at[0], y, at[2]];
  // P16-R05: a living, wet eyeball of bone-white flesh, its iris a pulsing gland.
  flesh.lathe(EYEBALL, 8, F.bone, { at: centre });
  // The glowing iris looks up and forward, half at the camera, half where the eye aims.
  const iris = { pitch: IRIS_TILT };
  const along = (d: number): Vec3 => [
    centre[0],
    y + d * Math.cos(IRIS_TILT),
    centre[2] + d * Math.sin(IRIS_TILT),
  ];
  vein.cylinder(4.4, 0.8, 8, IDOL_NEON, { at: along(6.1), ...iris }, 4);
  flesh.cylinder(2, 0.5, 6, F.purple, { at: along(6.8), ...iris });
  const forward = { pitch: QUARTER };
  charge.cylinder(2.2, 1.6, 8, WHITE, { at: [x, y, z - 1.6], ...forward }, 1.4);
  muzzle(tip, 'laser');
}

/** The iris's tilt from straight up towards the front (+Z). */
const IRIS_TILT = QUARTER * 0.55;

/** The mouth's open lips (outline around its centre: half width, half depth). */
const LIPS = { width: 15, depth: 8 } as const;

/**
 * The mouth around its centre `at` (P09-R09): thick carved lips open on a deep throat, stone
 * teeth, a neon lining; its rings of boulders leave from the throat's glow.
 */
export function mouth(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  const { width: w, depth: d } = LIPS;
  // P16-R05: a living maw: a red throat, swollen flesh lips, the stone grown over them as armour.
  flesh.box([w * 2, 0.6, d * 2], F.wound, { at: offset(at, 0, FACE - 0.2, 0) });
  // Upper lip (towards the nose, -Z), lower lip, and the corners.
  flesh.box([w * 2 + 4, 4, 4], F.sinew, { at: offset(at, 0, FACE - 1, -d - 1) }, F.crimson);
  flesh.box([w * 2, 4.5, 5], F.sinew, { at: offset(at, 0, FACE - 1, d + 1.5) }, F.crimson);
  hull.box([w * 1.2, 1, 2.4], STONE.base, { at: offset(at, 0, FACE + 3, -d - 1.6) }, STONE.light);
  for (const s of SIDES) {
    flesh.box([4, 4, d * 2], F.sinew, { at: offset(at, s * (w + 1), FACE - 1, 0) });
    neon.box([0.5, 0.5, d * 2 - 1], IDOL_NEON, { at: offset(at, s * (w - 1.2), FACE + 0.4, 0) });
  }
  neon.box([w * 2 - 2, 0.5, 0.5], IDOL_NEON, { at: offset(at, 0, FACE + 0.4, -d + 1.2) });
  neon.box([w * 2 - 2, 0.5, 0.5], IDOL_NEON, { at: offset(at, 0, FACE + 0.4, d - 1.2) });
  // Stone teeth: square ones under the upper lip, worn ones on the lower.
  for (const x of [-9, -4.5, 0, 4.5, 9]) {
    flesh.box([3, 1.6, 2.6], F.bone, { at: offset(at, x, FACE, -d + 2.4) });
    if (x !== 0) flesh.box([2.6, 1.2, 2], F.bone, { at: offset(at, x * 0.9, FACE, d - 2.2) });
  }
  for (const throat of IDOL_THROAT.map((m) => bossPoint(...m))) {
    const glow: Vec3 = [throat[0], FACE + 0.1, throat[2]];
    charge.cylinder(5, throat[1] - glow[1], 8, WHITE, { at: glow }, 3);
    muzzle(throat, 'ring');
  }
  moss(hull, offset(at, 7, FACE + 3, d + 2), 3, 1);
  // A vine hanging from the lower lip over the chin.
  vine(hull, [offset(at, -6, FACE + 3, d + 2), offset(at, -9, FACE, d + 9), [at[0] - 8, 2, 50]]);
}
