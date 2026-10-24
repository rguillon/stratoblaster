import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { around, flipX, radial, shiftX, SIDES } from './enemy-shapes';

// P05-R01..R05: the lighter enemies. Logical pixels, nose +Z, Y up (towards the camera).
const H = ENEMY_LOOK.hull;
const N = ENEMY_LOOK.neon;
const WHITE = [1, 1, 1] as const;

/** P05-R01: a small flat disc with three short fins at 120° and a neon ring around its rim. */
export function buildGnat(scene: Scene): EnemyModel {
  return buildEnemyModel('gnat', scene, N.gnat, ({ hull, neon }) => {
    const profile = [
      [0, -1.5],
      [5.5, -1.2],
      [6.5, 0],
      [5.5, 1.2],
      [3, 1.8],
      [0, 2.6],
    ] as const;
    hull.lathe(profile, 8, H.base);
    for (const a of around(3)) {
      hull.box([1.6, 1.2, 3.4], H.panel, { at: radial(a, 7, -0.6), yaw: a });
    }
    neon.ring(6.7, 0.7, 12, N.gnat, { at: [0, -0.35, 0] });
  });
}

/** P05-R02: an arrow head with sharply swept wings and a single red neon eye at the nose. */
export function buildHornet(scene: Scene): EnemyModel {
  return buildEnemyModel('hornet', scene, N.hornet, ({ hull, neon }) => {
    const body = [
      [0, 12],
      [2.6, 1],
      [1.8, -9],
      [-1.8, -9],
      [-2.6, 1],
    ] as const;
    hull.slab(body, [-1.2, 1.6], H.base, {}, H.panel);
    const wing = [
      [2, 3],
      [11.5, -11],
      [8, -11],
      [1.8, -6],
    ] as const;
    hull.slab(wing, [-0.6, 0.4], H.base, {}, H.panel);
    hull.slab(flipX(wing), [-0.6, 0.4], H.base, {}, H.panel);
    const ridge = [
      [0, 7],
      [1.2, 2],
      [0, -6],
      [-1.2, 2],
    ] as const;
    hull.slab(ridge, [1.6, 2.4], H.dark);
    neon.lathe(
      [
        [0, -0.9],
        [1.4, 0],
        [0, 0.9],
      ],
      6,
      N.hornet,
      { at: [0, 1.8, 8.5] },
    );
  });
}

/** P05-R03: a small delta wing with twin tail booms and a cyan neon strip along each boom. */
export function buildScout(scene: Scene): EnemyModel {
  return buildEnemyModel('scout', scene, N.scout, ({ hull, neon, charge }) => {
    const delta = [
      [0, 12],
      [13, -8],
      [11, -9],
      [-11, -9],
      [-13, -8],
    ] as const;
    hull.slab(delta, [-0.8, 0.8], H.base, {}, H.panel);
    const cockpit = [
      [0, 9],
      [2.2, 2],
      [1.8, -5],
      [-1.8, -5],
      [-2.2, 2],
    ] as const;
    hull.slab(cockpit, [0.8, 2.4], H.dark);
    for (const s of SIDES) {
      hull.box([2.4, 2.6, 13], H.base, { at: [s * 7, -1, -8.5] }, H.panel);
      neon.box([0.8, 0.5, 10], N.scout, { at: [s * 7, 1.6, -8.5] });
    }
    // Its gun, under the nose, glows as the next shot comes.
    charge.box([1.2, 1, 1.6], WHITE, { at: [0, -0.5, 11.5] });
  });
}

/** P05-R04: a wide, flat flying wing with a row of magenta neon lights along the leading edge. */
export function buildStrafer(scene: Scene): EnemyModel {
  return buildEnemyModel('strafer', scene, N.strafer, ({ hull, neon }) => {
    const wing = [
      [0, 8],
      [20.5, -1.5],
      [20.5, -5],
      [6, -3.5],
      [0, -6],
      [-6, -3.5],
      [-20.5, -5],
      [-20.5, -1.5],
    ] as const;
    hull.slab(wing, [-1, 1], H.base, {}, H.panel);
    const hump = [
      [0, 6],
      [4, 0],
      [3, -5],
      [-3, -5],
      [-4, 0],
    ] as const;
    hull.slab(hump, [1, 2.6], H.dark);
    for (const s of SIDES) {
      for (let k = 1; k <= 5; k++) {
        const t = k / 6;
        neon.box([1.6, 0.6, 1.2], N.strafer, { at: [s * 20.5 * t, 1, 8 - 9.5 * t - 0.8] });
      }
    }
  });
}

/** P05-R05: a twin-hull catamaran, the two hulls joined by a glowing green neon bar. */
export function buildWeaver(scene: Scene): EnemyModel {
  return buildEnemyModel('weaver', scene, N.weaver, ({ hull, neon, charge }) => {
    const hullOutline = [
      [0, 15.5],
      [2.6, 9],
      [2.6, -12],
      [0, -15.5],
      [-2.6, -12],
      [-2.6, 9],
    ] as const;
    const canopy = [
      [0, 11],
      [1.3, 6],
      [1.3, 0],
      [-1.3, 0],
      [-1.3, 6],
    ] as const;
    for (const s of SIDES) {
      hull.slab(shiftX(hullOutline, s * 10), [-1.5, 1.5], H.base, {}, H.panel);
      hull.slab(shiftX(canopy, s * 10), [1.5, 2.5], H.dark);
      charge.box([1, 1, 1.6], WHITE, { at: [s * 10, -0.5, 15] });
    }
    hull.box([16, 1.4, 4], H.dark, { at: [0, -0.7, -1] });
    neon.box([15, 0.9, 2.2], N.weaver, { at: [0, 0.7, -1] });
  });
}
