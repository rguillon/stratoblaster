import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { VETERAN_CONFIG, VETERAN_NEON as N } from '../../config/enemies-veteran';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { SegmentedBody } from '../../../render/geometry/organic';
import {
  carapace,
  organ,
  segmentedBody,
  segmentStations,
  tendril,
} from '../../../render/geometry/organic';
import { MANTIS_DESIGN } from '../../sim/enemies/mantis';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { eyes, reactorSac } from './organic-parts';
import { mandibles } from './vetelite-organic';
import { buildJointedModel } from './jointed-model';
import { backBand, noseGun } from './veteran-shapes';

// P05-R16, P16-R04: the Mantis, its arms on their shoulders (P05-R13). Logical pixels, nose +Z, Y up; a
// point (x, y) of the design (X right, Y up, facing down) is at `bossPoint(x, y)`.
const H = ENEMY_LOOK.hull;
const F = ENEMY_LOOK.flesh;
const QUARTER = Math.PI / 2;
const CFG = VETERAN_CONFIG.mantis;
const ARM = CFG.arm;
const WHITE = [1, 1, 1] as const;

/** P16-R04: its long, swollen abdomen and plated thorax, tail to neck. */
const ABDOMEN: SegmentedBody = {
  tail: -20,
  nose: -1.5,
  segments: 3,
  width: 4.8,
  bottom: -1.4,
  top: 2.6,
};
const THORAX: SegmentedBody = {
  tail: -2,
  nose: 8.5,
  segments: 2,
  width: 3.6,
  bottom: -1,
  top: 2.4,
};
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

/** The arm on side `s`: a flesh forearm, a bone scythe, lime along its edge, its muzzles. */
function drawArm(s: 1 | -1) {
  return ({ flesh, neon, charge, muzzle }: EnemyParts): void => {
    // P16-R04: the forearm a sinew, the scythe grown out of it.
    const fore = [0, 4, 8, 11.5].map((t) => bladePoint(s, [t, 0], 1.2));
    tendril(flesh, fore, [1.5, 1.1], 3, F.sinew);
    flesh.bevelSlab(outline(s, BLADE), [0.4, 1.2, 1.9], [0.3, 0.5], F.bone, {}, F.sinew);
    neon.slab(outline(s, EDGE), [1.85, 2.05], N.mantis);
    const muzzles = s === 1 ? ARM.muzzles.right : ARM.muzzles.left;
    for (const [x, y, h] of muzzles) {
      const at = bossPoint(x, y, h);
      charge.box([0.9, 0.5, 0.9], WHITE, { at: [at[0], 1.9, at[2]] });
      muzzle(at);
    }
  };
}

/** The shoulder on side `s`: a metal knuckle turning with the arm, not to be shot off. */
function drawShoulder(s: 1 | -1) {
  return ({ hull }: EnemyParts): void => {
    const at = bladePoint(s, [0, 0], 0.2);
    hull.cylinder(2.2, 2, 6, H.panel, { at }, 1.6);
  };
}

/** The body: abdomen striped with lime, plated thorax, the head with its eyes, mandibles, gun. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  segmentedBody(flesh, ABDOMEN, F.teal);
  carapace(flesh, THORAX, [F.sinew, F.teal]);
  // The narrow head, a bulb on its neck, a metal plate on its brow.
  organ(flesh, 2.4, 5, F.teal, { at: [0, 0.3, 9.4], pitch: QUARTER }, 1.1);
  hull.box([3, 0.5, 2.4], H.panel, { at: [0, 2.6, 11] });
  const stations = segmentStations(ABDOMEN);
  for (const band of [
    [-15, -14],
    [-11.5, -10.5],
    [-8, -7],
  ] as const) {
    backBand(neon, stations, band, N.mantis);
  }
  eyes(p, [0, 1.6, 12.6], { count: 2, size: 0.7, spacing: 2.8 }, N.mantis);
  mandibles(flesh, [0, 0.6, 13.4], [2.6, 2.4, 0.4]);
  reactorSac(p, [0, 0.3, -20], 1.1, N.mantis, { flesh: F.teal });
  noseGun(p, [0, 1.4, 11.8], 2);
}

/**
 * P05-R16, P16-R04: an insect with a narrow head and two long bone scythes on flesh forearms,
 * folded forward, lime neon along the blades. The arms swing on their shoulders and go when shot
 * off.
 */
export function buildMantis(scene: Scene): EnemyModel {
  return buildJointedModel('mantis', scene, N.mantis, MANTIS_DESIGN, {
    body: drawBody,
    limbs: { 'left-shoulder': drawShoulder(-1), 'right-shoulder': drawShoulder(1) },
    parts: { 'left-arm': drawArm(-1), 'right-arm': drawArm(1) },
  });
}
