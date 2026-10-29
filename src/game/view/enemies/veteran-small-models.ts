import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { MembraneWing, SegmentedBody } from '../../../render/geometry/organic';
import {
  carapace,
  curve,
  organ,
  segmentedBody,
  segmentStations,
  vein as veinTube,
} from '../../../render/geometry/organic';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { Phantom } from '../../sim/enemies/phantom';
import { buildEnemyModel } from './enemy-mesh';
import { flipX, POD_SECTION, SIDES } from './enemy-shapes';
import { eyes, reactorSac } from './organic-parts';
import { mandibles, membranePair, sinew } from './vetelite-organic';
import { backBand, edgeStrip, noseGun } from './veteran-shapes';

// P05-R14, P05-R17, P16-R04: the lighter veteran kinds. Logical pixels, nose +Z, Y up (to the camera).
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const QUARTER = Math.PI / 2;

/** P05-R14, P16-R04: the Wasp's narrow, swollen abdomen (tail to waist), striped with neon. */
const WASP_ABDOMEN: SegmentedBody = {
  tail: -9,
  nose: -0.8,
  segments: 3,
  width: 2.4,
  bottom: -0.9,
  top: 1.8,
  pinch: 0.25,
};
/** Its plated thorax and head, waist to jaws. */
const WASP_THORAX: SegmentedBody = {
  tail: -1.2,
  nose: 7.4,
  segments: 2,
  width: 2.3,
  bottom: -0.9,
  top: 1.8,
};
/** Its two pairs of thin swept wings (right side), the front pair the bigger. */
const WASP_WINGS: readonly MembraneWing[] = [
  {
    root: [1.2, 3.4],
    tips: [
      [9.6, 0.4],
      [9.3, -0.9],
    ],
    y: 1.4,
    thickness: 0.25,
    strut: 0.35,
  },
  {
    root: [1.2, 1.4],
    tips: [
      [7.4, -3.2],
      [6.8, -4.2],
    ],
    y: 1.3,
    thickness: 0.25,
    strut: 0.3,
  },
];

/**
 * P05-R14, P16-R04: a small, wasp-like insect: a swollen abdomen striped with yellow neon bands,
 * two pairs of fluttering membrane wings, a yellow neon sting, bone mandibles round a gun
 * grafted in its jaws, and reactors in flesh sacs under its wings.
 */
export function buildWasp(scene: Scene): EnemyModel {
  return buildEnemyModel('wasp', scene, N.wasp, (p) => {
    const { hull, flesh, neon, vein } = p;
    segmentedBody(flesh, WASP_ABDOMEN, F.sinew);
    carapace(flesh, WASP_THORAX, [F.crimson, F.membrane]);
    // The head, a bulb between the eyes, capped with a metal plate.
    organ(flesh, 1.6, 6, F.crimson, { at: [0, 0.3, 7.2], pitch: QUARTER }, 0.9);
    hull.box([2.2, 0.4, 2.2], H.panel, { at: [0, 1.75, 4.2] });
    const stations = segmentStations(WASP_ABDOMEN);
    for (const band of [
      [-7.2, -6.4],
      [-5.4, -4.6],
      [-3.6, -2.8],
    ] as const) {
      backBand(neon, stations, band, N.wasp);
    }
    for (const wing of WASP_WINGS) membranePair(p, wing, 9);
    // The sting, out of the tail.
    neon.cylinder(0.45, 2, 6, N.wasp, { at: [0, 0.3, -8.8], pitch: -QUARTER }, 0);
    eyes(p, [0, 1.3, 8.3], { count: 2, size: 0.5, spacing: 2.2 }, N.wasp);
    mandibles(flesh, [0, 0.5, 8.2], [2.4, 2.6, 0.35]);
    veinTube(vein, curve([0, 1.9, -1], [0, 2, 5], [0, 0.3, 0], 2), 0.5, N.wasp);
    for (const s of SIDES) reactorSac(p, [s * 2.6, 0.2, 0.6], 0.6, N.wasp, { veinLength: 1.2 });
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
/** Its metal nose cap, grafted over the gun. */
const PHANTOM_NOSE = [
  [7, 1.6, -0.6, 1.6],
  [10.5, 1.2, -0.4, 1.2],
  [12.5, 0, 0.3, 0.3],
] as const;
/** Its body, a low ridged shell blended into the wing, tail to nose. */
const PHANTOM_BODY: SegmentedBody = {
  tail: -10,
  nose: 13.5,
  segments: 3,
  width: 6,
  bottom: -1.2,
  top: 2.4,
  girth: (t) => 0.5 + 0.5 * Math.sin(Math.PI * Math.min(1, t * 1.3)),
};
/** The bone struts holding the wing out: from the shoulder to the nose and to each tip (right). */
const PHANTOM_STRUTS = [
  [
    [3, 0.9, 2],
    [17, 0.4, -6.5],
  ],
  [
    [3, 0.9, -2],
    [9, 0.5, -6.5],
  ],
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
    const { hull, flesh, neon, vein } = p;
    // P16-R04: a membrane wing on bone struts, a shell of a body, a metal nose cap and gun.
    flesh.bevelSlab(PHANTOM_WING, [-0.6, 0, 0.6], [0.5, 1.2], F.membrane, {}, F.purple);
    carapace(flesh, PHANTOM_BODY, [F.purple, F.membrane]);
    for (const strip of phantomEdges()) neon.slab(strip, [-0.15, 0.3], N.phantom);
    for (const s of SIDES) {
      for (const [a, b] of PHANTOM_STRUTS) {
        const at = (q: readonly [number, number, number]) => [s * q[0], q[1], q[2]] as const;
        sinew(flesh, at(a), at(b), [0.7, 0.2], F.bone, [0, 0.5, 0]);
      }
      veinTube(
        vein,
        curve([s * 2.2, 2.3, 3], [s * 2.2, 2, -5], [s * 0.6, 0.4, 0], 2),
        0.6,
        N.phantom,
      );
      reactorSac(p, [s * 2.4, 0.2, -10], 1.2, N.phantom, { flesh: F.purple });
    }
    eyes(p, [0, 1.6, 9], { count: 3, size: 0.45, spacing: 1.2 }, N.phantom);
    hull.loft(POD_SECTION, PHANTOM_NOSE, H.panel);
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
