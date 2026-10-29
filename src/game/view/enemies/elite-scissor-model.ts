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
import { ahead, H, QUARTER, strip, WHITE } from './elite-shapes';
import { canopyPaint, FIGHTER_SECTION, flipX, SIDES } from './enemy-shapes';
import { eyes, reactorSac } from './organic-parts';
import { buildJointedModel } from './jointed-model';

// P05-R21, P16-R04: the Scissor. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.scissor;
const NEON = ELITE_NEON.scissor;
const F = ENEMY_LOOK.flesh;

type Arm = (typeof CFG.arms)[number];

/** P16-R04: the long, narrow, segmented body under its ridged shell, tail to nose. */
const BODY: SegmentedBody = {
  tail: -31,
  nose: 29,
  segments: 5,
  width: 8.5,
  bottom: -2.5,
  top: 3.2,
};
const SHELL: SegmentedBody = {
  tail: -24,
  nose: 18,
  segments: 4,
  width: 6.5,
  bottom: 0.6,
  top: 4.6,
  closed: [false, false],
};
/** The right tail fin (mirrored for the left). */
const FIN: OutlinePoint[] = [
  [-3, -20],
  [-11, -30],
  [-10.5, -33],
  [-3, -28],
];
/** Its metal nose cap, tail to nose. */
const NOSE = [
  [17, 4, -1.4, 2.6],
  [23, 2.6, -1, 1.8],
  [29.5, 0, 0, 0],
] as const;
/** The right shoulder's armour plate (mirrored for the left), over the arm's hinge. */
const SHOULDER: OutlinePoint[] = [
  [3, 12],
  [9, 9],
  [9, 3],
  [3, 4],
];
/** How high the arms ride. */
const ARM_Y = 1;
/** An arm from its hinge along +Z: a blade narrowing to the emitter at its tip. */
const BLADE: OutlinePoint[] = [
  [-2.8, -2.5],
  [2.8, -2.5],
  [2.2, 27],
  [-2.2, 27],
];

/** The body and its shell, crimson veins, metal tail fins, a nose cap, reactors in sacs. */
function body(p: EnemyParts): void {
  const { hull, flesh, neon, vein } = p;
  segmentedBody(flesh, BODY, F.crimson);
  carapace(flesh, SHELL, [F.sinew, F.crimson]);
  hull.loft(FIGHTER_SECTION, NOSE, H.base, {}, { paint: canopyPaint([2, 3], H.dark) });
  neon.box([1.2, 0.5, 22], NEON, { at: [0, 4.8, -3] });
  eyes(p, [0, 1.8, 22], { count: 2, size: 0.6, spacing: 3 }, NEON);
  for (const s of SIDES) {
    veinTube(vein, curve([s * 5, 2, -20], [s * 4.5, 2.4, 14], [s * 2.5, 0.6, 0], 3), 0.9, NEON);
    plate(hull, s > 0 ? SHOULDER : flipX(SHOULDER), [3.6, 5], [H.panel, H.dark]);
    hull.bevelSlab(s > 0 ? FIN : flipX(FIN), [-0.5, 0, 0.6], [0.2, 0.4], H.base, {}, H.panel);
    reactorSac(p, [s * 3, 0.3, -31], 1.6, NEON);
  }
}

/** A shoulder hinge, a metal joint turning with its arm. */
function shoulder(arm: Arm): (p: EnemyParts) => void {
  const at = bossPoint(arm.pivot[0], arm.pivot[1], -1.5);
  return ({ hull, neon }) => {
    hull.cylinder(3.4, 4.5, 8, H.panel, { at });
    neon.ring(3.5, 0.8, 8, NEON, { at: [at[0], 2.2, at[2]] });
  };
}

/** A laser arm: a flesh limb, a bone blade with a crimson edge, metal cuffs, the emitter. */
function arm(spec: Arm): (p: EnemyParts) => void {
  const pivot = bossPoint(spec.pivot[0], spec.pivot[1], ARM_Y);
  const tip = bossPoint(...spec.muzzle);
  const yaw = spec.aim;
  return ({ hull, flesh, neon, charge, muzzle }) => {
    const path = [0, 8, 16, 23].map((d) => ahead([pivot[0], ARM_Y + 0.6, pivot[2]], yaw, d));
    tendril(flesh, path, [2.6, 1.6], 5, F.sinew);
    flesh.bevelSlab(BLADE, [-1.4, 0, 1.6], [0.4, 0.7], F.bone, { at: pivot, yaw }, F.sinew);
    for (const d of [6, 17]) {
      const [x, , z] = ahead(pivot, yaw, d);
      hull.box([6, 1, 2.4], H.panel, { at: [x, ARM_Y + 1.6, z], yaw });
    }
    strip(neon, [pivot[0], ARM_Y + 2.2, pivot[2]], yaw, [13, 18, 1.2], NEON);
    // The emitter: a cone ending at the tip, brightening through the warning.
    const lens = [
      [2, 0],
      [1.2, 2.2],
      [0, 3],
    ] as const;
    charge.lathe(lens, 6, WHITE, { at: ahead(tip, yaw, -3), pitch: QUARTER, yaw });
    muzzle(tip, 'laser');
  };
}

/**
 * P05-R21, P16-R04: a long, narrow, shelled body with two crimson laser arms, bone blades on
 * flesh limbs, hinged at its shoulders.
 */
export function buildScissor(scene: Scene): EnemyModel {
  return buildJointedModel('scissor', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.arms.map((a) => [a.joint, shoulder(a)])),
    parts: Object.fromEntries(CFG.arms.map((a) => [a.id, arm(a)])),
  });
}
