import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_CONFIG, VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { SegmentedBody } from '../../../render/geometry/organic';
import {
  carapace,
  curve,
  organ,
  segmentedBody,
  vein as veinTube,
} from '../../../render/geometry/organic';
import { buildEnemyModel } from './enemy-mesh';
import type { EnemyParts } from './enemy-mesh';
import { flipX, SIDES } from './enemy-shapes';
import { eyes, reactorSac } from './organic-parts';

// P05-R15, P05-R18, P16-R04: the heavier veteran kinds. Logical pixels, nose +Z, Y up (to the camera).
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** P05-R15, P16-R04: the Mortar's squat, ridged shell, wider than long (tail to front). */
const MORTAR_SHELL: SegmentedBody = {
  tail: -14,
  nose: 12,
  segments: 3,
  width: 17.5,
  bottom: -2.2,
  top: 3.4,
  girth: (t) => 0.55 + 0.45 * Math.sin(Math.PI * t),
  closed: [false, false],
};
/** The armour plates grafted on its front shoulders (right side). */
const MORTAR_PLATE = [
  [6, 11],
  [12, 8],
  [12.5, 4],
  [7, 6],
] as const;

/** A side sac on side `s`, swollen with shells, a running light along it. */
function mortarSac({ flesh, neon, vein }: EnemyParts, s: 1 | -1): void {
  organ(flesh, 3, 6, F.crimson, { at: [s * 18, 0.6, -9], pitch: QUARTER }, 0.95);
  neon.box([0.8, 0.3, 4], N.mortar, { at: [s * 18.2, 3.6, -4] });
  veinTube(vein, curve([s * 15.5, 3, -4], [s * 8, 4.2, -2], [0, 1, 1.5], 2), 0.6, N.mortar);
}

/**
 * P05-R15, P16-R04: a squat, armoured beetle with a short, wide barrel grafted on a raised mount
 * in its middle, shell sacs on its flanks and olive-green neon. The barrel's mouth glows as the
 * next shell charges.
 */
export function buildMortar(scene: Scene): EnemyModel {
  const [, mouthY, mouthHeight] = VETERAN_CONFIG.mortar.muzzles[0];
  const mouth = -mouthY;
  return buildEnemyModel('mortar', scene, N.mortar, (p) => {
    const { hull, flesh, neon, charge, muzzle } = p;
    carapace(flesh, MORTAR_SHELL, [F.sinew, F.crimson]);
    // The raised mount: a squat drum, a cradle on it, then the barrel.
    hull.cylinder(7, 3, 8, H.panel, { at: [0, 2.4, 0] }, 6);
    hull.box([6, 2.6, 9], H.dark, { at: [0, 5.4, 1.5] });
    neon.ring(6.6, 0.5, 8, N.mortar, { at: [0, 3.6, 0] });
    hull.cylinder(2.6, mouth - 4.3, 8, H.dark, { at: [0, mouthHeight, 4], pitch: QUARTER }, 2.4);
    hull.ring(2.9, 1.5, 8, H.panel, { at: [0, mouthHeight, mouth - 3], pitch: QUARTER });
    charge.ring(2, 0.3, 8, WHITE, { at: [0, mouthHeight, mouth - 0.3], pitch: QUARTER });
    muzzle([0, mouthHeight, mouth]);
    eyes(p, [0, 1.6, 11.4], { count: 2, size: 0.6, spacing: 3 }, N.mortar);
    for (const s of SIDES) {
      reactorSac(p, [s * 8, 0, -14], 1.6, N.mortar, { veinLength: 4 });
      hull.bevelSlab(
        s === 1 ? MORTAR_PLATE : flipX(MORTAR_PLATE),
        [2, 2.6, 3.6],
        [0, 0.4],
        H.panel,
      );
      mortarSac(p, s);
    }
  });
}

/** P05-R18, P16-R04: the Minelayer's long, flat, segmented body, tail to nose. */
const MINELAYER_BODY: SegmentedBody = {
  tail: -21,
  nose: 22,
  segments: 4,
  width: 6.8,
  bottom: -1.8,
  top: 2.5,
  pinch: 0.2,
  girth: (t) => 0.6 + 0.4 * Math.sin(Math.PI * t),
};
/** A mine's egg, a lathe profile bottom to top. */
const MINE = [
  [0, -1.6],
  [1.6, -0.8],
  [1.6, 0.8],
  [0, 1.6],
] as const;
/** Its tail fins (right side). */
const MINELAYER_FIN = [
  [5, -12],
  [9.8, -17],
  [9.8, -20.5],
  [4.5, -18.5],
] as const;

/**
 * P05-R18, P16-R04: a long, flat, segmented grub with a rack of egg-mines along its belly (each
 * lit as the next drop charges), metal tail fins and red-orange neon running lights.
 */
export function buildMinelayer(scene: Scene): EnemyModel {
  const hatches = VETERAN_CONFIG.minelayer.muzzles;
  return buildEnemyModel('minelayer', scene, N.minelayer, (p) => {
    const { hull, flesh, neon, charge, vein, muzzle } = p;
    segmentedBody(flesh, MINELAYER_BODY, F.purple);
    // The egg rack along its belly, a metal graft.
    hull.box([4, 1, 26], H.dark, { at: [0, -2.6, 0] });
    for (const [, y, height] of hatches) {
      // An egg-mine hanging from the rack, its cap a charge light.
      flesh.lathe(MINE, 6, F.membrane, { at: [0, height, -y] });
      neon.ring(1.65, 0.4, 6, N.minelayer, { at: [0, height - 0.2, -y] });
      muzzle([0, height, -y]);
      // The hatch's glands on the back, lit as the next drop charges.
      for (const s of SIDES) charge.box([1.2, 0.3, 1.6], WHITE, { at: [s * 2.2, 2.6, -y] });
    }
    veinTube(vein, curve([0, 2.6, -18], [0, 2.6, 17], [0, 0.4, 0], 2), 0.8, N.minelayer);
    neon.box([0.8, 0.25, 6], N.minelayer, { at: [0, 2.2, 18] });
    eyes(p, [0, 1.4, 19.5], { count: 2, size: 0.6, spacing: 2.4 }, N.minelayer);
    for (const s of SIDES) {
      for (const z of [-14, -4, 6]) {
        neon.box([0.8, 0.4, 2.2], N.minelayer, { at: [s * 5.4, 1.4, z] });
      }
      const fin = s === 1 ? MINELAYER_FIN : flipX(MINELAYER_FIN);
      hull.bevelSlab(fin, [-0.5, 0, 0.6], [0.3, 0.5], H.base, {}, H.panel);
      reactorSac(p, [s * 2.4, 0.2, -21], 1.3, N.minelayer, { flesh: F.purple });
    }
  });
}
