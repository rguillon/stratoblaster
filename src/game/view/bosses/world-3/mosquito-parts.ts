import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { MOSQUITO_NEEDLE, MOSQUITO_WING_GUNS } from '../../../config/bosses/world-3/mosquito';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { sided } from '../final-boss-shapes';
import { seam } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';

// P09-R09, 3-4: the Mosquito's parts (its buzzing wings and its proboscis) and its swamp
// growth. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Mosquito's pink neon. */
export const MOSQUITO_PINK: Rgb = BOSS_LOOK.neon.mosquito ?? [1, 0.3, 0.7];
/** Swamp moss on its back and the dark, oily sheen of its wing membranes (World 3 growth). */
export const MOSS: Rgb = [0.13, 0.2, 0.07];
export const MEMBRANE: Rgb = [0.11, 0.08, 0.13];

/** Moss tufts at each point (`[x, y, z]`): low, lumpy cushions of growth. */
export function moss(hull: SolidBuilder, points: readonly Vec3[], size = 2.4): void {
  points.forEach((at, i) => {
    const r = size * (0.8 + (i % 3) * 0.2);
    hull.cylinder(r, r * 0.5, 5, MOSS, { at, yaw: i * 0.7 }, r * 0.45);
  });
}

/** The left wing seen from above (model +X), from its root's leading edge out and back. */
const WING: OutlinePoint[] = [
  [10, 1],
  [22, 3],
  [36, 2],
  [47, -1],
  [52, -5],
  [51, -9],
  [44, -12],
  [30, -13],
  [18, -11],
  [10, -7],
];
/** The membrane's neon veins, root to tip (left wing). */
const VEINS: readonly (readonly [OutlinePoint, OutlinePoint])[] = [
  [
    [12, 0],
    [49, -4],
  ],
  [
    [12, -4],
    [44, -10],
  ],
  [
    [14, -7],
    [30, -12],
  ],
];
/** Height of the membrane: a thin film over the pod. */
const WING_Y = 3;
/** A wing pod's nacelle under the membrane (loft stations around the pod's centre). */
const NACELLE = [
  [-7, 2.5, -2, 2],
  [-2, 4, -2.5, 3],
  [5, 3.6, -2, 2.6],
  [8, 2.2, -1, 1.6],
] as const;

/**
 * A wing around its pod's centre `at` (P09-R09), drawn on its buzzing joint: a long, thin
 * membrane veined with pink neon, and under it the fan pod with its two barrels.
 */
export function wing(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  hull.bevelSlab(sided(WING, s), [WING_Y - 0.3, WING_Y, WING_Y + 0.5], [0.3, 0.3], MEMBRANE);
  for (const [[ax, az], [bx, bz]] of VEINS) {
    seam(neon, [s * ax, az], [s * bx, bz], [WING_Y + 0.6, 0.5, 0.25], MOSQUITO_PINK);
  }
  seam(hull, [s * 10, 1], [s * 47, -1], [WING_Y + 0.4, 1.2, 0.8], H.panel);
  neon.box([1.4, 0.8, 1.4], MOSQUITO_PINK, { at: [s * 51, WING_Y + 0.6, -7] });
  hull.loft(POD_SECTION, NACELLE, H.base, { at: [at[0], -1, at[2]] });
  // The left wing (screen left) is on the model's +X side.
  const guns = s > 0 ? MOSQUITO_WING_GUNS : mirror(MOSQUITO_WING_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(0.9, 6, 6, H.dark, { at: [x, y, z - 6.6], pitch: QUARTER });
    charge.cylinder(0.95, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/** The proboscis's socket under the head (a lathe profile): the needle turns in it. */
const SOCKET = [
  [5.5, 0],
  [6, 2],
  [4.5, 4.5],
  [0, 5],
] as const;

/** The proboscis around its centre `at` (P09-R09): a ringed socket the needle turns in. */
export function proboscis({ hull, neon }: EnemyParts, at: Vec3): void {
  hull.lathe(SOCKET, 8, H.panel, { at: offset(at, 0, -1, 0), yaw: Math.PI / 8 });
  neon.ring(6.1, 0.6, 8, MOSQUITO_PINK, { at: offset(at, 0, 1, 0), yaw: Math.PI / 8 });
  for (const s of [-1, 1]) {
    hull.box([1.2, 1.6, 7], SHADE.edge, { at: offset(at, s * 6, 1, -2), yaw: s * 0.3 });
  }
}

/** The needle (a lathe profile along its axis, from its root to its point). */
const NEEDLE = [
  [2.6, 0],
  [2.2, 3],
  [1.2, 6],
  [0.9, 14],
  [0.4, 19],
] as const;

/**
 * The proboscis's needle, turning on its socket (P09-R09, D-073: it aims its laser at the
 * player during the warning line): a long, thin spike ringed in pink, its point glowing as the
 * laser charges.
 */
export function needle(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const [tip] = MOSQUITO_NEEDLE.map((m) => bossPoint(...m));
  if (!tip) return;
  const [x, y, z] = tip;
  const root: Vec3 = [x, y, at[2] + 1];
  const forward = { pitch: QUARTER };
  hull.lathe(NEEDLE, 6, H.dark, { at: root, ...forward });
  for (const along of [3.5, 8, 12]) {
    neon.ring(1.6 - along * 0.05, 0.5, 6, MOSQUITO_PINK, {
      at: offset(root, 0, 0, along),
      ...forward,
    });
  }
  hull.cylinder(3.2, 2.6, 8, H.panel, { at: offset(root, 0, 0, -1.5), ...forward });
  charge.cylinder(0.9, 1.6, 6, WHITE, { at: [x, y, z - 1.6], ...forward }, 0.2);
  muzzle(tip, 'laser');
}
