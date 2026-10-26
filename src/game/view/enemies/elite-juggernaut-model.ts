import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { barrel, H } from './elite-shapes';
import { angryEyes, POD_SECTION, sideStripe } from './enemy-shapes';
import { buildJointedModel } from './jointed-model';

// P05-R22: the Juggernaut. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.juggernaut;
const NEON = ELITE_NEON.juggernaut;

type Cannon = (typeof CFG.cannons)[number];
type Plate = (typeof CFG.plates)[number];

/** The massive, wide hull seen from above, behind its plates. */
const HULL: OutlinePoint[] = [
  [-14, -24],
  [14, -24],
  [22, -16],
  [24, 4],
  [18, 12],
  [-18, 12],
  [-24, 4],
  [-22, -16],
];
/** The back turret carrying the core's twin cannon. */
const TURRET = { radius: 6.5, z: -3, y: 4.6, height: 3.2 } as const;
/** A cannon's pod around its centre, along +Z. */
const POD = [
  [-6, 4.6, -2, 3.5],
  [0, 5.2, -2.5, 4.2],
  [5, 4.2, -2, 3.2],
] as const;
/** A front plate around its centre: a thick, chamfered slab. */
const PLATE: OutlinePoint[] = [
  [-8.5, -6],
  [8.5, -6],
  [9.5, 1.5],
  [6.5, 7],
  [-6.5, 7],
  [-9.5, 1.5],
];

/** The hull, its steel-blue visor and stripes, the turret with the core's cannon, reactors. */
function body(p: EnemyParts): void {
  const { hull, neon, reactor } = p;
  hull.bevelSlab(HULL, [-4, 0, 4.6], [1.5, 3], H.base, {}, H.panel);
  for (const slit of angryEyes([0, 6], 6, [8, 1.4], 0.25)) {
    neon.slab(slit, [4.5, 4.9], NEON);
  }
  for (const x of [-15, 15]) neon.box([1.4, 0.4, 20], NEON, { at: [x, 4.5, -10] });
  hull.cylinder(TURRET.radius, TURRET.height, 8, H.panel, { at: [0, TURRET.y, TURRET.z] });
  for (const m of CFG.muzzles) barrel(p, bossPoint(...m), 0, [1.1, 7]);
  for (const x of [-10, 0, 10]) reactor([x, 0.5, -24.5], 2.4);
}

/** A shoulder mount, turning with its joint. */
function shoulder(cannon: Cannon): (p: EnemyParts) => void {
  const at = bossPoint(cannon.pivot[0], cannon.pivot[1], -2.5);
  return ({ hull }) => {
    hull.cylinder(5, 7, 8, H.dark, { at });
  };
}

/** A shoulder cannon: a pod with a steel-blue stripe and a long barrel. */
function cannon(spec: Cannon): (p: EnemyParts) => void {
  const at = bossPoint(spec.centre[0], spec.centre[1], 0);
  return (p) => {
    p.hull.loft(POD_SECTION, POD, H.panel, { at });
    const stripe = sideStripe(POD_SECTION, 2, [0.3, 0.7]);
    p.neon.loft(stripe, POD, NEON, { at }, { open: true });
    barrel(p, bossPoint(...spec.muzzle), 0, [1.4, 8]);
  };
}

/** A front armour plate, a steel-blue light along its edge. */
function plate(spec: Plate): (p: EnemyParts) => void {
  const at = bossPoint(spec.x, spec.y, 0);
  return ({ hull, neon }) => {
    hull.bevelSlab(PLATE, [-3, 0, 5], [1, 2.2], H.panel, { at }, H.base);
    neon.box([10, 0.5, 1.2], NEON, { at: [at[0], 4.6, at[2] + 3.5] });
  };
}

/** P05-R22: a massive, wide hull with two front plates and a shoulder cannon on each side. */
export function buildJuggernaut(scene: Scene): EnemyModel {
  return buildJointedModel('juggernaut', scene, NEON, CFG.design, {
    body,
    limbs: Object.fromEntries(CFG.cannons.map((c) => [c.joint, shoulder(c)])),
    parts: {
      ...Object.fromEntries(CFG.cannons.map((c) => [c.id, cannon(c)])),
      ...Object.fromEntries(CFG.plates.map((pl) => [pl.id, plate(pl)])),
    },
  });
}
