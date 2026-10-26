import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement, SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { JAGUAR_CLAW, JAGUAR_TAIL } from '../../../config/bosses/world-3/jaguar';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, POD_SECTION } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';

// P09-R09, 3-5: the Jaguar's destroyable parts (its two claw guns and its tail cannon) and its
// spotted armour. Model space: logical pixels, nose +Z, Y up; each part drawn around its centre
// `at`, each turret around its pivot.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const H = ENEMY_LOOK.hull;
const WHITE: Rgb = [1, 1, 1];
const QUARTER = Math.PI / 2;

/** Its amber neon (GD-61, `boss-look.ts`). */
export const AMBER: Rgb = BOSS_LOOK.neon.jaguar ?? [1, 0.6, 0.05];
/** The spotted armour: a warm ochre metal, dark rosettes on it, worn steel talons. */
export const COAT: Rgb = [0.2, 0.135, 0.06];
export const ROSETTE: Rgb = [0.03, 0.022, 0.015];
const ROSETTE_HEART: Rgb = [0.13, 0.08, 0.03];
const TALON: Rgb = [0.26, 0.25, 0.27];

/**
 * A jaguar's rosette painted at height `y` around `[x, z]`: five dark blotches in a ring, `r`
 * from its centre, round a darker heart.
 */
export function rosette(hull: SolidBuilder, [x, z]: OutlinePoint, r: number, y: number): void {
  const heart = Array.from({ length: 5 }, (_, k): OutlinePoint => {
    const a = (2 * Math.PI * k) / 5;
    return [x + Math.sin(a) * r * 0.7, z + Math.cos(a) * r * 0.7];
  });
  decal(hull, heart, y - 0.02, ROSETTE_HEART);
  for (let k = 0; k < 5; k++) {
    const a = (2 * Math.PI * k) / 5 + x * 0.1;
    const [cx, cz] = [x + Math.sin(a) * r, z + Math.cos(a) * r];
    const [u, v] = [Math.cos(a) * r * 0.42, -Math.sin(a) * r * 0.42];
    const [du, dv] = [Math.sin(a) * r * 0.22, Math.cos(a) * r * 0.22];
    decal(
      hull,
      [
        [cx - u - du, cz - v - dv],
        [cx + u - du, cz + v - dv],
        [cx + u * 0.7 + du, cz + v * 0.7 + dv],
        [cx - u * 0.7 + du, cz - v * 0.7 + dv],
      ],
      y,
      ROSETTE,
    );
  }
}

/** A claw's armoured pad around its centre, and the arm reaching back to the wing root. */
const PAD: OutlinePoint[] = [
  [0, 9],
  [7, 6],
  [8, -3],
  [5, -9],
  [-5, -9],
  [-8, -3],
  [-7, 6],
];
const PAD_TOP = 2.5;

/** `outline` moved to `[x, z]`. */
const moved = (outline: readonly OutlinePoint[], [x, , z]: Vec3): OutlinePoint[] =>
  outline.map(([px, pz]): OutlinePoint => [px + x, pz + z]);

/**
 * A claw gun's mount (P09-R09): an armoured pad on an arm reaching forward from the wing root,
 * spotted on top, amber lights along its flank (its gun turns on it, {@link clawTurret}).
 */
export function clawMount({ hull, neon }: EnemyParts, at: Vec3): void {
  const s = Math.sign(at[0]) || 1;
  hull.bevelSlab(moved(PAD, at), [-2, 0, PAD_TOP], [1, 1.4], H.panel, {}, COAT);
  hull.box([7, 3.5, 14], H.base, { at: [at[0] - s * 2, -1.5, at[2] - 14] }, COAT);
  rosette(hull, [at[0] + s * 4, at[2] - 14], 2, 2.05);
  neon.box([0.8, 0.6, 12], AMBER, { at: [at[0] + s * 8.2, 0.2, at[2] - 1], yaw: s * 0.12 });
  neon.ring(7.6, 0.5, 8, AMBER, { at: [at[0], PAD_TOP - 0.3, at[2]], yaw: Math.PI / 8 });
}

/** The claw gun's housing (a lathe profile, bottom to top) and its talons (from above). */
const HOUSING = [
  [6.5, 0],
  [7, 1.6],
  [5.4, 4.2],
  [2.4, 5.2],
  [0, 5.4],
] as const;
const BLADE: OutlinePoint[] = [
  [-1.5, 0],
  [1.5, 0],
  [0.9, 7],
  [-0.3, 10],
];

/** A barrel along +Z from `start` to the muzzle `tip`, its charge light at the tip. */
function barrel(
  { hull, charge, muzzle }: EnemyParts,
  tip: Vec3,
  [start, bore]: readonly [number, number],
  kind = 'gun',
): void {
  const along = (z: number): Placement => ({ at: [tip[0], tip[1], z], pitch: QUARTER });
  hull.cylinder(bore, tip[2] - 2 - start, 6, H.dark, along(start), bore * 0.85);
  charge.cylinder(bore * 1.1, 2, 6, WHITE, along(tip[2] - 2), bore * 0.7);
  muzzle(tip, kind);
}

/**
 * A claw gun (P09-R09), turning on its pad: a low housing, twin barrels between three steel
 * talons curving forward like a paw's claws.
 */
export function clawTurret(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  const tips = (at[0] < 0 ? JAGUAR_CLAW : mirror(JAGUAR_CLAW)).map((m) => bossPoint(...m));
  hull.lathe(HOUSING, 8, H.panel, { at: [at[0], PAD_TOP, at[2]], yaw: Math.PI / 8 });
  hull.box([9, 2.6, 4], H.dark, { at: [at[0], 4.6, at[2] + 4] }, COAT);
  for (const tip of tips) barrel(p, tip, [at[2] + 4, 1.2]);
  for (const dx of [-5, 0, 5]) {
    hull.bevelSlab(BLADE, [3, 3.6, 4.6], [0.2, 0.5], TALON, {
      at: [at[0] + dx, 0, at[2] + (dx === 0 ? 7 : 5)],
      yaw: dx * 0.05,
    });
  }
  neon.box([4, 0.4, 0.8], AMBER, { at: [at[0], PAD_TOP + 5.1, at[2] - 2.5] });
}

/** The tail cannon's mount: a pod at the tip of the tail, and the pylon its cannon turns on. */
const PYLON_TOP = 13;

/** The tail cannon's mount (P09-R09): a spotted pod at the tail's tip, a pylon, a lit ring. */
export function tailMount({ hull, neon }: EnemyParts, at: Vec3): void {
  hull.lathe(
    [
      [7, -2],
      [8, 1],
      [6, 3.5],
      [3.5, 4],
    ],
    8,
    COAT,
    { at, yaw: Math.PI / 8 },
  );
  hull.cylinder(2.6, PYLON_TOP - 3, 6, H.dark, { at: [at[0], 3, at[2]] }, 2);
  neon.ring(8.1, 0.6, 8, AMBER, { at: [at[0], 0.4, at[2]], yaw: Math.PI / 8 });
}

/** The tail cannon's body along Z around its pivot (loft stations: z, half width, bottom, top). */
const CANNON = [
  [-9, 2.5, -1.5, 2.5],
  [-4, 4.5, -2.5, 4],
  [4, 4.5, -2.5, 4],
  [8, 3, -1.5, 3],
] as const;

/**
 * The tail cannon (P09-R09), turning on its pylon high over the tail: a spotted pod, a long
 * barrel reaching forward over the wing, its lens glowing as the laser charges.
 */
export function tailTurret(p: EnemyParts, at: Vec3): void {
  const [m] = JAGUAR_TAIL;
  const tip = m ? bossPoint(...m) : at;
  p.hull.loft(POD_SECTION, CANNON, COAT, { at: [at[0], PYLON_TOP + 2.5, at[2]] });
  rosette(p.hull, [at[0], at[2] - 3], 1.4, PYLON_TOP + 6.55);
  barrel(p, tip, [at[2] + 8, 1.8], 'laser');
  for (const dz of [at[2] + 12, at[2] + 17]) {
    p.neon.ring(2.1, 0.8, 6, AMBER, { at: [tip[0], tip[1], dz], pitch: QUARTER });
  }
}
