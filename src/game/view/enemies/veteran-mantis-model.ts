import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_CONFIG, VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { MANTIS_DESIGN } from '../../sim/enemies/mantis';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { POD_SECTION, SIDES } from './enemy-shapes';
import { buildJointedModel } from './jointed-model';
import { backBand, noseGun } from './veteran-shapes';

// P05-R16: the Mantis, its arms on their shoulders (P05-R13). Logical pixels, nose +Z, Y up; a
// point (x, y) of the design (X right, Y up, facing down) is at `bossPoint(x, y)`.
const H = ENEMY_LOOK.hull;
const CFG = VETERAN_CONFIG.mantis;
const ARM = CFG.arm;
const WHITE = [1, 1, 1] as const;

/** Its long abdomen, thorax and narrow head, tail to nose. */
const ABDOMEN = [
  [-20, 1.8, -0.6, 1.2],
  [-17, 3.4, -1, 1.8],
  [-11, 4.8, -1.4, 2.6],
  [-4.5, 3.8, -1.2, 2.2],
  [-1.5, 2, -0.8, 1.3],
] as const;
const THORAX = [
  [-2, 2.2, -0.8, 1.5],
  [2, 3.6, -1, 2.4],
  [6, 2.8, -0.9, 2],
  [8.5, 1.3, -0.5, 1.1],
] as const;
const HEAD = [
  [8, 1.2, -0.5, 1],
  [10, 2.8, -0.8, 1.8],
  [12.5, 2, -0.6, 1.4],
  [15, 0, 0.3, 0.3],
] as const;

/**
 * The blade (right arm, along its length from the shoulder `t`, and across it `w`, outwards):
 * a forearm, then a scythe hooking in, its cutting edge on the inside.
 */
const BLADE = [
  [0, -1.3],
  [0, 1.3],
  [11, 1.7],
  [19, 1.4],
  [24.5, 0],
  [23, -0.9],
  [18, -2.4],
  [13, -2.8],
  [11, -1.3],
] as const;
/** The lime neon along the blade's cutting edge. */
const EDGE = [
  [12, -1.5],
  [13, -2.6],
  [18, -2.2],
  [23, -0.7],
  [22.6, -0.2],
  [18, -1.5],
  [13, -1.8],
] as const;

/** The blade's local point `(t, w)` on side `s`, in model space at height `h`. */
function bladePoint(s: 1 | -1, [t, w]: readonly [number, number], h = 0) {
  const out = (ARM.outDeg * Math.PI) / 180;
  const [sx, sy] = [s * CFG.shoulder[0], CFG.shoulder[1]];
  const x = sx + t * s * Math.sin(out) + w * s * Math.cos(out);
  const y = sy - t * Math.cos(out) + w * Math.sin(out);
  return bossPoint(x, y, h);
}

/** An outline of the blade's local points, on side `s`, in model XZ. */
const outline = (s: 1 | -1, points: readonly (readonly [number, number])[]): OutlinePoint[] =>
  points.map((p) => {
    const [x, , z] = bladePoint(s, p);
    return [x, z];
  });

/** The arm on side `s`: its blade, lime along its edge, its pair of muzzles lighting up. */
function drawArm(s: 1 | -1) {
  return ({ hull, neon, charge, muzzle }: EnemyParts): void => {
    hull.bevelSlab(outline(s, BLADE), [0.4, 1.2, 1.9], [0.3, 0.5], H.base, {}, H.panel);
    neon.slab(outline(s, EDGE), [1.85, 2.05], N.mantis);
    const muzzles = s === 1 ? ARM.muzzles.right : ARM.muzzles.left;
    for (const [x, y, h] of muzzles) {
      const at = bossPoint(x, y, h);
      charge.box([0.9, 0.5, 0.9], WHITE, { at: [at[0], 1.9, at[2]] });
      muzzle(at);
    }
  };
}

/** The shoulder on side `s`: a knuckle turning with the arm, not to be shot off. */
function drawShoulder(s: 1 | -1) {
  return ({ hull }: EnemyParts): void => {
    const at = bladePoint(s, [0, 0], 0.2);
    hull.cylinder(2.2, 2, 6, H.panel, { at }, 1.6);
  };
}

/** The hull: abdomen striped with lime, thorax, the narrow head with its eyes and gun. */
function drawBody(p: EnemyParts): void {
  const { hull, neon, reactor } = p;
  hull.loft(POD_SECTION, ABDOMEN, H.base);
  hull.loft(POD_SECTION, THORAX, H.panel);
  hull.loft(POD_SECTION, HEAD, H.base);
  for (const band of [
    [-15, -14],
    [-11.5, -10.5],
    [-8, -7],
  ] as const) {
    backBand(neon, ABDOMEN, band, N.mantis);
  }
  for (const s of SIDES) {
    neon.box([1.2, 0.7, 1.8], N.mantis, { at: [s * 1.7, 1.2, 10.4] });
  }
  reactor([0, 0.3, -20], 1.1);
  noseGun(p, [0, 1.4, 11.8], 2);
}

/**
 * P05-R16: an insect-like hull with a narrow head and two long scythe arms folded forward, lime
 * neon along the blades. The arms swing on their shoulders and go when shot off.
 */
export function buildMantis(scene: Scene): EnemyModel {
  return buildJointedModel('mantis', scene, N.mantis, MANTIS_DESIGN, {
    body: drawBody,
    limbs: { 'left-shoulder': drawShoulder(-1), 'right-shoulder': drawShoulder(1) },
    parts: { 'left-arm': drawArm(-1), 'right-arm': drawArm(1) },
  });
}
