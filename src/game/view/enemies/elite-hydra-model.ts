import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { ahead, H } from './elite-shapes';
import { CANOPY_SECTION, HULL_SECTION, POD_SECTION, sideStripe, SIDES } from './enemy-shapes';
import { buildJointedModel } from './jointed-model';

// P05-R19: the Hydra. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.hydra;
const NEON = ELITE_NEON.hydra;

type Head = (typeof CFG.heads)[number];

/** The broad hull (loft stations, tail to front) and the ridge along its back. */
const HULL = [
  [-21, 11, -3, 3],
  [-14, 19, -4, 5],
  [-4, 22, -4, 6],
  [4, 18, -3, 5],
  [8, 10, -2, 3.5],
] as const;
const RIDGE = [
  [-18, 3, 4.5, 7],
  [-7, 5, 5.5, 9],
  [3, 4, 4.5, 7],
] as const;
/** How high the necks and heads ride. */
const NECK_Y = 1.5;
/** A head around its centre, along +Z: a snout closing towards its eye. */
const HEAD = [
  [-5, 3.4, -2, 2.4],
  [-1.5, 4.8, -2.4, 3.2],
  [3, 4, -2, 2.8],
  [6.5, 1.4, -1, 1],
] as const;
/** The right mandible, beside the snout (mirrored for the left). */
const JAW: OutlinePoint[] = [
  [2.5, -1],
  [4.6, 1],
  [3.6, 6.5],
  [2.4, 3],
];

/** The broad hull, its ridge and stripes, and the reactors at its tail. */
function body({ hull, neon, reactor }: EnemyParts): void {
  hull.loft(HULL_SECTION, HULL, H.base);
  hull.loft(CANOPY_SECTION, RIDGE, H.panel, {}, { open: true });
  for (const side of [0, 3]) {
    const stripe = sideStripe(CANOPY_SECTION, side, [0.3, 0.7]);
    neon.loft(stripe, RIDGE, NEON, {}, { open: true });
  }
  // Teal lights along the front edge, where the necks grow out.
  neon.box([30, 0.6, 1.2], NEON, { at: [0, 4.2, 6.2] });
  for (const s of SIDES) reactor([s * 8, 0.5, -21.5], 2.2);
}

/** A neck from its joint to its head, ringed with teal. */
function neck(head: Head): (p: EnemyParts) => void {
  const [px, py] = head.pivot;
  const [hx, hy] = head.head;
  const length = Math.hypot(hx - px, hy - py) - 3;
  const at = bossPoint(px, py, NECK_Y);
  return ({ hull, neon }) => {
    const stations = [
      [0, 3.4, -1.7, 1.9],
      [length, 2.2, -1.2, 1.3],
    ] as const;
    hull.loft(POD_SECTION, stations, H.panel, { at, yaw: head.aim });
    for (const t of [0.35, 0.7]) {
      // A band around the neck, a little proud of it.
      const halfWidth = 3.4 - 1.2 * t;
      const [bottom, top] = [-1.7 + 0.5 * t, 1.9 - 0.6 * t];
      const [x, , z] = ahead(at, head.aim, t * length);
      const size = [2 * halfWidth + 0.4, top - bottom + 0.4, 1] as const;
      neon.box(size, NEON, { at: [x, NECK_Y + bottom - 0.2, z], yaw: head.aim });
    }
  };
}

/** A head on its neck: a snout with mandibles and a glowing eye, where its bullets leave from. */
function head(spec: Head): (p: EnemyParts) => void {
  const at = bossPoint(spec.head[0], spec.head[1], NECK_Y);
  const eye = bossPoint(...spec.muzzle);
  return ({ hull, neon, muzzle }) => {
    hull.loft(POD_SECTION, HEAD, H.base, { at, yaw: spec.aim });
    for (const s of SIDES) {
      const jaw = JAW.map(([x, z]): OutlinePoint => [s * x, z]);
      hull.bevelSlab(jaw, [-1.2, 0, 1], [0.2, 0.4], H.panel, { at, yaw: spec.aim });
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

/** P05-R19: a broad hull with three long necks forward, each ending in a teal-eyed head. */
export function buildHydra(scene: Scene): EnemyModel {
  return buildJointedModel('hydra', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.heads.map((h) => [h.joint, neck(h)])),
    parts: Object.fromEntries(CFG.heads.map((h) => [h.id, head(h)])),
  });
}
