import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { MESA_FORTRESS } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { edgeStrips, missileTips, mirrored, openHatch, shift, sided } from './final-boss-shapes';
import { lanceDetails, mesaArm, mesaDeck, mesaKeep, siloDetails } from './final-boss-mesa';

// P07-R05: the Mesa Fortress, the final boss of 1-3. Logical pixels, nose +Z, Y up (towards the
// camera). A flying fortress built like the canyon's mesas: two stepped armoured tiers, a fan
// cannon on top, an arm on each side cradling a laser lance, two missile silos on the rear deck,
// red neon slits along its armour.
const H = ENEMY_LOOK.hull;
const N = BOSS_LOOK.neon['mesa-fortress'] ?? [1, 0.1, 0.12];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** The lower tier (right half, front to back): the silos stand on its rear deck. */
const BASE = mirrored([
  [0, 48],
  [22, 46],
  [40, 30],
  [44, 10],
  [44, -36],
  [34, -50],
  [0, -54],
]);
const BASE_TOP = 7;
const KEEP_TOP = 15;
/** The right arm: a beam out from the base, then a rail forward; the lance lies in between. */
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
/** The fan cannon's housing, on the front of the upper tier. */
const FAN_HOUSING = [
  [-12, -8],
  [12, -8],
  [14, 4],
  [7, 12],
  [-7, 12],
  [-14, 4],
] as const;
const FAN_AT: Vec3 = [0, KEEP_TOP, 26];
/** The lance's housing around its centre, its emitter barrel and lens (lathe profiles). */
const LANCE_HOUSING = [
  [-10, 10],
  [10, 10],
  [12, 2],
  [11, -14],
  [7, -18],
  [-7, -18],
  [-11, -14],
  [-12, 2],
] as const;
const LENS = [
  [0, 0],
  [4, 1],
  [3.2, 3],
  [0, 3.8],
] as const;

/** The two tiers, the arms, the red slits along the armour, and the reactors in the back wall. */
function drawBody(p: EnemyParts): void {
  p.hull.bevelSlab(BASE, [-6, 0, BASE_TOP], [3, 4], H.base, {}, H.panel);
  mesaKeep(p, N);
  mesaDeck(p);
  const rim: OutlinePoint[] = [
    [-34, 28.5],
    [-19, 41.5],
    [19, 41.5],
    [34, 28.5],
  ];
  edgeStrips(p.neon, rim, 1.2, [BASE_TOP - 0.2, BASE_TOP + 0.5], N);
  for (const s of SIDES) {
    p.hull.bevelSlab(sided(ARM, s), [-4, 0, 6], [1, 1.5], H.base, {}, H.panel);
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
    mesaArm(p, s, N);
    p.reactor([s * 10, 0.5, -53.4], 3.8);
    p.reactor([s * 24, 0.5, -51.8], 3.8);
  }
}

/** The fan cannon on top (the core's gun): a housing and five barrels fanned out forward. */
function drawFanCannon(p: EnemyParts): void {
  p.hull.bevelSlab(FAN_HOUSING, [0, 0, 5], [0, 1.5], H.dark, { at: FAN_AT }, H.panel);
  for (let k = 0; k < 5; k++) {
    const yaw = (k - 2) * 0.28;
    const out = (r: number): Vec3 => shift(FAN_AT, [Math.sin(yaw) * r, 2.6, 4 + Math.cos(yaw) * r]);
    p.hull.cylinder(1.6, 9, 6, H.dark, { at: out(4), pitch: QUARTER, yaw }, 1.3);
    p.charge.cylinder(1.5, 2, 6, WHITE, { at: out(13), pitch: QUARTER, yaw });
    p.muzzle(out(15));
  }
}

/** A laser lance in its cradle: an armoured housing, a long barrel ringed with neon, its lens. */
function drawLance(p: EnemyParts, at: Vec3): void {
  p.hull.bevelSlab(LANCE_HOUSING, [-2, 2, 11], [1.5, 2.5], H.panel, { at }, H.base);
  const [x, , z] = at;
  edgeStrips(
    p.neon,
    [
      [x, z - 13],
      [x, z + 4],
    ],
    1.4,
    [10.8, 11.4],
    N,
  );
  const barrel = shift(at, [0, 6, 8]);
  p.hull.cylinder(5.5, 28, 8, H.dark, { at: barrel, pitch: QUARTER }, 3.6);
  for (const dz of [6, 13, 20]) {
    const r = 5.5 - (dz / 28) * 1.9 + 0.3;
    p.neon.ring(r, 1.2, 8, N, { at: shift(barrel, [0, 0, dz]), pitch: QUARTER });
  }
  // The lens glows through the warning line and while the laser fires.
  p.charge.lathe(LENS, 8, WHITE, { at: shift(barrel, [0, 0, 27.5]), pitch: QUARTER });
  p.muzzle(shift(barrel, [0, 0, 31.3]), 'laser');
  lanceDetails(p, at);
}

/** A missile silo on the rear deck: a hexagonal housing, its hatch open on four missile tips. */
function drawSilo(p: EnemyParts, at: Vec3): void {
  const housing = [
    [12.5, 0],
    [12.5, 2.5],
    [10.5, 5],
  ] as const;
  const base = shift(at, [0, BASE_TOP, 0]);
  p.hull.lathe(housing, 6, H.panel, { at: base });
  p.neon.ring(12.7, 0.8, 6, N, { at: shift(base, [0, 0.6, 0]) });
  const hatch = shift(base, [0, 5, 0]);
  openHatch(p, hatch, [12, 15]);
  missileTips(p, shift(hatch, [0, 0.4, 0]), [2, 2], [5.6, 1.9]);
  siloDetails(p, at);
}

/**
 * P07-R05: the Mesa Fortress, a flying fortress 5 L across with red neon slits; a laser lance
 * in each side arm, two missile silos on its rear deck, and a fan cannon on its heavy armoured
 * central block (the core).
 */
export function buildMesaFortress(scene: Scene): EnemyModel {
  return buildBossModel(MESA_FORTRESS, scene, N, {
    core: (p) => {
      drawBody(p);
      drawFanCannon(p);
    },
    parts: {
      'lance-left': drawLance,
      'lance-right': drawLance,
      'silo-left': drawSilo,
      'silo-right': drawSilo,
    },
  });
}
