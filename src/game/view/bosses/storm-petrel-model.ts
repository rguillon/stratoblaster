import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { STORM_PETREL } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { flipX, FIGHTER_SECTION, POD_SECTION, sideStripe, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { barrels, edgeStrips, missileTips, shift, sided, turret } from './final-boss-shapes';
import {
  petrelBack,
  petrelHullPaint,
  petrelNacelle,
  petrelTail,
  petrelWing,
  plateDetails,
  podDetails,
  rackDetails,
} from './final-boss-petrel';

// P07-R05: the Storm Petrel, the final boss of 1-1. Logical pixels, nose +Z, Y up (towards the
// camera). A flying-boat bomber: a long hull, a high wing with an engine nacelle on each side,
// magenta neon along the wing edges; its parts are fitted onto the wing and the hull.
const H = ENEMY_LOOK.hull;
const N = BOSS_LOOK.neon['storm-petrel'] ?? [1, 0.1, 0.85];
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/**
 * The flying-boat hull (loft stations, tail to nose): a deep belly, a rounded back. Stations
 * on the straight lines between others only split its paint into plates ({@link petrelHullPaint}).
 */
const HULL = [
  [-64, 3, 3, 7],
  [-50, 7, 0, 9.5],
  [-40, 8.82, -1.36, 10.86],
  [-28, 11, -3, 12.5],
  [-14, 12.5, -3.5, 13.75],
  [-8, 13.14, -3.71, 14.29],
  [0, 14, -4, 15],
  [22, 13, -4, 14],
  [38, 10, -3, 11],
  [50, 5, -1.5, 6],
  [56, 0, 1.5, 1.5],
] as const;
/** The right wing, root inside the hull, its tip squared off; the gun pod sits near its tip. */
const WING = [
  [8, 20],
  [36, 12],
  [74, 3],
  [77, -1],
  [76, -7],
  [56, -10],
  [30, -14],
  [8, -20],
] as const;
/** Neon along the right wing's leading edge and around its tip, just proud of the edge. */
const WING_LEAD = [
  [13, 19.4],
  [36, 12.8],
  [74.4, 3.8],
  [77.8, -1],
  [76.8, -7.6],
] as const;
const WING_TRAIL = [
  [40, -13],
  [30, -14.8],
  [14, -19.6],
] as const;
/** The right tailplane and the fin standing at its tip (in its own plane, rolled upright). */
const TAILPLANE = [
  [4, -48],
  [30, -56],
  [31, -62],
  [24, -64],
  [4, -62],
] as const;
const FIN = [
  [0, -52],
  [11, -59],
  [11, -63],
  [0, -64],
] as const;
/** An engine nacelle on the wing (loft stations, tail to front), around its axis. */
const NACELLE = [
  [-19, 3.6, 0, 7],
  [-8, 5.5, -1, 9],
  [10, 5, -1, 8.5],
  [19, 3.4, 0.8, 6.2],
] as const;
const NACELLE_X = 24;
/** A float on each side of the hull, low under the wing root, its nose ahead of the wing. */
const FLOAT = [
  [-14, 2, 0, 3],
  [-4, 4, 0, 5.5],
  [12, 4, 0, 5.5],
  [24, 0, 2.5, 2.5],
] as const;
/** Dark flaps along the right wing's trailing edge, set into its top. */
const FLAPS = [
  [14, -17.6],
  [30, -12.6],
  [40, -11.2],
] as const;
const WING_Y = [6, 7.5, 9.5] as const;

/** The hull, its neon chines and the cockpit turret on its back (the core's gun). */
function drawHull(p: EnemyParts): void {
  p.hull.loft(FIGHTER_SECTION, HULL, H.base, {}, { paint: petrelHullPaint });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.25, 0.75]);
    p.neon.loft(stripe, HULL.slice(1, 4), N, {}, { open: true });
  }
  petrelBack(p, N);
  // A barbette rising out of the back, the gun turret on it: the cockpit turret.
  p.hull.cylinder(8.5, 7.5, 8, H.dark, { at: [0, 7, 5] }, 8);
  turret(p, [0, 14.5, 5], 8.5, [2, N]);
}

/** Both wings with their neon edges, the engine nacelles and their reactors. */
function drawWings(p: EnemyParts): void {
  for (const s of SIDES) {
    const flip = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => sided(o, s);
    p.hull.bevelSlab(flip(WING), WING_Y, [1.2, 1.8], H.base, {}, H.panel);
    edgeStrips(p.neon, flip(WING_LEAD), 1.2, [6.9, 8.1], N);
    edgeStrips(p.neon, flip(WING_TRAIL), 1, [6.9, 8.1], N);
    const nacelle: Vec3 = [s * NACELLE_X, 7, 0];
    p.hull.loft(POD_SECTION, NACELLE, H.panel, { at: nacelle });
    // A dark intake on the nacelle's front, a neon ring around it.
    p.neon.ring(3.6, 0.8, 6, N, { at: shift(nacelle, [0, 3.8, 19.2]), pitch: QUARTER });
    p.reactor(shift(nacelle, [0, 3.5, -19.2]), 3.2);
    edgeStrips(p.hull, flip(FLAPS), 3, [9.2, 9.8], H.dark);
    p.hull.loft(POD_SECTION, FLOAT, H.base, { at: [s * 20, -4, 0] });
    petrelNacelle(p, nacelle, s);
    petrelWing(p, s, N);
  }
}

/** The tailplanes, their fins and neon tips. */
function drawTail(p: EnemyParts): void {
  for (const s of SIDES) {
    const plane = s > 0 ? TAILPLANE : flipX(TAILPLANE);
    p.hull.bevelSlab(plane, [7, 8, 9.5], [0.6, 1], H.base, {}, H.panel);
    p.hull.bevelSlab(FIN, [-0.9, 0, 0.9], [0.2, 0.5], H.panel, {
      at: [s * 28, 9, 0],
      roll: QUARTER,
    });
    edgeStrips(
      p.neon,
      sided(
        [
          [6, -48.6],
          [30.4, -55.6],
        ],
        s,
      ),
      1,
      [7.6, 8.6],
      N,
    );
    petrelTail(p, s);
  }
}

/** A wing gun pod: an armoured glove over the wing, the pod on it, twin guns at its nose. */
function drawPod(p: EnemyParts, at: Vec3): void {
  const glove = [
    [-13, 15],
    [13, 15],
    [14, -10],
    [10, -14],
    [-10, -14],
    [-14, -10],
  ] as const;
  p.hull.bevelSlab(glove, [9, 9, 11.5], [0, 1.2], H.dark, { at }, H.base);
  const pod = shift(at, [0, 10, 0]);
  const stations = [
    [-16, 4, 1, 6.5],
    [-9, 7, 0, 9],
    [8, 7, 0, 9],
    [14, 5.5, 1, 7.5],
  ] as const;
  p.hull.loft(POD_SECTION, stations, H.panel, { at: pod });
  for (const side of [1, 3]) {
    const stripe = sideStripe(POD_SECTION, side, [0.3, 0.7]);
    p.neon.loft(stripe, stations.slice(1, 3), N, { at: pod }, { open: true });
  }
  barrels(p, shift(pod, [0, 4.3, 14]), [2, 5], [1.3, 7]);
  podDetails(p, at, N);
}

/** The tail missile rack: an armoured box on the tail, six missile tips standing in it. */
function drawRack(p: EnemyParts, at: Vec3): void {
  const box = [
    [-11, 13],
    [11, 13],
    [12, -9],
    [8, -13],
    [-8, -13],
    [-12, -9],
  ] as const;
  p.hull.bevelSlab(box, [7, 9, 13], [0.5, 1.4], H.panel, { at }, H.base);
  missileTips(p, shift(at, [0, 12.6, 0]), [2, 3], [6.2, 1.8]);
  // A neon lip along its front edge.
  const [x, , z] = at;
  edgeStrips(
    p.neon,
    [
      [x - 10, z + 13.6],
      [x + 10, z + 13.6],
    ],
    1,
    [9.4, 10.6],
    N,
  );
  rackDetails(p, at, N);
}

/** The belly plate: an armour shell wrapped over the nose, neon slits along its shoulders. */
function drawPlate(p: EnemyParts, at: Vec3): void {
  const z = at[2];
  const shell = [
    [z - 16, 14.6, -1, 15.9],
    [z - 2, 12.6, -1, 13.7],
    [z + 10, 9.6, -0.5, 10.7],
    [z + 17, 6.3, 0, 7.5],
  ] as const;
  const place = { at: [at[0], 0, 0] as Vec3 };
  p.hull.loft(FIGHTER_SECTION, shell, H.panel, place, { open: true });
  for (const side of [2, 5]) {
    const slit = sideStripe(FIGHTER_SECTION, side, [0.35, 0.65], 1.06);
    p.neon.loft(slit, shell.slice(0, 3), N, place, { open: true });
  }
  plateDetails(p, at, N);
}

/**
 * P07-R05: the Storm Petrel, a seaplane bomber 4.5 L across its wings, magenta neon along the
 * wing edges; a gun pod on each wing, a missile rack on its tail, an armour plate over its nose,
 * and a cockpit turret on the hull (the core).
 */
export function buildStormPetrel(scene: Scene): EnemyModel {
  return buildBossModel(STORM_PETREL, scene, N, {
    core: (p) => {
      drawHull(p);
      drawWings(p);
      drawTail(p);
    },
    parts: {
      'pod-left': drawPod,
      'pod-right': drawPod,
      'missile-rack': drawRack,
      'belly-plate': drawPlate,
    },
  });
}
