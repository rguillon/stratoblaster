import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import {
  ARMS,
  GOLEM_ARM,
  GOLEM_CANNON_GUNS,
  GOLEM_KNUCKLES,
  GOLEM_LENS,
  sideOf,
  type Arm,
} from '../../../config/bosses/world-4/obsidian-golem';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, type LimbDrawing } from '../boss-model';
import { mirrored } from '../final-boss-shapes';
import { seam } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { segment } from '../world-3/toucan-jungle';
import { barrel } from './magma-salamander-parts';

// P10-R11, 4-3: the Obsidian Golem's parts (its fists, shoulder cannons, chest emitter and armour
// plate), its arms and its obsidian look. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Golem's neon: the deep orange of its magma seams. */
export const GOLEM_NEON: Rgb = BOSS_LOOK.neon['obsidian-golem'] ?? [1, 0.32, 0.04];
/** Molten rock glowing in its seams and cracks, hotter than its neon. */
export const MAGMA: Rgb = [1, 0.55, 0.1];
/** Black volcanic glass: its armour plates (matte, a touch of violet). */
export const OBSIDIAN: Rgb = [0.045, 0.04, 0.055];

/** A crack of magma across a surface at height `y`: glowing strips through the points `path`. */
export function crack(neon: SolidBuilder, path: readonly OutlinePoint[], y: number): void {
  path.slice(1).forEach((b, i) => {
    const a = path[i];
    if (a) seam(neon, a, b, [y, 0.7, 0.3], MAGMA);
  });
}

/** The model-space points of `arm` at rest: its shoulder, its elbow and its fist's centre. */
export function armPoints(arm: Arm): [shoulder: Vec3, elbow: Vec3, fist: Vec3] {
  const s = sideOf(arm);
  const at = ([x, y]: readonly [number, number], h: number): Vec3 => bossPoint(s * x, y, h);
  return [at(GOLEM_ARM.shoulder, 12), at(GOLEM_ARM.elbow, 10), at(GOLEM_ARM.fist, 8)];
}

/** `arm`'s upper arm, on its shoulder: a thick, plated strut down to the elbow's joint. */
function upperArm(arm: Arm) {
  return ({ hull, neon }: EnemyParts): void => {
    const [shoulder, elbow] = armPoints(arm);
    segment(hull, [shoulder, elbow], [7, 6], H.base, 6);
    segment(hull, [offset(shoulder, 0, 4, 0), offset(elbow, 0, 3.6, 0)], [3.6, 3], OBSIDIAN, 5);
    segment(neon, [offset(shoulder, 0, 6.8, 0), offset(elbow, 0, 6.2, 0)], [0.5, 0.5], MAGMA, 4);
    hull.cylinder(7.4, 9, 7, H.dark, { at: offset(elbow, 0, -4.5, 0) });
    neon.ring(7.5, 0.8, 7, GOLEM_NEON, { at: offset(elbow, 0, 2, 0) });
  };
}

/** `arm`'s forearm, on its elbow: a massive tapering block of armour down to the wrist. */
function forearm(arm: Arm) {
  return ({ hull, neon }: EnemyParts): void => {
    const [, elbow, fist] = armPoints(arm);
    const wrist = offset(fist, 0, 0, -10);
    segment(hull, [elbow, wrist], [6.4, 7.6], H.panel, 6);
    for (const t of [0.35, 0.7]) {
      const at: Vec3 = [
        elbow[0] + (wrist[0] - elbow[0]) * t,
        elbow[1] + (wrist[1] - elbow[1]) * t,
        elbow[2] + (wrist[2] - elbow[2]) * t,
      ];
      neon.box([1.2, 1, 1.2], MAGMA, { at: offset(at, 0, 7.4, 0) });
    }
  };
}

/** The limbs of the two arms: an upper arm on each shoulder and a forearm on each elbow. */
export function armLimbs(): Record<string, LimbDrawing> {
  const limbs: Record<string, LimbDrawing> = {};
  for (const arm of ARMS) {
    limbs[`shoulder-${arm}`] = { draw: upperArm(arm) };
    limbs[`elbow-${arm}`] = { draw: forearm(arm) };
  }
  return limbs;
}

/**
 * A fist around its centre `at` (P10-R11), on its elbow: a huge block of obsidian, four knuckles
 * with magma glowing between them, a thumb on the inside, and the magma vent in the middle of
 * its knuckles that throws rings of slow, big globs.
 */
export function fist(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge } = p;
  const s = Math.sign(at[0]);
  const base = offset(at, 0, -1, -2);
  hull.box([26, 15, 20], OBSIDIAN, { at: base }, H.base);
  hull.box([27, 4, 21], H.dark, { at: offset(base, 0, 4, 0) });
  for (let k = 0; k < 4; k++) {
    const x = (k - 1.5) * 6.2;
    hull.box([5.6, 8, 5], H.panel, { at: offset(at, x, 1, 9) }, SHADE.edge);
    if (k > 0) neon.box([0.6, 6, 4], MAGMA, { at: offset(at, x - 3.1, 1.6, 9.4) });
  }
  hull.box([6, 7, 12], H.base, { at: offset(at, -s * 15, 0, 2), yaw: -s * 0.3 });
  crack(
    neon,
    [
      [at[0] + 8, at[2] - 6],
      [at[0] + 2, at[2] - 2],
      [at[0] - 6, at[2] - 7],
    ],
    at[1] + 14.1,
  );
  const guns = s > 0 ? GOLEM_KNUCKLES : mirror(GOLEM_KNUCKLES);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    hull.cylinder(3.4, 2, 7, H.dark, { at: offset(tip, 0, 0, -5.4), pitch: QUARTER });
    charge.ring(2.6, 1.2, 7, WHITE, { at: offset(tip, 0, 0, -3.6), pitch: QUARTER });
    barrel(p, tip, [1.8, 2.4]);
  }
}

/**
 * A shoulder cannon's mount around its centre `at` (P10-R11): a low armoured ring on the back
 * of its shoulder, its turret turning on it.
 */
export function cannonMount({ hull, neon }: EnemyParts, at: Vec3): void {
  hull.cylinder(11, 11, 8, H.base, { at: offset(at, 0, 0, 0), yaw: Math.PI / 8 }, 9.6);
  neon.ring(9.8, 0.7, 8, GOLEM_NEON, { at: offset(at, 0, 10.6, 0), yaw: Math.PI / 8 });
}

/** The cannon turret's dome (a lathe profile around its pivot). */
const DOME = [
  [8.4, 0],
  [8.6, 2.2],
  [6.6, 5],
  [3, 6.4],
  [0, 6.6],
] as const;

/**
 * A shoulder cannon's turret around its pivot `at` (P10-R11, D-060): a faceted dome on its
 * mount and two heavy barrels, turning the way their aimed spreads fire.
 */
export function cannonTurret(p: EnemyParts, at: Vec3): void {
  const { hull } = p;
  hull.lathe(DOME, 8, OBSIDIAN, { at: offset(at, 0, 11, 0), yaw: Math.PI / 8 });
  hull.box([9, 4, 6], H.dark, { at: offset(at, 0, 13, 7) }, H.panel);
  // The left cannon (screen left) is on the model's +X side.
  const guns = at[0] > 0 ? GOLEM_CANNON_GUNS : mirror(GOLEM_CANNON_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) barrel(p, tip, [1.2, 7]);
}

/** The armour plate seen from above: a chevron of obsidian over the chest (right half). */
const PLATE = mirrored([
  [0, 14],
  [12, 10],
  [19, 2],
  [16, -10],
  [0, -6],
]);

/**
 * The armour plate around its centre `at` (P10-R11, no weapon): a thick chevron of obsidian on
 * its chest, cracked with magma, bolted on with dark studs.
 */
export function plate({ hull, neon }: EnemyParts, at: Vec3): void {
  const [x, , z] = at;
  hull.bevelSlab(PLATE, [2, 10, 17], [1, 2], H.base, { at: [x, 0, z] }, OBSIDIAN);
  crack(
    neon,
    [
      [x - 10, z + 6],
      [x - 2, z + 2],
      [x + 3, z + 7],
      [x + 11, z + 3],
    ],
    17.1,
  );
  crack(
    neon,
    [
      [x - 2, z + 2],
      [x, z - 5],
    ],
    17.1,
  );
  for (const s of SIDES) {
    hull.cylinder(1.4, 1, 6, SHADE.edge, { at: [x + s * 13, 16.6, z + 3] });
    neon.box([0.6, 6, 0.6], GOLEM_NEON, { at: [x + s * 18.4, 8, z + 1] });
  }
}

/** The emitter's housing on its prow (a lathe profile along its axis, from its back). */
const HOUSING = [
  [5, 0],
  [8, 3],
  [8.6, 9],
  [6.8, 14],
  [5, 16],
] as const;

/**
 * The chest emitter around its centre `at` (P10-R11): a heavy housing on the prow under the
 * plate, ringed in orange, its lens glowing as the laser charges; the beam fires straight down.
 */
export function emitter(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const [lens] = GOLEM_LENS.map((m) => bossPoint(...m));
  if (!lens) return;
  const back: Vec3 = [lens[0], lens[1], lens[2] - 17.4];
  hull.lathe(HOUSING, 8, H.panel, { at: back, pitch: QUARTER, yaw: Math.PI / 8 });
  neon.ring(8.8, 1, 8, GOLEM_NEON, { at: offset(back, 0, 0, 8), pitch: QUARTER });
  hull.box([12, 4, 14], OBSIDIAN, { at: offset(at, 0, -2, -4) });
  charge.cylinder(4.4, 1.4, 8, WHITE, { at: offset(lens, 0, 0, -1.4), pitch: QUARTER });
  muzzle(lens, 'laser');
}
