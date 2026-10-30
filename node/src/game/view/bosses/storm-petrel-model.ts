import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { segmentedBody } from '../../../render/geometry/organic';
import { STORM_PETREL } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { flipX, SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { edgeStrips, shift, sided, turret } from './final-boss-shapes';
import { drawPlate, drawPod, drawRack } from './final-boss-petrel';
import {
  barbs,
  F,
  gland,
  graft,
  hide,
  M,
  polygon,
  ribCage,
  spine,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Storm Petrel, the final boss of 1-1. Logical pixels, nose +Z, Y up
// (towards the camera). A colossal sea-bird creature: a long shelled body, broad membrane wings
// on bone struts with an engine sac on each, magenta veins along the wing edges; its parts are
// growths on its wings, tail and breast.
const N = BOSS_LOOK.neon['storm-petrel'] ?? [1, 0.1, 0.85];

type Vec3 = [number, number, number];

/** The right wing, root inside the body, its tip squared off; the gun pod sits near its tip. */
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
/** The bone struts of the right wing, from its root out (x, z of their ends). */
const STRUTS = [
  [
    [10, 16],
    [74, 2],
  ],
  [
    [10, 4],
    [70, -8],
  ],
  [
    [10, -8],
    [46, -11],
  ],
] as const;
/** The right tailplane and the fin standing at its tip (in its own plane, rolled upright). */
const TAILPLANE = [
  [4, -48],
  [30, -56],
  [31, -62],
  [24, -64],
  [4, -62],
] as const;
const NACELLE_X = 24;
const WING_Y = [6, 7.5, 9.5] as const;

/**
 * The body (P16-R06): a long shelled body from tail to beak, plated grafts on its back, ribs
 * across its shoulders, a magenta vein down its spine, eyes over its beak, and the barbette of
 * the cockpit turret growing out of its back.
 */
function drawHull(p: EnemyParts): void {
  hide(p, {
    tail: -64,
    nose: 56,
    width: 14,
    bottom: -4,
    top: 15,
    segments: 7,
    shell: [F.purple, F.membrane],
    belly: F.crimson,
  });
  ribCage(p, [-22, -12, 14], { halfWidth: 15, y: 3, height: 12, thickness: 1.1 });
  spine(p, [0, 15.5, -50], [0, 15.5, -10], { color: N, width: 1.4 });
  graft(p, polygon(6, 5, [1.2, 1.6]), [13.6, 15], [0, 0, 26]);
  graft(p, polygon(4, 4, [1.4, 1]), [13.6, 14.8], [0, 0, 38], { color: M.base });
  eyes(p, [0, 9.5, 46], { count: 2, size: 1.4, spacing: 7 }, N);
  barbs(p, [0, 14, -32], { count: 3, spacing: 0.1, size: 4, dir: [0, 1, -0.5] });
  // A barbette of flesh rising out of the back, the gun turret on it: the cockpit turret.
  p.flesh.cylinder(8.5, 7.5, 7, F.sinew, { at: [0, 7, 5] }, 8);
  p.neon.box([2, 1.2, 1], N, { at: [0, 4.4, -64.4] });
}

/** The cockpit turret on its barbette (the core's gun), turning around its pivot `at`. */
function cockpitTurret(p: EnemyParts, at: Vec3): void {
  turret(p, shift(at, [0, 14.5, 0]), 8.5, [2, N]);
}

/**
 * Both wings (P16-R06): a membrane on bone struts (big, heavy wings: they stay still), neon along
 * their leading edges, veins across them, an engine sac on each with its reactor, a float of
 * flesh under each root.
 */
function drawWings(p: EnemyParts): void {
  for (const s of SIDES) {
    const flip = (o: readonly OutlinePoint[]): readonly OutlinePoint[] => sided(o, s);
    p.flesh.bevelSlab(flip(WING), WING_Y, [1.2, 1.8], F.membrane, {}, F.purple);
    edgeStrips(p.neon, flip(WING_LEAD), 1.2, [6.9, 8.1], N);
    for (const [[x0, z0], [x1, z1]] of STRUTS) {
      tentacle(p, [s * x0, 9, z0], [s * x1, 9, z1], [0, 1.2, 0], [1.8, 0.5], F.bone, 4);
    }
    veinLine(p, [s * 12, 9.8, -2], [s * 60, 9.7, -6], [0, 0.6, 2], 1.1, N);
    const nacelle: Vec3 = [s * NACELLE_X, 7, 0];
    segmentedBody(
      p.flesh,
      { tail: -19, nose: 19, segments: 3, width: 5.5, bottom: -1, top: 9 },
      F.crimson,
      { at: nacelle },
    );
    graft(p, polygon(5, 3.4), [9, 10], shift(nacelle, [0, 0, 12]));
    p.neon.ring(3.6, 0.8, 6, N, { at: shift(nacelle, [0, 3.8, 19.2]), pitch: Math.PI / 2 });
    reactorSac(p, shift(nacelle, [0, 3.5, -19.2]), 3.2, N);
    segmentedBody(
      p.flesh,
      { tail: -14, nose: 24, segments: 2, width: 4, bottom: 0, top: 5.5 },
      F.sinew,
      { at: [s * 20, -4, 0] },
    );
    gland(p, [s * 76.6, 8.6, -3.5], 1.2, N);
  }
}

/** The tailplanes: membrane on bone, their fins of bone, neon on their leading edges. */
function drawTail(p: EnemyParts): void {
  for (const s of SIDES) {
    const plane = s > 0 ? TAILPLANE : flipX(TAILPLANE);
    p.flesh.bevelSlab(plane, [7, 8, 9.5], [0.6, 1], F.membrane, {}, F.purple);
    tentacle(p, [s * 4, 9, -50], [s * 30, 9, -57], [0, 1, 0], [1.4, 0.4], F.bone, 4);
    tentacle(p, [s * 28, 9, -55], [s * 28, 19, -63], [0, 0, 2], [1.4, 0.2], F.bone, 4);
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
  }
}

/**
 * P07-R05, P16-R06: the Storm Petrel, a colossal sea-bird creature 4.5 L across its wings,
 * magenta veins along the wing edges; a gun growth on each wing, a missile brood on its tail, a
 * bony shell over its breast, and a cockpit turret on its back (the core).
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
    turrets: { core: cockpitTurret },
  });
}
