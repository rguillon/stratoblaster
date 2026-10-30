import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import type { SegmentedBody } from '../../../render/geometry/organic';
import {
  carapace,
  curve,
  plate,
  segmentedBody,
  tendril,
  vein as veinTube,
} from '../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { ahead, H, QUARTER } from './elite-shapes';
import { SIDES } from './enemy-shapes';
import { reactorSac } from './organic-parts';
import { buildJointedModel } from './jointed-model';

// P05-R19, P16-R04: the Hydra. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.hydra;
const NEON = ELITE_NEON.hydra;
const F = ENEMY_LOOK.flesh;

type Head = (typeof CFG.heads)[number];

/** P16-R04: the broad, armoured shell (tail to front) and the bone ridge along its back. */
const SHELL: SegmentedBody = {
  tail: -21.5,
  nose: 8,
  segments: 4,
  width: 22,
  bottom: -4,
  top: 6,
  girth: (t) => 0.5 + 0.5 * Math.sin(Math.PI * Math.min(1, t * 1.15)),
  closed: [false, false],
};
/** The metal plates grafted on its shoulders (right side). */
const PLATES: readonly OutlinePoint[][] = [
  [
    [6, 4],
    [17, 0],
    [16, -8],
    [6, -6],
  ],
  [
    [5, -10],
    [14, -12],
    [10, -19],
    [4, -17],
  ],
];
/** How high the necks and heads ride. */
const NECK_Y = 1.5;
/** A head around its centre, along +Z: a swollen skull closing towards its eye. */
const HEAD: SegmentedBody = {
  tail: -5,
  nose: 6.5,
  segments: 2,
  width: 4.8,
  bottom: -2.4,
  top: 3.2,
};
/** The right mandible, beside the skull (mirrored for the left). */
const JAW: OutlinePoint[] = [
  [2.5, -1],
  [4.6, 1],
  [3.6, 6.5],
  [2.4, 3],
];
/** The armour cap on a head's brow (around its centre, along +Z). */
const CAP: OutlinePoint[] = [
  [-2.6, -4],
  [2.6, -4],
  [2, 2],
  [-2, 2],
];
/** The shell, its plates, ridge and veins, and the reactors in sacs at its tail. */
function body(p: EnemyParts): void {
  const { hull, flesh, neon, vein } = p;
  carapace(flesh, SHELL, [F.teal, F.purple]);
  tendril(flesh, curve([0, 5.5, -19], [0, 6, 4], [0, 2.5, 0], 3), [1.6, 0.8], 4, F.bone);
  for (const s of SIDES) {
    PLATES.forEach((pl, i) => {
      const outline = pl.map(([x, z]): OutlinePoint => [s * x, z]);
      // The front plates riveted, the back ones plain (lean on triangles).
      if (i === 0) plate(hull, outline, [4.4, 5.6], [H.panel, H.dark]);
      else hull.bevelSlab(outline, [4.4, 4.4, 5.6], [0, 0.6], H.panel);
    });
    veinTube(vein, curve([s * 3, 5.6, -17], [s * 5, 5.4, 4], [s * 3, 1, 0], 3), 0.9, NEON);
    reactorSac(p, [s * 8, 0.5, -21.5], 2.2, NEON, { flesh: F.teal });
  }
  // Teal lights along the front edge, where the necks grow out.
  neon.box([30, 0.6, 1.2], NEON, { at: [0, 4.2, 6.2] });
}

/** A neck from its joint to its head: a flesh tendril ringed with teal and metal collars. */
function neck(head: Head): (p: EnemyParts) => void {
  const [px, py] = head.pivot;
  const [hx, hy] = head.head;
  const length = Math.hypot(hx - px, hy - py) - 3;
  const at = bossPoint(px, py, NECK_Y);
  return ({ hull, flesh, neon }) => {
    const path = [0, 0.33, 0.66, 1].map((t) => ahead(at, head.aim, t * length));
    tendril(flesh, path, [3, 2], 5, F.teal);
    for (const t of [0.35, 0.7]) {
      const [x, , z] = ahead(at, head.aim, t * length);
      const r = 3.3 - 1.1 * t;
      hull.ring(r, 1.2, 5, H.panel, { at: [x, NECK_Y - 0.6, z], pitch: QUARTER, yaw: head.aim });
      neon.box([2 * r, 0.4, 0.6], NEON, { at: [x, NECK_Y + r - 0.2, z], yaw: head.aim });
    }
  };
}

/** A head on its neck: a skull with bone mandibles, a metal brow and a glowing eye. */
function head(spec: Head): (p: EnemyParts) => void {
  const at = bossPoint(spec.head[0], spec.head[1], NECK_Y);
  const eye = bossPoint(...spec.muzzle);
  return ({ hull, flesh, neon, muzzle }) => {
    segmentedBody(flesh, HEAD, F.teal, { at, yaw: spec.aim });
    hull.bevelSlab(CAP, [2.6, 2.6, 3.4], [0, 0.5], H.panel, { at, yaw: spec.aim });
    for (const s of SIDES) {
      const jaw = JAW.map(([x, z]): OutlinePoint => [s * x, z]);
      flesh.bevelSlab(jaw, [-1.2, 0, 1], [0.2, 0.4], F.bone, { at, yaw: spec.aim });
    }
    const lens = [
      [0, -0.8],
      [1.5, 0],
      [0, 0.8],
    ] as const;
    neon.lathe(lens, 6, NEON, { at: [eye[0], eye[1] - 0.6, eye[2]] });
    muzzle(eye);
  };
}

/**
 * P05-R19, P16-R04: a broad, plated shell with three long flesh necks forward, each ending in a
 * teal-eyed head.
 */
export function buildHydra(scene: Scene): EnemyModel {
  return buildJointedModel('hydra', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.heads.map((h) => [h.joint, neck(h)])),
    parts: Object.fromEntries(CFG.heads.map((h) => [h.id, head(h)])),
  });
}
