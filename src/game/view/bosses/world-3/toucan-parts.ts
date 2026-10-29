import type { LoftStation } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { TOUCAN_BEAK_TIP, TOUCAN_POD_GUNS } from '../../../config/bosses/world-3/toucan';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, sac, veinTo } from './jungle-flesh';
import { bossPoint } from '../boss-limbs';
import { lamps } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { moss, segment } from './toucan-jungle';

// P09-R09, 3-2: the Toucan's parts: its huge beak cannon and its two wing pods (ducted fans).
// Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Toucan's yellow neon, and the orange one of its accents (P09-R09). */
export const TOUCAN_YELLOW: Rgb = BOSS_LOOK.neon.toucan ?? [1, 0.7, 0.1];
export const TOUCAN_ORANGE: Rgb = [1, 0.36, 0.04];

/** The beak's bright paint: yellow along most of it, orange towards the tip, a dark root. */
const BEAK_YELLOW: Rgb = [0.95, 0.66, 0.1];
const BEAK_ORANGE: Rgb = [0.95, 0.34, 0.05];
/** The beak along Z, from its root on the head to just behind the emitter (loft stations). */
const BEAK: readonly LoftStation[] = [
  [20, 10, -1, 12],
  [28, 9.6, -0.6, 11.6],
  [36, 8.2, 0.4, 10.6],
  [44, 6.2, 1.8, 9.2],
  [50, 3.8, 3, 7.4],
  [53.6, 1.8, 3.9, 6.1],
];
/** The bands of the beak painted orange (towards its tip) and dark (its root). */
const ORANGE_BANDS = new Set([3, 4]);

/** The paint of the beak's faces: its root band dark, its last bands orange, yellow between. */
function beakPaint(_side: number, band: number): Rgb | undefined {
  if (band === 0) return H.dark;
  return ORANGE_BANDS.has(band) ? BEAK_ORANGE : undefined;
}

/**
 * The beak cannon (P09-R09): a huge, bright, faceted beak with neon along its ridge and cutting
 * edges, the laser emitter in its tip (its lens lights up as it charges).
 */
export function beak(p: EnemyParts): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  // P16-R05: a living, horny beak (its bright paint the toucan's mark), a metal band at its root.
  flesh.loft(ROUND_SECTION, BEAK, BEAK_YELLOW, {}, { paint: beakPaint });
  hull.box([20.4, 2, 2.4], H.panel, { at: [0, 4.6, 22] }, H.base);
  segment(
    neon,
    [
      [0, 12.05, 21],
      [0, 7.5, 50.5],
    ],
    [0.5, 0.4],
    TOUCAN_YELLOW,
    4,
  );
  for (const s of SIDES) {
    segment(
      neon,
      [
        [s * 10.1, 1.3, 21],
        [s * 3.9, 3.5, 50],
      ],
      [0.45, 0.35],
      TOUCAN_ORANGE,
      4,
    );
    // Nostrils at the root of the beak.
    hull.box([1.4, 0.6, 2.2], SHADE.soot, { at: [s * 3.5, 11.6, 23] });
  }
  const [tip] = TOUCAN_BEAK_TIP.map((m) => bossPoint(...m));
  if (!tip) return;
  const forward = { pitch: QUARTER };
  hull.cylinder(1.9, 2.2, 8, H.dark, { at: offset(tip, 0, 0, -2.8), ...forward }, 1.6);
  neon.ring(2, 0.4, 8, TOUCAN_ORANGE, { at: offset(tip, 0, 0, -2.2), ...forward });
  charge.cylinder(1.3, 0.6, 8, WHITE, { at: offset(tip, 0, 0, -0.6), ...forward });
  muzzle(tip, 'laser');
}

/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED: Rgb = [1, 0.1, 0.12];
const STARBOARD_GREEN: Rgb = [0.2, 1, 0.35];

/** A pod's duct around its fan: an open lathe, wider at its lip (around the pod's centre). */
const DUCT = [
  [9.6, -1.5],
  [11.2, -0.5],
  [11.4, 3.5],
  [10.2, 5.2],
] as const;

/**
 * A wing pod around its centre `at` (P09-R09): a ducted fan, its lip ringed with neon, a gun
 * housing under its front with the two barrels of its fans, moss on its back.
 */
export function wingPod(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = Math.sign(at[0]);
  // P16-R05: the grafted fan duct grows out of a swollen flesh root at the wing's end.
  sac(p, offset(at, -s * 9, 1.5, -2), 5.5, F.crimson, 0.6);
  veinTo(p, [offset(at, -s * 12, 3.4, -2), offset(at, -s * 6, 4.4, 5)], [0, 1, 0], TOUCAN_ORANGE);
  hull.lathe(DUCT, 10, H.panel, { at, yaw: Math.PI / 10 }, false);
  hull.cylinder(9.6, 0.5, 10, H.dark, { at: offset(at, 0, 0.2, 0) });
  hull.cylinder(2.4, 3, 6, H.base, { at: offset(at, 0, 0.6, 0) });
  p.rotor(offset(at, 0, 3.2, 0), 8.6);
  neon.ring(11.5, 0.8, 10, TOUCAN_YELLOW, { at: offset(at, 0, 4, 0), yaw: Math.PI / 10 });
  moss(hull, offset(at, s * 8, 5.1, -7), 2.6, at[0]);
  lamps(neon, [offset(at, s * 11.6, 4.4, -2)], 1.4, s > 0 ? PORT_RED : STARBOARD_GREEN);
  hull.box([9, 3, 6], H.base, { at: offset(at, 0, 0.3, 9) }, H.panel);
  // The right pod (screen right) is on the model's -X side.
  const guns = s < 0 ? TOUCAN_POD_GUNS : mirror(TOUCAN_POD_GUNS);
  for (const tip of guns.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.cylinder(1.1, 5.6, 6, H.dark, { at: [x, y, z - 6.2], pitch: QUARTER });
    charge.cylinder(1.15, 0.6, 6, WHITE, { at: [x, y, z - 0.6], pitch: QUARTER });
    muzzle(tip);
  }
}
