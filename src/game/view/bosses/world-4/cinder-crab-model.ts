import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import { CINDER_CRAB, CRAB_DOME } from '../../../config/bosses/world-4/cinder-crab';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { vent } from '../mini-boss-greebles';
import { H, offset, SHADE, WHITE } from '../mini-boss-shapes';
import { blot, bolts, FORGE, moltenSeam, soot, strut } from './black-sands-kit';
import { claw, CRAB_LIMBS, CRAB_ORANGE as N, mortar } from './cinder-crab-parts';
import { backRibs, fleshShell, glands, magmaVein, MAGMA, reactorSacs, SKIN } from './living-forge';

// P10-R11, 4-1: the Cinder Crab. Logical pixels, nose +Z, Y up (towards the camera). A wide,
// low crab-ship: a soot-black carapace cracked by molten seams, orange neon along its rim and on
// its eye stalks, six short legs, arms reaching from under its front rim to the two claws, the
// ring dome on its back and the mortar behind it.
// P16-R05: a living crab, a scorched flesh shell banded in darker seams, bony legs, glowing eyes
// on fleshy stalks, metal grafted on as its belly plate, dome, joints and guns.
type Vec3 = [number, number, number];

/** The carapace (loft stations, tail to front: z, half width, bottom, top): wide and low. */
const CARAPACE = [
  [-32, 14, 1, 4],
  [-25, 32, -1, 8],
  [-12, 45, -2, 11],
  [2, 48, -2, 12],
  [14, 40, -1, 10],
  [20, 26, 0, 7.5],
  [24, 12, 1, 4],
] as const;
/** The legs either side: where along the carapace each hangs (z), and how it is bent. */
const LEGS = [9, -3, -15] as const;
const LEG = { hip: 3, knee: 9, out: 6, foot: 9, drop: -3 } as const;
/** The eye stalks at the front: across, along, and how tall. */
const EYES = { x: 6, z: 20, height: 13 } as const;
/** The ring dome on its back (a lathe profile around the dome's axis). */
const DOME = [
  [7, 0],
  [7, 1.4],
  [5.4, 3.2],
  [2.6, 4.2],
  [0, 4.4],
] as const;

/** Linear interpolation of station column `k` of the carapace at `z`. */
function stationAt(z: number, k: 1 | 3): number {
  for (let i = 1; i < CARAPACE.length; i++) {
    const [a, b] = [CARAPACE[i - 1], CARAPACE[i]];
    if (!a || !b || z > b[0]) continue;
    return a[k] + ((b[k] - a[k]) * (z - a[0])) / (b[0] - a[0]);
  }
  return CARAPACE.at(-1)?.[k] ?? 0;
}
/** The carapace's height at `z` (the top of its loft there), for things laid on it. */
export const topAt = (z: number): number => stationAt(z, 3);
/** The carapace's half width at `z`. */
const widthAt = (z: number): number => stationAt(z, 1);

/** The carapace, its orange neon flanks, the belly plate and the reactors. */
function drawCarapace(p: EnemyParts): void {
  const { hull, neon } = p;
  fleshShell(p.flesh, HULL_SECTION, CARAPACE, [SKIN.base, SKIN.dark]);
  for (const side of [1, 3]) {
    neon.loft(
      sideStripe(HULL_SECTION, side, [0.15, 0.4], 1.03),
      CARAPACE.slice(1, 6),
      N,
      {},
      { open: true },
    );
  }
  hull.box([44, 2.4, 40], H.dark, { at: [0, -3.4, -6] }, H.panel);
  reactorSacs(
    p,
    [
      [9, 2.5, -33],
      [-9, 2.5, -33],
    ],
    2.4,
    MAGMA,
  );
}

/** Its six short legs: each bends up at the knee and down to a pointed foot. */
function drawLegs({ flesh, neon }: EnemyParts): void {
  for (const s of SIDES) {
    for (const z of LEGS) {
      const w = widthAt(z);
      const hip: Vec3 = [s * (w - 6), LEG.hip, z];
      const knee: Vec3 = [s * (w + LEG.out), LEG.knee, z - 3];
      const foot: Vec3 = [s * (w + LEG.foot), LEG.drop, z - 7];
      strut(flesh, [hip, knee], [2.2, 1.8], SKIN.panel, 5);
      strut(flesh, [knee, foot], [1.8, 0.4], SKIN.bone, 4);
      neon.box([1, 0.6, 1], N, { at: offset(knee, 0, 1.6, 0) });
    }
  }
}

/** The front: two eye stalks with orange neon tips, a brow plate, the arms' shoulder sockets. */
function drawFront(p: EnemyParts): void {
  const { hull, neon, charge, flesh } = p;
  for (const s of SIDES) {
    const base: Vec3 = [s * EYES.x, topAt(EYES.z) - 0.5, EYES.z];
    flesh.cylinder(1.4, EYES.height - base[1], 5, SKIN.panel, { at: base }, 1);
    glands(p, [[s * EYES.x, EYES.height + 0.6, EYES.z + 0.6]], 1.4, N);
    neon.box([2.6, 1.6, 2.6], N, { at: [s * EYES.x, EYES.height, EYES.z] });
    hull.cylinder(4.5, 4, 7, H.dark, { at: [s * 16, -1, 14] }, 3.6);
  }
  hull.box([18, 1.4, 3], SHADE.edge, { at: [0, topAt(16), 16] });
  charge.box([8, 0.4, 1.6], WHITE, { at: [0, topAt(13) + 0.1, 13] });
}

/** P16-R05, P16-R06: its living flesh: veins, glands and ribs. */
function backFlesh(p: EnemyParts): void {
  backRibs(p, [-20, 1], { halfWidth: 30, y: 4, height: 6.5, thickness: 0.9 });
  magmaVein(
    p,
    [
      [-24, 7, -16],
      [-10, topAt(-6), -6],
      [10, topAt(-6), -6],
      [24, 7, -16],
    ],
    1.1,
  );
  glands(
    p,
    [
      [-26, 7.5, 3],
      [26, 7.5, 3],
    ],
    1.8,
    MAGMA,
  );
}

/** Its back: molten seams between the plates, soot, bolts, a hot vent and the ring dome. */
function drawBack(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  backFlesh(p);
  for (const z of [-11, 9]) {
    const y = topAt(z) + 0.05;
    const half = widthAt(z) * 0.55;
    moltenSeam(
      neon,
      [
        [-half, z],
        [-half * 0.5, z + 1.5],
        [0, z - 1],
        [half * 0.5, z + 1.2],
        [half, z - 0.5],
      ],
      y,
    );
  }
  soot(hull, blot([14, -4], 5, 0.8, 1), topAt(-4));
  soot(hull, blot([-17, 3], 4, 1.1, 3), topAt(3));
  soot(hull, blot([5, -19], 4.5, 0.7, 5), topAt(-19));
  bolts(
    hull,
    [-20, -12, 12, 20].map((x) => [x, 4] as const),
    topAt(4),
    1.2,
  );
  vent(hull, [-14, topAt(-17) + 0.05, -17], [8, 5], 3);
  charge.box([6, 0.3, 3.4], WHITE, { at: [-14, topAt(-17), -17] });
  neon.box([6.4, 0.25, 0.5], FORGE.ember, { at: [-14, topAt(-17) + 0.1, -14.7] });
  const [emitter] = CRAB_DOME;
  if (!emitter) return;
  const top = bossPoint(...emitter);
  const base: Vec3 = [top[0], topAt(top[2]) - 0.4, top[2]];
  const k = (top[1] - base[1] - 0.6) / (DOME.at(-1)?.[1] ?? 1);
  hull.lathe(
    DOME.map(([r, y]) => [r, y * k] as const),
    8,
    H.panel,
    { at: base },
  );
  neon.ring(7.2, 0.7, 8, N, { at: offset(base, 0, 0.5, 0) });
  charge.cylinder(1.6, 0.6, 6, WHITE, { at: offset(top, 0, -0.6, 0) }, 0.8);
  p.muzzle(top, 'ring');
}

/**
 * P10-R11: the Cinder Crab, a wide, low crab-ship 3 L across, orange neon: a soot-black
 * carapace cracked by molten seams on six short legs, eye stalks, two claws on swinging arms
 * whose outer fingers snap open and shut, the ring dome on its back and a mortar behind it.
 */
export function buildCinderCrab(scene: Scene): EnemyModel {
  return buildBossModel(CINDER_CRAB, scene, N, {
    core: (p) => {
      drawCarapace(p);
      drawLegs(p);
      drawFront(p);
      drawBack(p);
    },
    parts: {
      'claw-left': claw,
      'claw-right': claw,
      mortar: (p, at) => {
        mortar(p, at, topAt(at[2]) - 0.4);
      },
    },
    limbs: CRAB_LIMBS,
  });
}
