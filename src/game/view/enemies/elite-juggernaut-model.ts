import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import type { SegmentedBody } from '../../../render/geometry/organic';
import {
  carapace,
  curve,
  plate,
  segmentedBody,
  vein as veinTube,
} from '../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { barrel, H, QUARTER } from './elite-shapes';
import { angryEyes, SIDES } from './enemy-shapes';
import { reactorSac } from './organic-parts';
import { buildJointedModel } from './jointed-model';

// P05-R22, P16-R04: the Juggernaut. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.juggernaut;
const NEON = ELITE_NEON.juggernaut;
const F = ENEMY_LOOK.flesh;

type Cannon = (typeof CFG.cannons)[number];
type Plate = (typeof CFG.plates)[number];

/** P16-R04: the massive, wide body (tail to front) and the ridged shell over it. */
const BODY: SegmentedBody = {
  tail: -24,
  nose: 12,
  segments: 3,
  width: 24,
  bottom: -4,
  top: 3,
  girth: (t) => 0.7 + 0.3 * Math.sin(Math.PI * t),
  closed: [false, false],
};
const SHELL: SegmentedBody = {
  tail: -23,
  nose: 11,
  segments: 3,
  width: 19,
  bottom: 0,
  top: 4.8,
  closed: [false, false],
};
/** The metal plate bolted on its back, under the turret. */
const BACK_PLATE: OutlinePoint[] = [
  [-9, -14],
  [9, -14],
  [11, 4],
  [-11, 4],
];
/** The back turret carrying the core's twin cannon. */
const TURRET = { radius: 6.5, z: -3, y: 4.6, height: 3.2 } as const;
/** A cannon's flesh pod around its centre, along +Z. */
const POD: SegmentedBody = { tail: -6, nose: 5, segments: 2, width: 5.2, bottom: -2.5, top: 4.2 };
/** A front plate around its centre: a thick, chamfered slab. */
const PLATE: OutlinePoint[] = [
  [-8.5, -6],
  [8.5, -6],
  [9.5, 1.5],
  [6.5, 7],
  [-6.5, 7],
  [-9.5, 1.5],
];

/** The armoured beast: a flesh body under a plated shell, the turret, its eyes, reactor sacs. */
function body(p: EnemyParts): void {
  const { hull, flesh, neon, vein } = p;
  // P16-R04: the swollen body, and the metal shell bolted over its back.
  segmentedBody(flesh, BODY, F.sinew);
  carapace(flesh, SHELL, [F.crimson, F.sinew]);
  plate(hull, BACK_PLATE, [3.6, 5.2], [H.base, H.dark]);
  for (const slit of angryEyes([0, 6], 6, [8, 1.4], 0.25)) {
    neon.slab(slit, [4.5, 4.9], NEON);
  }
  for (const x of [-15, 15]) neon.box([1.4, 0.4, 20], NEON, { at: [x, 4.5, -10] });
  for (const s of SIDES) {
    veinTube(vein, curve([s * 4, 5.4, -20], [s * 11, 4.8, 6], [s * 4, 0.6, 0], 2), 1, NEON);
  }
  hull.cylinder(TURRET.radius, TURRET.height, 8, H.panel, { at: [0, TURRET.y, TURRET.z] });
  for (const m of CFG.muzzles) barrel(p, bossPoint(...m), 0, [1.1, 7]);
  for (const x of [-10, 10]) reactorSac(p, [x, 0.5, -24.5], 2.4, NEON, { veinLength: 4 });
  p.reactor([0, 0.5, -24.5], 2.4);
}

/** A shoulder mount, a metal joint turning with its joint, a sinew into the body. */
function shoulder(cannon: Cannon): (p: EnemyParts) => void {
  const at = bossPoint(cannon.pivot[0], cannon.pivot[1], -2.5);
  return ({ hull }) => {
    hull.cylinder(5, 7, 6, H.dark, { at });
  };
}

/** A shoulder cannon: a flesh pod in a metal band, a steel-blue gland and a long barrel. */
function cannon(spec: Cannon): (p: EnemyParts) => void {
  const at = bossPoint(spec.centre[0], spec.centre[1], 0);
  return (p) => {
    segmentedBody(p.flesh, POD, F.crimson, { at });
    p.hull.ring(4.9, 1.4, 6, H.panel, { at: [at[0], at[1] + 0.8, at[2] - 0.5], pitch: QUARTER });
    p.vein.box([1.2, 0.5, 6], NEON, { at: [at[0], at[1] + 4.4, at[2]] });
    p.neon.box([0.6, 0.4, 3], NEON, { at: [at[0], at[1] + 4.6, at[2] - 4] });
    barrel(p, bossPoint(...spec.muzzle), 0, [1.4, 8]);
  };
}

/** A front armour plate, riveted on, a steel-blue light along its edge. */
function frontPlate(spec: Plate): (p: EnemyParts) => void {
  const at = bossPoint(spec.x, spec.y, 0);
  return ({ hull, neon }) => {
    hull.bevelSlab(PLATE, [-3, 0, 5], [1, 2.2], H.panel, { at }, H.base);
    for (const [x, z] of [
      [-5, 4],
      [5, 4],
      [-6, -3],
      [6, -3],
    ] as const) {
      hull.box([1, 0.6, 1], H.dark, { at: [at[0] + x, 5.2, at[2] + z] });
    }
    neon.box([10, 0.5, 1.2], NEON, { at: [at[0], 4.6, at[2] + 3.5] });
  };
}

/**
 * P05-R22, P16-R04: a massive, armoured beast with two riveted front plates and a flesh cannon
 * pod on each shoulder.
 */
export function buildJuggernaut(scene: Scene): EnemyModel {
  return buildJointedModel('juggernaut', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.cannons.map((c) => [c.joint, shoulder(c)])),
    parts: {
      ...Object.fromEntries(CFG.cannons.map((c) => [c.id, cannon(c)])),
      ...Object.fromEntries(CFG.plates.map((pl) => [pl.id, frontPlate(pl)])),
    },
  });
}
