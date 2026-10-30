import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { MESA_FORTRESS } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { edgeStrips, mirrored, shift, sided } from './final-boss-shapes';
import { BASE_TOP, drawLance, drawSilo } from './final-boss-mesa';
import {
  barbs,
  F,
  gland,
  graft,
  hide,
  M,
  mantle,
  polygon,
  ribCage,
  spine,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Mesa Fortress, the final boss of 1-3. Logical pixels, nose +Z, Y up
// (towards the camera). A colossal canyon tortoise: a wide skirt of hide under a high, stepped
// shell like the mesas, plated with grafted armour, a fan cannon on its brow, a forelimb on each
// side cradling a laser lance, two spore silos on its back, red veins along its shell.
const N = BOSS_LOOK.neon['mesa-fortress'] ?? [1, 0.1, 0.12];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** The skirt of hide (right half, front to back): the silos stand on its rear. */
const BASE = mirrored([
  [0, 48],
  [22, 46],
  [40, 30],
  [44, 10],
  [44, -36],
  [34, -50],
  [0, -54],
]);
/** The right forelimb: an upper limb out from the body, then a forearm forward. */
const ARM = [
  [40, -6],
  [72, -6],
  [74, 26],
  [78, 32],
  [85, 30],
  [86, -16],
  [80, -23],
  [40, -24],
] as const;
/** The fan cannon's housing, on the brow. */
const FAN_HOUSING = [
  [-12, -8],
  [12, -8],
  [14, 4],
  [7, 12],
  [-7, 12],
  [-14, 4],
] as const;
const FAN_AT: Vec3 = [0, 15, 26];
/** Grafted armour plates on the shell (x, z, radius), mirrored. */
const SHELL_PLATES = [
  [14, -26, 6],
  [20, 2, 5],
  [10, 14, 4.5],
] as const;

/** The skirt, the stepped shell with its ribs, veins and grafted plates, the head at its front. */
function drawBody(p: EnemyParts): void {
  mantle(p, BASE, [-6, BASE_TOP], F.sinew, N);
  hide(p, {
    tail: -50,
    nose: 30,
    width: 38,
    bottom: BASE_TOP - 2,
    top: 22,
    segments: 4,
    shell: [F.crimson, F.membrane],
    belly: F.purple,
  });
  hide(p, {
    tail: -36,
    nose: 18,
    width: 22,
    bottom: 14,
    top: 30,
    segments: 3,
    shell: [F.sinew, F.crimson],
    belly: F.crimson,
  });
  ribCage(p, [-40, 22], { halfWidth: 34, y: BASE_TOP, height: 13, thickness: 1.4 }, F.bone);
  spine(p, [0, 30.5, -32], [0, 30.5, 14], { color: N, width: 1.6 });
  const rim: OutlinePoint[] = [
    [-34, 28.5],
    [-19, 41.5],
    [19, 41.5],
    [34, 28.5],
  ];
  edgeStrips(p.neon, rim, 1.2, [BASE_TOP - 0.2, BASE_TOP + 0.5], N);
  for (const s of SIDES) {
    for (const [x, z, r] of SHELL_PLATES) {
      graft(p, polygon(6, r, [1, 1.3]), [17, 18.4], [s * x, 0, z], { color: M.base });
    }
    for (const z of [-30, -8]) {
      veinLine(p, [s * 18, 27, z], [s * 38, 12, z - 6], [s * 3, 4, 0], 1.3, N);
    }
    gland(p, [s * 12, 29, 0], 2.2, N);
    reactorSac(p, [s * 10, 0.5, -53.4], 3.8, N);
    reactorSac(p, [s * 24, 0.5, -51.8], 3.8, N);
  }
  eyes(p, [0, 12, 40], { count: 2, size: 1.6, spacing: 10 }, N);
  barbs(p, [0, 7, 46], { count: 4, spacing: 6, size: 3, dir: [0, -0.2, 1] });
}

/** The forelimbs: a scaly limb out to each lance's cradle, a bone claw at its front. */
function drawArms(p: EnemyParts): void {
  for (const s of SIDES) {
    p.flesh.bevelSlab(sided(ARM, s), [-4, 0, 5], [1, 2], F.sinew, {}, F.crimson);
    tentacle(p, [s * 36, 6, -15], [s * 76, 7, -14], [0, 3, 0], [6, 4], F.crimson, 5);
    graft(p, polygon(4, 5, [2, 0.9]), [8.5, 9.6], [s * 56, 0, -16]);
    for (const dx of [-3, 3]) {
      tentacle(p, [s * (81 + dx), 4, 26], [s * (80 + dx), 0, 36], [0, 2, 0], [1.6, 0.1], F.bone, 3);
    }
    edgeStrips(
      p.neon,
      sided(
        [
          [79, 27],
          [81, -15],
        ],
        s,
      ),
      1,
      [5.8, 6.4],
      N,
    );
  }
}

/**
 * The fan cannon on the brow (the core's gun): a grafted housing and five barrels fanned out
 * forward, turning around the hub of its barrels (its pivot).
 */
function drawFanCannon(p: EnemyParts): void {
  p.hull.bevelSlab(FAN_HOUSING, [0, 0, 5], [0, 1.5], M.dark, { at: FAN_AT }, M.panel);
  for (let k = 0; k < 5; k++) {
    const yaw = (k - 2) * 0.28;
    const out = (r: number): Vec3 => shift(FAN_AT, [Math.sin(yaw) * r, 2.6, 4 + Math.cos(yaw) * r]);
    p.hull.cylinder(1.6, 9, 6, M.dark, { at: out(4), pitch: QUARTER, yaw }, 1.3);
    p.charge.cylinder(1.5, 2, 6, WHITE, { at: out(13), pitch: QUARTER, yaw });
    p.muzzle(out(15));
  }
}

/**
 * P07-R05, P16-R06: the Mesa Fortress, a colossal canyon tortoise 5 L across with red veins; a
 * laser lance in each forelimb, two spore silos on its back, and a fan cannon on its armoured
 * brow (the core).
 */
export function buildMesaFortress(scene: Scene): EnemyModel {
  return buildBossModel(MESA_FORTRESS, scene, N, {
    core: (p) => {
      drawBody(p);
      drawArms(p);
    },
    parts: {
      'lance-left': drawLance,
      'lance-right': drawLance,
      'silo-left': drawSilo,
      'silo-right': drawSilo,
    },
    turrets: { core: drawFanCannon },
  });
}
