import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { OWL_EYE_LENS, OWL_POD_GUNS } from '../../../config/bosses/world-2/snow-owl';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';

// P08-R10, 2-3: the Snow Owl's parts (its radar pods and sensor eye) and its frost. Logical
// pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Snow Owl's white neon. */
export const OWL_WHITE: Rgb = BOSS_LOOK.neon['snow-owl'] ?? [0.85, 0.92, 1];
/** Snow lying on its top faces, and the bluer ice of its crust and icicles (World 2 frost). */
export const FROST: Rgb = [0.75, 0.82, 0.9];
export const ICE: Rgb = [0.5, 0.62, 0.76];

/** Icicles hanging from each point (`[x, y, z]`, `x` times `side`): thin cones of ice. */
export function icicles(hull: SolidBuilder, points: readonly Vec3[], side = 1): void {
  points.forEach(([x, y, z], i) => {
    const length = 3.5 + (i % 3) * 1.2;
    hull.cylinder(0.9, length, 4, ICE, { at: [side * x, y, z], pitch: Math.PI }, 0);
  });
}

/** A radar pod's nacelle under its radome (loft stations around the pod's centre). */
const NACELLE = [
  [-11, 4, -3, 3],
  [-4, 5.5, -3.5, 4],
  [8, 5, -3, 3.5],
  [13, 3.5, -1.5, 2.5],
] as const;
/** A pod's radome: an iced dome on the wing (a lathe profile). */
const RADOME = [
  [7, 1.6],
  [7.2, 3],
  [5.8, 5.2],
  [3, 6.8],
  [0, 7.2],
] as const;

/**
 * A wing radar pod around its centre `at` (P08-R10): a nacelle under an iced radome with a
 * turning antenna on top, and two fan barrels poking out of the nacelle's front.
 */
export function radarPod(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  hull.loft(POD_SECTION, NACELLE, H.base, { at: [at[0], 0, at[2]] });
  hull.lathe(RADOME, 8, FROST, { at: offset(at, 0, 0, -2), yaw: Math.PI / 8 });
  neon.ring(7.3, 0.6, 8, OWL_WHITE, { at: offset(at, 0, 2, -2), yaw: Math.PI / 8 });
  p.rotor(offset(at, 0, 7.4, -2), 6.5);
  hull.box([3, 1, 5], SHADE.edge, { at: offset(at, s * 4.5, 3.4, -9) });
  icicles(hull, [offset(at, 3, -3, -6), offset(at, -3, -3, -3)]);
  // The right pod (screen right) is on the model's -X side.
  const guns = s < 0 ? OWL_POD_GUNS : mirror(OWL_POD_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(1.2, 6.4, 6, H.dark, { at: [x, y, z - 7], pitch: QUARTER });
    charge.cylinder(1.25, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}

/**
 * The sensor eye around its centre `at` (P08-R10): a big round housing facing forward, its lens
 * ringed with white neon, the iris lighting up as its laser charges, under a snow-capped brow.
 */
export function eye(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const [lens] = OWL_EYE_LENS.map((m) => bossPoint(...m));
  if (!lens) return;
  const [x, y, z] = lens;
  const forward = { pitch: QUARTER };
  hull.cylinder(9.5, 9, 10, H.panel, { at: [x, y, z - 10.5], ...forward }, 9);
  neon.ring(9.7, 0.8, 10, OWL_WHITE, { at: [x, y, z - 2.3], ...forward });
  neon.cylinder(7.5, 0.8, 10, OWL_WHITE, { at: [x, y, z - 1.5], ...forward });
  hull.cylinder(5.4, 0.3, 10, H.dark, { at: [x, y, z - 0.7], ...forward });
  charge.cylinder(3.6, 0.7, 8, WHITE, { at: [x, y, z - 0.7], ...forward });
  muzzle(lens, 'laser');
  hull.box([22, 2.2, 7], H.base, { at: offset(at, 0, 14.5, 1), pitch: -0.12 }, FROST);
  icicles(hull, [offset(at, 6, 14.6, 4), offset(at, -1, 14.6, 4.3), offset(at, -7, 14.6, 4)]);
  for (const s of SIDES) {
    hull.box([1.4, 7, 8], H.base, { at: offset(at, s * 10.4, 2.5, 0) }, SHADE.edge);
    neon.box([0.5, 0.5, 6], OWL_WHITE, { at: offset(at, s * 11.2, 8.6, 0) });
  }
}
