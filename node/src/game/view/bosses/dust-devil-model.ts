import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { DUST_DEVIL } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { organ } from '../../../render/geometry/organic';
import { around, SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { scaled, WHITE } from './mini-boss-shapes';
import { F, graft, polygon, tentacle, veinLine } from './world-1-organic-kit';

// P07-R05, P16-R05, 1-3: the Dust Devil. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const AMBER = BOSS_LOOK.neon['dust-devil'] ?? [1, 0.75, 0.15];

/** The core: a gyro disc (a lathe profile), domed on top, and its ring emitter on the dome. */
const GYRO_DISC = [
  [0, -4],
  [14, -4],
  [18, -1],
  [18, 1.5],
  [15, 4],
  [9, 7],
  [0, 8],
] as const;
const EMITTER = [
  [3.6, 7.6],
  [2.4, 9.4],
  [0, 10],
] as const;
/** The turning ring: its collar round the bell and its rim carrying the pods (lathe profiles). */
const HUB = [
  [18.5, -3],
  [22, -3],
  [22.5, 0],
  [21, 1.5],
  [18.5, 1.5],
  [18.5, -3],
] as const;
const RIM = [
  [38, -2],
  [41.5, -2.5],
  [43, 0],
  [41.5, 2],
  [38, 1.5],
  [38, -2],
] as const;
/** A swept membrane fin between two spokes. */
const BLADE = [
  [-3, 21],
  [4, 21],
  [1, 39],
  [-6, 39],
] as const;
/**
 * A blade pod around its centre, outwards along +Z, across along X: a swept airfoil whose two
 * tips carry the muzzles (it fires both ways along the ring), and the muzzles' outlines.
 */
const POD = [
  [-14, -1],
  [-9, 5],
  [3, 8],
  [12, 4],
  [14, 0],
  [7, -6],
  [-7, -7],
] as const;
const MUZZLES = [
  [
    [-14.6, -1.2],
    [-12, 2.6],
    [-11, 0.6],
  ],
  [
    [14.6, 0],
    [12.4, 3.6],
    [11.6, 1],
  ],
] as const;
/** The amber light along a pod's back, and its canopy (a lathe profile). */
const POD_LIGHT = [
  [-9, 1],
  [9, 2.2],
  [9, 3.2],
  [-9, 2],
] as const;
const POD_DOME = [
  [4, 0],
  [3, 2.2],
  [0, 3],
] as const;
const POD_TOP = 3.5;
/** The pods are drawn this much bigger than their outlines. */
const POD_SCALE = 1.15;

/**
 * The core (P16-R05): a swollen fleshy bell (the gyro disc grown over), plated ribs radiating
 * across it, the amber charge gland on its crown (the ring emitter), eyes at its front, its
 * reactors in sacs behind.
 */
function drawCore(p: EnemyParts): void {
  p.flesh.lathe(GYRO_DISC, 10, F.sinew, { yaw: Math.PI / 10 });
  p.neon.ring(18.2, 1.2, 10, AMBER, { at: [0, -0.4, 0], yaw: Math.PI / 10 });
  organ(p.flesh, 9, 8, F.crimson, { at: [0, 4, 0] }, 0.25);
  for (const a of around(8)) {
    const [x, z] = [Math.sin(a), Math.cos(a)];
    tentacle(p, [x * 5, 8, z * 5], [x * 18, 1.6, z * 18], [0, 2.2, 0], [1.1, 0.6], F.bone, 3);
    if (Math.abs(z) < 0.95) {
      graft(p, polygon(4, 2.6, [0.8, 1.4]), [4.4, 5.6], [x * 13, 0, z * 13], { yaw: a });
    }
  }
  for (const s of SIDES) {
    veinLine(p, [s * 4, 7.5, -3], [s * 15, 3, -10], [0, 1.5, 0], 0.9, AMBER);
    reactorSac(p, [s * 6, 4, -23], 2.6, AMBER);
    tentacle(p, [s * 5, 3, -14], [s * 6, 4, -21], [0, 1, 0], [3, 2.6], F.crimson, 5);
  }
  eyes(p, [0, 4.5, 16], { count: 3, size: 1, spacing: 3 }, AMBER);
  graft(p, polygon(5, 4, [1.2, 0.8]), [3, 4.4], [0, 0, 13]);
  // Brightens as the core's next volley charges; its bullets leave from its top.
  p.charge.lathe(EMITTER, 6, WHITE);
  p.muzzle([0, 10, 0]);
}

/**
 * The turning ring (P07-R05, P16-R05): a sinew collar round the bell, a fleshy rim, three
 * tentacle spokes out to the pods and membrane fins between them.
 */
function drawRing(p: EnemyParts): void {
  p.flesh.lathe(HUB, 10, F.purple, {}, false);
  p.flesh.lathe(RIM, 15, F.sinew, {}, false);
  p.neon.ring(43.1, 0.8, 15, AMBER, { at: [0, -0.4, 0] });
  for (const a of around(3)) {
    const [x, z] = [Math.sin(a), Math.cos(a)];
    tentacle(p, [x * 20, 0, z * 20], [x * 39, 0, z * 39], [0, 1.5, 0], [2.2, 1.6], F.crimson, 4);
    p.flesh.bevelSlab(BLADE, [-0.6, 0, 0.6], [0.4, 0.6], F.membrane, { yaw: a + Math.PI / 3 });
    const fin = a + Math.PI / 3;
    tentacle(
      p,
      [Math.sin(fin) * 21, 0.6, Math.cos(fin) * 21],
      [Math.sin(fin) * 38, 0.6, Math.cos(fin) * 38],
      [0, 0, 0],
      [0.6, 0.3],
      F.bone,
      3,
    );
    veinLine(p, [x * 21, 1.8, z * 21], [x * 38, 1.6, z * 38], [0, 0.8, 0], 0.7, AMBER);
  }
}

/**
 * P07-R05, P16-R05: the Dust Devil, a desert whirl-jelly with amber veins: a swollen fleshy
 * bell, and a slowly turning ring of sinew carrying three clinging sand rays.
 */
export function buildDustDevil(scene: Scene): EnemyModel {
  return buildBossModel(DUST_DEVIL, scene, AMBER, {
    core: drawCore,
    ring: drawRing,
    parts: { 'blade-1': bladePod, 'blade-2': bladePod, 'blade-3': bladePod },
  });
}

/**
 * A blade pod on the ring (P07-R05, P16-R05): a sand ray clinging to the rim, its wide fleshy
 * wings plated at the front, a bone barb at each wing tip carrying a muzzle.
 */
function bladePod(p: EnemyParts, at: Vec3): void {
  const place = { at, yaw: Math.atan2(at[0], at[2]) };
  p.flesh.bevelSlab(
    scaled(POD, POD_SCALE),
    [-3, 0, POD_TOP - 1],
    [1, 2.4],
    F.sinew,
    place,
    F.crimson,
  );
  organ(p.flesh, 5, 6, F.crimson, { at: [at[0], POD_TOP - 2.5, at[2]] }, 0.45);
  p.vein.slab(POD_LIGHT, [POD_TOP - 0.6, POD_TOP - 0.3], AMBER, place);
  p.neon.lathe(POD_DOME, 5, AMBER, { at: [at[0], POD_TOP + 1.6, at[2]] });
  for (const muzzle of MUZZLES) {
    p.charge.slab(scaled(muzzle, POD_SCALE), [-1.6, 2.2], WHITE, place);
  }
  graft(p, scaled(POD.slice(1, 4), 0.8, 0, 0), [POD_TOP - 1.2, POD_TOP], at, { yaw: place.yaw });
  const put = (x: number, z: number): [number, number, number] => [
    at[0] + x * Math.cos(place.yaw) + z * Math.sin(place.yaw),
    POD_TOP,
    at[2] - x * Math.sin(place.yaw) + z * Math.cos(place.yaw),
  ];
  // Its bullets leave from the tips, both ways along the ring.
  for (const side of [-1, 1]) {
    const [x, , z] = put(side * 14.6 * POD_SCALE, side < 0 ? -1.2 * POD_SCALE : 0);
    p.muzzle([x, 0.3, z]);
  }
}
