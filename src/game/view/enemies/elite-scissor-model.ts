import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { ahead, H, QUARTER, strip, WHITE } from './elite-shapes';
import { canopyPaint, FIGHTER_SECTION, flipX, sideStripe, SIDES } from './enemy-shapes';
import { buildJointedModel } from './jointed-model';

// P05-R21: the Scissor. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.scissor;
const NEON = ELITE_NEON.scissor;

type Arm = (typeof CFG.arms)[number];

/** The long, narrow hull, tail to nose. */
const HULL = [
  [-31, 4, -1.5, 2],
  [-22, 7, -2, 3.5],
  [-6, 8.5, -2.5, 4.5],
  [8, 6.5, -2, 3.6],
  [19, 3.5, -1.2, 2.2],
  [29, 0, 0, 0],
] as const;
/** The right tail fin (mirrored for the left). */
const FIN: OutlinePoint[] = [
  [-3, -20],
  [-11, -30],
  [-10.5, -33],
  [-3, -28],
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

/** The hull, its crimson stripes and tail fins, and its reactors. */
function body({ hull, neon, reactor }: EnemyParts): void {
  hull.loft(FIGHTER_SECTION, HULL, H.base, {}, { paint: canopyPaint([2, 3], H.dark) });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.7]);
    neon.loft(stripe, HULL.slice(1, 5), NEON, {}, { open: true });
  }
  for (const s of SIDES) {
    hull.bevelSlab(s > 0 ? FIN : flipX(FIN), [-0.5, 0, 0.6], [0.2, 0.4], H.base, {}, H.panel);
    reactor([s * 3, 0.3, -31], 1.6);
  }
}

/** A shoulder hinge, turning with its joint. */
function shoulder(arm: Arm): (p: EnemyParts) => void {
  const at = bossPoint(arm.pivot[0], arm.pivot[1], -1.5);
  return ({ hull, neon }) => {
    hull.cylinder(3.4, 4.5, 8, H.panel, { at });
    neon.ring(3.5, 0.8, 8, NEON, { at: [at[0], 2.2, at[2]] });
  };
}

/** A laser arm: a blade with a crimson edge and the emitter at its tip. */
function arm(spec: Arm): (p: EnemyParts) => void {
  const pivot = bossPoint(spec.pivot[0], spec.pivot[1], ARM_Y);
  const tip = bossPoint(...spec.muzzle);
  const yaw = spec.aim;
  return ({ hull, neon, charge, muzzle }) => {
    hull.bevelSlab(BLADE, [-1.4, 0, 1.6], [0.4, 0.7], H.base, { at: pivot, yaw }, H.panel);
    strip(neon, [pivot[0], ARM_Y + 1.5, pivot[2]], yaw, [13, 18, 1.2], NEON);
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

/** P05-R21: a long, narrow hull with two crimson laser arms hinged at its shoulders. */
export function buildScissor(scene: Scene): EnemyModel {
  return buildJointedModel('scissor', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.arms.map((a) => [a.joint, shoulder(a)])),
    parts: Object.fromEntries(CFG.arms.map((a) => [a.id, arm(a)])),
  });
}
