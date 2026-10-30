import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { carapace, curve, organ, tendril, vein } from '../../../render/geometry/organic';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { around, radial, SIDES } from './enemy-shapes';

// P05-R09, P05-R10, P16-R03: the Bulwark and the Splitter, Cyber-Organic (P16-R01). Logical
// pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R09: the Bulwark's armour band along the front of its shell, and the visor. */
const BULWARK_ARMOUR = [
  [0, 13],
  [12.5, 10.3],
  [23, 1],
  [19.5, -1],
  [10.5, 6.5],
  [0, 9],
  [-10.5, 6.5],
  [-19.5, -1],
  [-23, 1],
  [-12.5, 10.3],
] as const;
const BULWARK_VISOR = [
  [-7, 0.2],
  [0, 3.3],
  [7, 0.2],
  [7, -0.6],
  [0, 2.5],
  [-7, -0.6],
] as const;

/**
 * P05-R09, P16-R03: a heavy armoured beetle: a wide ridged carapace, a metal armour band across
 * its front with a blue neon visor slit, mandibles, short legs, twin cannon grafted on its head.
 */
export function buildBulwark(scene: Scene): EnemyModel {
  return buildEnemyModel(
    'bulwark',
    scene,
    N.bulwark,
    ({ flesh, hull, neon, charge, reactor, muzzle, vein: veins }) => {
      const shell = { tail: -17, nose: 15, segments: 2, width: 27, bottom: -3, top: 5.4 };
      carapace(flesh, shell, [F.teal, F.sinew]);
      hull.bevelSlab(BULWARK_ARMOUR, [2.5, 2.5, 3.9], [0, 1.1], H.panel, {}, H.base);
      neon.slab(BULWARK_VISOR, [5.1, 5.8], N.bulwark);
      vein(
        veins,
        [
          [0, 5.6, -2],
          [0, 5, -12],
          [0, 3.6, -16],
        ],
        1.2,
        N.bulwark,
      );
      for (const s of SIDES) {
        tendril(
          flesh,
          curve([s * 6, 0, 13], [s * 2, 0.5, 18], [s * 4, 0, 1], 2),
          [1.6, 0],
          3,
          F.bone,
        );
        for (const z of [4, -8]) {
          tendril(
            flesh,
            [
              [s * 22, -0.5, z],
              [s * 26.5, -1.5, z - 3],
            ],
            [1.3, 0.6],
            3,
            F.sinew,
          );
        }
        reactor([s * 12, -0.5, -20.5], 1.3);
        // The twin cannon on its head, over the armour (phase 7 review).
        hull.cylinder(0.9, 11, 5, H.dark, { at: [s * 3, 4.2, 2], pitch: QUARTER }, 0.75);
        charge.cylinder(0.95, 1, 5, WHITE, { at: [s * 3, 4.2, 13], pitch: QUARTER });
        muzzle([s * 3, 4.2, 14]);
      }
      reactor([0, 0, -17], 2.2);
    },
  );
}

/**
 * A Splitter pod: a wedge fitted around the core, `inner` to `outer` from the core's centre,
 * outwards along +Z, around its own centre `offset` out.
 */
function splitterPodOutline(offset: number, inner: number, outer: number): OutlinePoint[] {
  const rim = (a: number): OutlinePoint => [outer * Math.sin(a), outer * Math.cos(a) - offset];
  return [[-4, inner - offset], rim(-0.42), rim(-0.21), rim(0.21), rim(0.42), [4, inner - offset]];
}

/**
 * P16-R03: a pod of the Splitter, a curled flesh grub: a swollen body, a metal plate grafted
 * on its back, a neon seam along its inner side and a vein across it.
 */
function pod(
  flesh: SolidBuilder,
  hull: SolidBuilder,
  neon: SolidBuilder,
  veins: SolidBuilder,
  place: { at?: [number, number, number]; yaw?: number },
): void {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  const inner = 8.3;
  const body = splitterPodOutline(offset, inner, 16.4);
  flesh.bevelSlab(body, [-2.2, 0.4, 2.4], [0.8, 1.6], F.crimson, place, F.purple);
  hull.bevelSlab(splitterPodOutline(offset, 10.4, 14.4), [2.2, 2.2, 3], [0, 0.6], H.panel, place);
  const z0 = inner - offset - 0.45;
  const seam = [
    [-4.3, z0],
    [4.3, z0],
    [4.3, z0 + 0.4],
    [-4.3, z0 + 0.4],
  ] as const;
  neon.slab(seam, [-1.6, 1.8], N.splitter, place);
  const z = 15.6 - offset;
  vein(
    veins,
    [
      [-5, 2.4, z - 1],
      [0, 2.6, z],
      [5, 2.4, z - 1],
    ],
    0.8,
    N.splitter,
    place,
  );
}

/**
 * P05-R10, P16-R03: a body visibly made of the three grubs it splits into, curled around a
 * small flesh heart with a purple neon ring, its eye charging before it fires.
 */
export function buildSplitter(scene: Scene): EnemyModel {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  return buildEnemyModel('splitter', scene, N.splitter, (p) => {
    const { flesh, hull, neon, charge, reactor, muzzle } = p;
    organ(flesh, 8.6, 6, F.purple, { at: [0, -3, 0] }, 0.4);
    neon.ring(8.4, 0.7, 6, N.splitter, { at: [0, 0.6, 0] });
    for (const a of around(3)) pod(flesh, hull, neon, p.vein, { at: radial(a, offset, 0), yaw: a });
    const eye = [
      [0, 0],
      [2.2, 0.4],
      [0, 1.4],
    ] as const;
    charge.lathe(eye, 6, WHITE, { at: [0, 4, 0] });
    muzzle([0, 5.4, 0]);
    reactor([0, 0, -7.8], 1.6);
  });
}

/** P05-R10, P16-R03: a grub broken off a Splitter, diving outer side first. */
export function buildSplitterPod(scene: Scene): EnemyModel {
  const { podOffset } = ENEMY_CONFIG.splitter;
  return buildEnemyModel('splitter-pod', scene, N.splitter, (p) => {
    pod(p.flesh, p.hull, p.neon, p.vein, {});
    p.reactor([0, 0, 8.3 - podOffset], 1);
  });
}
