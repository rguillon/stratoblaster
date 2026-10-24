import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { around, CANOPY_SECTION, HULL_SECTION, POD_SECTION, radial, SIDES } from './enemy-shapes';

// P05-R06..R10: the bigger enemies. Logical pixels, nose +Z, Y up (towards the camera).
// Fuselages are lofts, plates and wings bevelled slabs (phase 5 review: no more stacked boxes).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R06: a ring with four spokes, a pod at the end of each, and an orange neon core. */
export function buildSpinner(scene: Scene): EnemyModel {
  const podRadius = ENEMY_CONFIG.spinner.podRadius;
  return buildEnemyModel('spinner', scene, N.spinner, ({ hull, neon, charge }) => {
    const ring = [
      [10.2, -1.2],
      [11.8, -1.6],
      [12.6, 0],
      [11.8, 1.6],
      [10.2, 1.2],
      [10.2, -1.2],
    ] as const;
    hull.lathe(ring, 12, H.base, {}, false);
    const spoke = [
      [-1.3, -4],
      [1.3, -4],
      [0.7, 4.5],
      [-0.7, 4.5],
    ] as const;
    for (const a of around(4)) {
      hull.bevelSlab(spoke, [-0.8, 0, 0.8], [0.3, 0.5], H.panel, { at: radial(a, 6.5, 0), yaw: a });
      const pod = [
        [0, -2],
        [2.8, -1.2],
        [2.8, 1.2],
        [0, 2.2],
      ] as const;
      hull.lathe(pod, 6, H.panel, { at: radial(a, podRadius, 0) });
      // The pods' muzzles light up while it fires.
      charge.ring(2.9, 0.7, 6, WHITE, { at: radial(a, podRadius, -0.35) });
    }
    const core = [
      [0, -1.5],
      [3.2, -0.8],
      [3.2, 0.8],
      [0, 2],
    ] as const;
    neon.lathe(core, 8, N.spinner);
  });
}

/** P05-R07: a long needle hull with a glowing emitter at the nose and two small side fins. */
export function buildLancer(scene: Scene): EnemyModel {
  const nose = ENEMY_CONFIG.lancer.emitterOffset;
  return buildEnemyModel('lancer', scene, N.lancer, ({ hull, neon, charge, reactor }) => {
    hull.loft(
      HULL_SECTION,
      [
        [-21, 2.3, -1.3, 1.2],
        [-6, 3.2, -1.5, 1.5],
        [6, 2.6, -1.3, 1.3],
        [nose - 4, 1.2, -0.6, 0.6],
        [nose - 1, 0, 0, 0],
      ],
      H.base,
    );
    reactor([0, 0, -21], 1.6);
    hull.loft(
      CANOPY_SECTION,
      [
        [-17, 0, 1.2, 1.2],
        [-12, 1, 1.4, 2.4],
        [4, 1, 1.3, 2.3],
        [13, 0, 0.8, 0.8],
      ],
      H.dark,
      {},
      true,
    );
    for (const s of SIDES) {
      const fin = [
        [s * 3, -5],
        [s * 10, -17],
        [s * 9.5, -20],
        [s * 2.5, -15],
      ] as const;
      hull.bevelSlab(fin, [-0.5, 0, 0.5], [0.3, 0.5], H.base, {}, H.panel);
      neon.box([0.5, 0.4, 16], N.lancer, { at: [s * 1.8, 1.25, -4] });
      reactor([s * 6.5, 0, -17.8], 0.9);
    }
    const emitter = [
      [0, -1.4],
      [1.8, 0],
      [0, 1.4],
    ] as const;
    // Brightens through the warning (its `charge`), full while the laser fires.
    charge.lathe(emitter, 6, WHITE, { at: [0, 0, nose] });
  });
}

/** P05-R08: a bulky hull with a missile pod on each side; the missile tips glow when loaded. */
export function buildRocketeer(scene: Scene): EnemyModel {
  const pod = ENEMY_CONFIG.rocketeer.podOffset;
  return buildEnemyModel('rocketeer', scene, N.rocketeer, ({ hull, neon, charge, reactor }) => {
    const body = [
      [0, 14],
      [7, 10],
      [9, 0],
      [8, -12],
      [4, -15],
      [-4, -15],
      [-8, -12],
      [-9, 0],
      [-7, 10],
    ] as const;
    hull.bevelSlab(body, [-2.2, 0, 2.4], [1.4, 2], H.base, {}, H.panel);
    const armour = [
      [0, 9],
      [4.5, 5],
      [4.5, -8],
      [-4.5, -8],
      [-4.5, 5],
    ] as const;
    hull.bevelSlab(armour, [2.4, 2.4, 3.6], [0, 1], H.dark);
    const pylon = [
      [-3.5, 3],
      [3.5, 1.5],
      [3.5, -3],
      [-3.5, -3],
    ] as const;
    const missile = [
      [2.6, 0],
      [4, 2.5],
      [4, 18.5],
      [3.3, 22],
    ] as const;
    for (const s of SIDES) {
      hull.bevelSlab(pylon, [-0.6, -0.2, 0.6], [0.3, 0.5], H.dark, { at: [s * 12, 0, 0] });
      hull.lathe(missile, 8, H.panel, { at: [s * pod, 0, -11], pitch: QUARTER });
      neon.box([1, 0.4, 12], N.rocketeer, { at: [s * pod, 3.9, -3] });
      charge.cylinder(2.6, 3.5, 8, WHITE, { at: [s * pod, 0, 11], pitch: QUARTER }, 0);
      reactor([s * 2.4, 0, -15], 1.6);
    }
  });
}

/** P05-R09: the Bulwark's front armour plates, its tower and its visor slit. */
const BULWARK_PLATE = [
  [-4.75, -3.5],
  [4.75, -3.5],
  [4.75, 3.5],
  [-4.75, 3.5],
] as const;
const BULWARK_TOWER = [
  [0, 4],
  [9, 0],
  [9, -12],
  [-9, -12],
  [-9, 0],
] as const;
/** Follows the tower's sloped front, just below its top. */
const BULWARK_VISOR = [
  [-7, 0.2],
  [0, 3.3],
  [7, 0.2],
  [7, -0.6],
  [0, 2.5],
  [-7, -0.6],
] as const;

/** P05-R09: a heavy, wide hull covered with front armour plates and a blue neon visor slit. */
export function buildBulwark(scene: Scene): EnemyModel {
  return buildEnemyModel('bulwark', scene, N.bulwark, ({ hull, neon, charge, reactor }) => {
    const body = [
      [0, 16],
      [14, 13],
      [27, 2],
      [27, -8],
      [18, -17],
      [-18, -17],
      [-27, -8],
      [-27, 2],
      [-14, 13],
    ] as const;
    hull.bevelSlab(body, [-3, -0.6, 2.5], [2, 2.5], H.base, {}, H.panel);
    for (let k = -2; k <= 2; k++) {
      const at = [k * 10, 0, 8 - Math.abs(k) * 2.5] as [number, number, number];
      // Sloped armour: the plates' tops lean back from their edges.
      hull.bevelSlab(
        BULWARK_PLATE,
        [2.5, 2.5, 4.1],
        [0, 1.4],
        H.panel,
        { at, yaw: -k * 0.12 },
        H.base,
      );
    }
    hull.bevelSlab(BULWARK_TOWER, [2.5, 2.5, 5.5], [0, 1.6], H.dark, {}, H.base);
    neon.slab(BULWARK_VISOR, [3.9, 5], N.bulwark);
    for (const s of SIDES) {
      hull.loft(
        POD_SECTION,
        [
          [-20, 3, -1.7, 1.7],
          [-16, 3.4, -2, 2],
          [-11, 2, -1.2, 1.2],
        ],
        H.dark,
        { at: [s * 12, 0, 0] },
      );
      reactor([s * 12, 0, -20], 1.3);
    }
    charge.box([3, 1, 2.4], WHITE, { at: [0, 2.5, 15.5] });
    reactor([0, 0, -17], 2.2);
  });
}

/** The pod of a Splitter: a small hexagonal pod with a purple neon rim. */
function pod(hull: SolidBuilder, at: [number, number, number]): void {
  const profile = [
    [0, -2.6],
    [4.5, -2],
    [4.5, 2],
    [0, 2.8],
  ] as const;
  hull.lathe(profile, 6, H.panel, { at });
}

/** P05-R10: a hexagonal core with three pods around it, purple neon seams in between. */
export function buildSplitter(scene: Scene): EnemyModel {
  const offset = ENEMY_CONFIG.splitter.podOffset;
  return buildEnemyModel('splitter', scene, N.splitter, ({ hull, neon, charge, reactor }) => {
    const core = [
      [0, -3],
      [9, -2.5],
      [9, 2.5],
      [6, 3.5],
      [0, 4],
    ] as const;
    hull.lathe(core, 6, H.base);
    neon.ring(9.1, 0.7, 6, N.splitter, { at: [0, 1, 0] });
    for (const a of around(3)) {
      pod(hull, radial(a, offset, 0));
      neon.box([1, 0.8, 4.4], N.splitter, { at: radial(a, 10.6, 1.4), yaw: a });
    }
    const eye = [
      [0, 0],
      [2.2, 0.4],
      [0, 1.4],
    ] as const;
    charge.lathe(eye, 6, WHITE, { at: [0, 4, 0] });
    reactor([0, 0, -7.8], 1.6);
  });
}

/** P05-R10: a pod broken off a Splitter, diving nose first. */
export function buildSplitterPod(scene: Scene): EnemyModel {
  return buildEnemyModel('splitter-pod', scene, N.splitter, ({ hull, neon, reactor }) => {
    pod(hull, [0, 0, 0]);
    hull.cylinder(2.2, 4, 6, H.dark, { at: [0, 0, 3.5], pitch: QUARTER }, 0);
    neon.ring(4.6, 0.7, 6, N.splitter, { at: [0, -0.35, 0] });
    reactor([0, 0, -3.9], 1);
  });
}
