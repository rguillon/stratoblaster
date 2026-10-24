import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import type { SolidBuilder } from '../../../render/geometry/solids';
import { ENEMY_CONFIG } from '../../config/enemies';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { around, radial, SIDES } from './enemy-shapes';

// P05-R06..R10: the bigger enemies. Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R06: a ring with four spokes, a pod at the end of each, and an orange neon core. */
export function buildSpinner(scene: Scene): EnemyModel {
  const podRadius = ENEMY_CONFIG.spinner.podRadius;
  return buildEnemyModel('spinner', scene, N.spinner, ({ hull, neon, charge }) => {
    const ring = [
      [10, -1.6],
      [12.5, -1.6],
      [12.5, 1.6],
      [10, 1.6],
      [10, -1.6],
    ] as const;
    hull.lathe(ring, 16, H.base, {}, false);
    for (const a of around(4)) {
      hull.box([1.8, 1.6, 8], H.panel, { at: radial(a, 6.5, -0.8), yaw: a });
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
  return buildEnemyModel('lancer', scene, N.lancer, ({ hull, neon, charge }) => {
    const needle = [
      [0, nose - 1],
      [2.6, 6],
      [3.2, -6],
      [2.2, -21],
      [-2.2, -21],
      [-3.2, -6],
      [-2.6, 6],
    ] as const;
    hull.slab(needle, [-1.4, 1.4], H.base, {}, H.panel);
    const spine = [
      [0, 12],
      [1, 4],
      [1, -16],
      [-1, -16],
      [-1, 4],
    ] as const;
    hull.slab(spine, [1.4, 2.4], H.dark);
    for (const s of SIDES) {
      const fin = [
        [s * 3, -5],
        [s * 10, -17],
        [s * 9.5, -20],
        [s * 2.5, -15],
      ] as const;
      hull.slab(fin, [-0.5, 0.5], H.base, {}, H.panel);
      neon.box([0.5, 0.4, 18], N.lancer, { at: [s * 1.4, 1.4, -4] });
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
  return buildEnemyModel('rocketeer', scene, N.rocketeer, ({ hull, neon, charge }) => {
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
    hull.slab(body, [-2.2, 2.4], H.base, {}, H.panel);
    const armour = [
      [0, 9],
      [4.5, 5],
      [4.5, -8],
      [-4.5, -8],
      [-4.5, 5],
    ] as const;
    hull.slab(armour, [2.4, 3.6], H.dark);
    for (const s of SIDES) {
      hull.box([7, 1.2, 6], H.dark, { at: [s * 12, -0.6, 0] });
      hull.cylinder(4, 22, 8, H.panel, { at: [s * pod, 0, -11], pitch: QUARTER });
      neon.box([1, 0.4, 12], N.rocketeer, { at: [s * pod, 3.9, -3] });
      charge.cylinder(2.6, 3.5, 8, WHITE, { at: [s * pod, 0, 11], pitch: QUARTER }, 0);
    }
  });
}

/** P05-R09: a heavy, wide hull covered with front armour plates and a blue neon visor slit. */
export function buildBulwark(scene: Scene): EnemyModel {
  return buildEnemyModel('bulwark', scene, N.bulwark, ({ hull, neon, charge }) => {
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
    hull.slab(body, [-3, 2.5], H.base, {}, H.panel);
    for (let k = -2; k <= 2; k++) {
      const at = [k * 10, 2.5, 8 - Math.abs(k) * 2.5] as [number, number, number];
      hull.box([9.5, 1.6, 7], H.panel, { at, yaw: -k * 0.12 }, H.base);
    }
    const tower = [
      [0, 4],
      [9, 0],
      [9, -12],
      [-9, -12],
      [-9, 0],
    ] as const;
    hull.slab(tower, [2.5, 5.5], H.dark, {}, H.base);
    neon.box([16, 0.8, 1.4], N.bulwark, { at: [0, 5.5, 1.2] });
    for (const s of SIDES) {
      hull.box([7, 3, 4], H.dark, { at: [s * 12, -1.5, -18] });
      neon.box([5, 1, 0.6], N.bulwark, { at: [s * 12, -0.5, -20.2] });
    }
    charge.box([3, 1, 2.4], WHITE, { at: [0, 2.5, 15.5] });
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
  return buildEnemyModel('splitter', scene, N.splitter, ({ hull, neon, charge }) => {
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
  });
}

/** P05-R10: a pod broken off a Splitter, diving nose first. */
export function buildSplitterPod(scene: Scene): EnemyModel {
  return buildEnemyModel('splitter-pod', scene, N.splitter, ({ hull, neon }) => {
    pod(hull, [0, 0, 0]);
    hull.cylinder(2.2, 4, 6, H.dark, { at: [0, 0, 3.5], pitch: QUARTER }, 0);
    neon.ring(4.6, 0.7, 6, N.splitter, { at: [0, -0.35, 0] });
  });
}
