import type { Scene } from '@babylonjs/core/scene';
import type { Placement } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  JAGUAR,
  JAGUAR_EYE,
  JAGUAR_FANGS,
  JAGUAR_PARTS,
} from '../../../config/bosses/world-3/jaguar';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { angryEyes, canopyPaint, decal, sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { vent } from '../mini-boss-greebles';
import { reactorSac } from '../../enemies/organic-parts';
import { ROUND_SECTION } from '../../../../render/geometry/organic';
import { F, sinew, spine, veinTo } from './jungle-flesh';
import { edgeLights, symmetric } from '../overlord-city';
import { AMBER, clawMount, clawTurret, COAT, rosette, tailMount, tailTurret } from './jaguar-parts';

// P09-R09, 3-5: the Jaguar, the mini boss of the canopy city. Model space: logical pixels, nose
// +Z (down the screen), Y up towards the camera; +X is the screen's left.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const H = ENEMY_LOOK.hull;
const WHITE: Rgb = [1, 1, 1];
const QUARTER = Math.PI / 2;

/**
 * The stealth delta seen from above (right half, nose to tail): a long nose, the wings swept
 * back from the claw roots, a sawtooth trailing edge.
 */
const WING = symmetric(
  [
    [5, 54],
    [10, 40],
    [15, 26],
    [22, 14],
    [40, -2],
    [57, -18],
    [56, -26],
    [44, -26],
    [36, -36],
    [26, -32],
    [18, -44],
    [8, -46],
  ],
  60,
);
/** Heights of the wing: belly, edge, top. */
const WING_Y = [-3, 0, 3] as const;
/** Its leading edges, lit amber (edges of {@link WING}, from point i to the next). */
const LEADING = [3, 4, 5, 19, 20, 21];
/** The fuselage along the centre line, tail to nose (loft stations), the cockpit painted dark. */
const FUSELAGE = [
  [-50, 6, 1, 6],
  [-36, 10, 1, 9],
  [-10, 12, 1, 11],
  [14, 11, 1, 11],
  [32, 8, 1, 9],
  [46, 6, 1, 7],
  [56, 3, 1, 4.5],
  [61, 0, 2.5, 2.5],
] as const;
/** The rosettes on the wings (right half, mirrored): where and how big. */
const SPOTS = [
  [24, 4, 3.2],
  [35, -9, 3],
  [48, -18, 2.3],
  [26, -20, 3.2],
  [19, -33, 2.5],
  [39, -27, 2],
  [16, 18, 2.4],
] as const;
/** The tail curling from the fuselage's end out to the cannon's pod (points along it). */
const TAIL: readonly Vec3[] = [
  [0, 2.5, -48],
  [8, 2.5, -56],
  [20, 2.5, -56],
  bossPoint(...JAGUAR_PARTS.tail, 1.5),
];

/** A cylinder lying from `a` to `b`. */
function segment(p: EnemyParts, [a, b]: readonly [Vec3, Vec3], radius: number, end: number): void {
  const [dx, dz] = [b[0] - a[0], b[2] - a[2]];
  const place: Placement = { at: a, pitch: QUARTER, yaw: Math.atan2(dx, dz) };
  p.flesh.cylinder(radius, Math.hypot(dx, dz), 6, COAT, place, end);
  p.neon.ring(radius + 0.2, 0.7, 6, AMBER, place);
}

/** P16-R05: its bone spine, the sinews and veins under its pelt. */
function drawSinews(p: EnemyParts): void {
  spine(
    p,
    FUSELAGE.slice(1, 5).map(([z, , , t]) => [0, t + 0.3, z] as const),
    { at: [-30, -18, -6, 6], halfWidth: 11, y: 2, height: 9.6 },
    AMBER,
  );
  for (const s of SIDES) {
    sinew(
      p,
      [
        [s * 9, 4, 16],
        [s * 40, 2.4, -14],
      ],
      [0, 1.4, 4],
      1.4,
      F.sinew,
    );
    veinTo(
      p,
      [
        [s * 10, 3.4, 4],
        [s * 36, 3.4, -30],
      ],
      [0, 0, 6],
      AMBER,
    );
  }
}

/** The wings and the fuselage, the cockpit dark, rosettes on the wings, lit leading edges. */
function drawBody(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  // P16-R05: a living big cat: a spotted pelt stretched over its delta like a flying squirrel's,
  // a muscular body with a bone spine, metal fins and nozzles grafted on.
  flesh.bevelSlab(WING, WING_Y, [1.5, 2], F.sinew, {}, COAT);
  edgeLights(neon, WING, LEADING, [-1.4, -0.3], AMBER);
  flesh.loft(ROUND_SECTION, FUSELAGE, COAT, {}, { paint: canopyPaint([3, 4], F.crimson) });
  drawSinews(p);
  for (const side of [1, 6]) {
    neon.loft(
      sideStripe(ROUND_SECTION, side, [0.3, 0.75]),
      FUSELAGE.slice(1, 6),
      AMBER,
      {},
      {
        open: true,
      },
    );
  }
  for (const s of SIDES) {
    for (const [x, z, r] of SPOTS) rosette(hull, [s * x, z], r, WING_Y[2] + 0.05);
    vent(hull, [s * 14, WING_Y[2] - 0.1, -22], [4, 9], 3, s * 0.2);
    // Canted fins, like a stealth fighter's, near the tail.
    hull.box([1, 8, 12], H.panel, { at: [s * 13, 4, -34], roll: s * 0.5 }, COAT);
    neon.box([0.5, 0.5, 10], AMBER, { at: [s * 16.5, 10.6, -34], roll: s * 0.5 });
  }
  for (let i = 0; i < TAIL.length - 1; i++) {
    const [a, b] = [TAIL[i], TAIL[i + 1]];
    if (a && b) segment(p, [a, b], 2.8 - i * 0.3, 2.5 - i * 0.3);
  }
}

/** The cat's head: ears on the fuselage, angry amber eyes, fang guns under the nose. */
function drawHead(p: EnemyParts): void {
  const { hull, flesh, neon, charge, muzzle } = p;
  for (const s of SIDES) {
    flesh.lathe(
      [
        [3.2, 0],
        [0, 5.5],
      ],
      3,
      COAT,
      { at: [s * 6, 8, 36], yaw: s * 0.4 },
    );
  }
  for (const eye of angryEyes([0, 45], 3, [5.5, 1.6], 0.35)) decal(neon, eye, 7.5, AMBER);
  for (const m of JAGUAR_FANGS) {
    const tip = bossPoint(...m);
    const along = (z: number): Placement => ({ at: [tip[0], tip[1], z], pitch: QUARTER });
    hull.cylinder(1.2, tip[2] - 2 - 46, 6, H.dark, along(46), 1);
    charge.cylinder(1.3, 2, 6, WHITE, along(tip[2] - 2), 0.8);
    muzzle(tip);
  }
  // The spiral emitter: a lit eye on the back behind the cockpit.
  const eye = bossPoint(...JAGUAR_EYE);
  hull.cylinder(4, 1.6, 8, H.dark, { at: [eye[0], eye[1] - 3, eye[2]] }, 3.4);
  charge.lathe(
    [
      [2.6, 0],
      [1.8, 1.2],
      [0, 1.4],
    ],
    6,
    WHITE,
    { at: [eye[0], eye[1] - 1.4, eye[2]] },
  );
  neon.ring(4.1, 0.6, 8, AMBER, { at: [eye[0], eye[1] - 2.6, eye[2]] });
  muzzle(eye, 'ring');
}

/**
 * P09-R09: the Jaguar, a sleek stealth interceptor with spotted armour and amber neon: a cat's
 * head with ears and fang guns, claw guns reaching forward from its wing roots, and a tail
 * curling out to a cannon held high over its left wing.
 */
export function buildJaguar(scene: Scene): EnemyModel {
  return buildBossModel(JAGUAR, scene, AMBER, {
    core: (p) => {
      drawBody(p);
      drawHead(p);
      for (const s of SIDES) reactorSac(p, [s * 6, 3.5, -50], 3.5, AMBER, { flesh: F.sinew });
    },
    parts: { 'claw-left': clawMount, 'claw-right': clawMount, 'tail-cannon': tailMount },
    turrets: { 'claw-left': clawTurret, 'claw-right': clawTurret, 'tail-cannon': tailTurret },
  });
}
