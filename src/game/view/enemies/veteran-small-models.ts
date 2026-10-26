import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { SectionPoint } from '../../../render/geometry/solids';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { Phantom } from '../../sim/enemies/phantom';
import { buildEnemyModel } from './enemy-mesh';
import { flipX, POD_SECTION, SIDES } from './enemy-shapes';
import { backBand, edgeStrip, noseGun } from './veteran-shapes';

// P05-R14, P05-R17: the lighter veteran kinds. Logical pixels, nose +Z, Y up (to the camera).
const H = ENEMY_LOOK.hull;
const QUARTER = Math.PI / 2;

/** P05-R14: the Wasp's narrow abdomen, its waist, and its thorax and head. */
const WASP_ABDOMEN = [
  [-9, 0.5, 0, 0.6],
  [-7.5, 1.7, -0.6, 1.3],
  [-5, 2.4, -0.9, 1.8],
  [-2.5, 2, -0.8, 1.5],
  [-0.8, 0.8, -0.3, 0.6],
] as const;
const WASP_THORAX = [
  [-1.2, 0.9, -0.3, 0.8],
  [1, 2.2, -0.9, 1.7],
  [4, 2.3, -0.9, 1.8],
  [6, 1.3, -0.5, 1.1],
  [7.5, 1.9, -0.6, 1.5],
  [9.5, 1.2, -0.4, 1],
  [10.2, 0, 0.3, 0.3],
] as const;
/** Its two pairs of thin swept wings (right side), the front pair the bigger. */
const WASP_WINGS = [
  [
    [1.2, 4.5],
    [9.6, 0.4],
    [9.3, -0.9],
    [1.2, 2.4],
  ],
  [
    [1.2, 2],
    [7.4, -3.2],
    [6.8, -4.2],
    [1.2, 0.6],
  ],
] as const;

/**
 * P05-R14: a small, wasp-like dart: a narrow abdomen striped with yellow neon bands, two pairs
 * of thin swept wings, a yellow neon sting, and a gun between its mandibles.
 */
export function buildWasp(scene: Scene): EnemyModel {
  return buildEnemyModel('wasp', scene, N.wasp, (p) => {
    const { hull, neon, reactor } = p;
    hull.loft(POD_SECTION, WASP_ABDOMEN, H.base);
    hull.loft(POD_SECTION, WASP_THORAX, H.panel);
    for (const band of [
      [-7.2, -6.4],
      [-5.4, -4.6],
      [-3.6, -2.8],
    ] as const) {
      backBand(neon, WASP_ABDOMEN, band, N.wasp);
    }
    for (const wing of WASP_WINGS) {
      for (const outline of [wing, flipX(wing)])
        hull.slab(outline, [1.3, 1.6], H.dark, {}, H.panel);
    }
    // The sting, out of the tail.
    neon.cylinder(0.45, 2, 6, N.wasp, { at: [0, 0.3, -8.8], pitch: -QUARTER }, 0);
    for (const s of SIDES) {
      neon.box([0.9, 0.6, 1.2], N.wasp, { at: [s * 1.1, 1.1, 8.3] });
      reactor([s * 2.6, 0.2, 0.6], 0.6);
    }
    noseGun(p, [0, 0.8, 7.6], 2, 0.45);
  });
}

/** P05-R17: the Phantom's flying wing, seen from above (nose +Z). */
const PHANTOM_WING = [
  [0, 14],
  [17, -6],
  [16, -9],
  [8, -6],
  [0, -11],
  [-8, -6],
  [-16, -9],
  [-17, -6],
] as const;
/** Its faceted body, a low diamond, blended into the wing. */
const PHANTOM_SECTION: readonly SectionPoint[] = [
  [0.3, 0],
  [1, 0.35],
  [0.35, 1],
  [-0.35, 1],
  [-1, 0.35],
  [-0.3, 0],
];
const PHANTOM_BODY = [
  [-10, 4, -1, 1.4],
  [-3, 6, -1.2, 2.4],
  [5, 4, -1, 2],
  [11, 1.6, -0.5, 0.8],
  [13.5, 0, 0, 0],
] as const;

/** The wing's edges lit in neon: from the nose to each tip, and across each tip. */
function phantomEdges(): OutlinePoint[][] {
  const [nose, tip, tail] = [PHANTOM_WING[0], PHANTOM_WING[1], PHANTOM_WING[2]];
  return [edgeStrip(nose, tip, 0.6), edgeStrip(tip, tail, 0.6)].flatMap((strip) => [
    strip,
    flipX(strip),
  ]);
}

/**
 * P05-R17: a sleek flying wing with a faceted hull and pale violet neon edges. It fades out and
 * in with the Phantom: every mesh is as visible as the Phantom is (`Phantom.opacity`).
 */
export function buildPhantom(scene: Scene): EnemyModel {
  const model = buildEnemyModel('phantom', scene, N.phantom, (p) => {
    const { hull, neon, reactor } = p;
    hull.bevelSlab(PHANTOM_WING, [-0.8, 0, 1], [0.8, 1.6], H.base, {}, H.panel);
    hull.loft(PHANTOM_SECTION, PHANTOM_BODY, H.panel);
    for (const strip of phantomEdges()) neon.slab(strip, [-0.15, 0.3], N.phantom);
    for (const s of SIDES) {
      neon.box([0.5, 0.25, 5], N.phantom, { at: [s * 2.2, 2.3, -1] });
      reactor([s * 2.4, 0.2, -10], 1.2);
    }
    noseGun(p, [0, 0.6, 8], 5.8);
  });
  const meshes = model.root.getChildMeshes();
  return {
    root: model.root,
    sync: (enemy, dt) => {
      model.sync(enemy, dt);
      const opacity = enemy instanceof Phantom ? enemy.opacity : 1;
      for (const mesh of meshes) {
        mesh.visibility = opacity;
        mesh.isVisible = opacity > 0;
      }
    },
  };
}
