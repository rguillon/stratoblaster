import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_CONFIG, VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel } from './enemy-mesh';
import { decal, flipX, HULL_SECTION, SIDES } from './enemy-shapes';

// P05-R15, P05-R18: the heavier veteran kinds. Logical pixels, nose +Z, Y up (to the camera).
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R15: the Mortar's squat hull, wider than long. */
const MORTAR_HULL = [
  [0, 12],
  [11, 10.5],
  [20, 4],
  [20, -7],
  [13, -14],
  [-13, -14],
  [-20, -7],
  [-20, 4],
  [-11, 10.5],
] as const;
/** Its olive neon bands, painted on the hull's top on either side of the mount (right side). */
const MORTAR_BANDS = [
  [
    [9, 7],
    [15, 3],
    [15, 1.6],
    [9, 5.6],
  ],
  [
    [9, -2],
    [16, -2],
    [16, -3.4],
    [9, -3.4],
  ],
] as const;

/**
 * P05-R15: a squat gunship with a short, wide barrel on a raised mount in its middle, and
 * olive-green neon bands. The barrel's mouth glows as the next shell charges.
 */
export function buildMortar(scene: Scene): EnemyModel {
  const [, mouthY, mouthHeight] = VETERAN_CONFIG.mortar.muzzles[0];
  const mouth = -mouthY;
  return buildEnemyModel('mortar', scene, N.mortar, ({ hull, neon, charge, reactor, muzzle }) => {
    hull.bevelSlab(MORTAR_HULL, [-2.2, 0, 2.4], [1.4, 2], H.base, {}, H.panel);
    // The raised mount: a squat drum, a cradle on it, then the barrel.
    hull.cylinder(7, 3, 8, H.panel, { at: [0, 2.4, 0] }, 6);
    hull.box([6, 2.6, 9], H.dark, { at: [0, 5.4, 1.5] });
    neon.ring(6.6, 0.5, 8, N.mortar, { at: [0, 3.6, 0] });
    hull.cylinder(2.6, mouth - 4.3, 8, H.dark, { at: [0, mouthHeight, 4], pitch: QUARTER }, 2.4);
    hull.ring(2.9, 1.5, 8, H.panel, { at: [0, mouthHeight, mouth - 3], pitch: QUARTER });
    charge.ring(2, 0.3, 8, WHITE, { at: [0, mouthHeight, mouth - 0.3], pitch: QUARTER });
    muzzle([0, mouthHeight, mouth]);
    for (const band of MORTAR_BANDS) {
      for (const outline of [band, flipX(band)]) decal(neon, outline, 2.45, N.mortar);
    }
    for (const s of SIDES) {
      reactor([s * 8, 0, -14], 1.6);
      // Side sponsons with a running light each.
      hull.bevelSlab(
        [
          [s * 17, 2],
          [s * 21, -1],
          [s * 21, -7],
          [s * 17, -9],
        ],
        [-1.6, 0, 1.6],
        [0.4, 0.8],
        H.panel,
      );
      neon.box([0.8, 0.3, 4], N.mortar, { at: [s * 19.4, 1.6, -4] });
    }
  });
}

/** P05-R18: the Minelayer's long, flat hull, tail to nose. */
const MINELAYER_HULL = [
  [-21, 4.5, -1.4, 1.5],
  [-14, 6.2, -1.8, 2.2],
  [0, 6.8, -1.8, 2.5],
  [12, 5.8, -1.6, 2.1],
  [18.5, 3.4, -1.2, 1.4],
  [22, 0, 0, 0],
] as const;
/** Its tail fins (right side). */
const MINELAYER_FIN = [
  [5, -12],
  [9.8, -17],
  [9.8, -20.5],
  [4.5, -18.5],
] as const;

/**
 * P05-R18: a long, flat hull with a rack of mines along its belly (each lit as the next drop
 * charges) and red-orange neon running lights.
 */
export function buildMinelayer(scene: Scene): EnemyModel {
  const hatches = VETERAN_CONFIG.minelayer.muzzles;
  return buildEnemyModel('minelayer', scene, N.minelayer, (p) => {
    const { hull, neon, charge, reactor, muzzle } = p;
    hull.loft(HULL_SECTION, MINELAYER_HULL, H.base);
    hull.box([4, 1, 26], H.dark, { at: [0, -2.6, 0] });
    for (const [, y, height] of hatches) {
      // A mine hanging from the rack, its cap a charge light.
      hull.lathe(
        [
          [0, -1.6],
          [1.6, -0.8],
          [1.6, 0.8],
          [0, 1.6],
        ],
        6,
        H.panel,
        { at: [0, height, -y] },
      );
      neon.ring(1.65, 0.4, 6, N.minelayer, { at: [0, height - 0.2, -y] });
      muzzle([0, height, -y]);
      // The hatch's lights on the back, lit as the next drop charges.
      for (const s of SIDES) charge.box([1.2, 0.3, 1.6], WHITE, { at: [s * 2.2, 2.4, -y] });
    }
    neon.box([0.8, 0.25, 24], N.minelayer, { at: [0, 2.45, -2] });
    for (const s of SIDES) {
      for (const z of [-14, -4, 6]) {
        neon.box([0.8, 0.4, 2.2], N.minelayer, { at: [s * 4.6, 1.95, z] });
      }
      const fin = s === 1 ? MINELAYER_FIN : flipX(MINELAYER_FIN);
      hull.bevelSlab(fin, [-0.5, 0, 0.6], [0.3, 0.5], H.base, {}, H.panel);
      reactor([s * 2.4, 0.2, -21], 1.3);
    }
  });
}
