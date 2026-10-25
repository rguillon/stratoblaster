import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { DUST_DEVIL } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { around, canopyPaint, FIGHTER_SECTION, POD_SECTION, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { H, scaled, WHITE } from './mini-boss-shapes';

// P07-R05, 1-3: the Dust Devil. Logical pixels, nose +Z, Y up (towards the camera).
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
/** The cockpit faired onto the disc's front, and the engine fairing on its back (loft stations). */
const COCKPIT = [
  [2, 6, 1, 7],
  [12, 6, 1, 6.5],
  [19, 3.5, 0.5, 3.5],
  [23, 0, 1.5, 1.5],
] as const;
const ENGINES = [
  [-23, 4.5, 1, 7],
  [-16, 5, 1, 8],
  [-6, 3, 2, 7.5],
] as const;
/** The turning ring: its hub collar round the disc and its rim carrying the pods (lathe profiles). */
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
/** A spoke from the hub to the rim (towards +Z), and a swept, knife-edged blade between spokes. */
const SPOKE = [
  [-2.6, 21],
  [2.6, 21],
  [1.6, 39],
  [-1.6, 39],
] as const;
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

/** The core's disc with its amber band, cockpit, engines and ring emitter. */
function drawCore({ hull, neon, charge, reactor }: EnemyParts): void {
  hull.lathe(GYRO_DISC, 12, H.base, { yaw: Math.PI / 12 });
  neon.ring(18.2, 1.2, 12, AMBER, { at: [0, -0.4, 0], yaw: Math.PI / 12 });
  hull.loft(FIGHTER_SECTION, COCKPIT, H.panel, {}, { paint: canopyPaint([0, 1], H.dark) });
  for (const s of SIDES) {
    hull.loft(POD_SECTION, ENGINES, H.panel, { at: [s * 6, 0, 0] });
    neon.box([0.6, 0.4, 8], AMBER, { at: [s * 6, 8, -17] });
    reactor([s * 6, 4, -23], 2.6);
  }
  // Brightens as the core's next volley charges.
  charge.lathe(EMITTER, 6, WHITE);
}

/** The turning ring (P07-R05): a hub collar, three spokes to the pods, swept blades between. */
function drawRing({ hull, neon }: EnemyParts): void {
  hull.lathe(HUB, 12, H.panel, {}, false);
  hull.lathe(RIM, 18, H.base, {}, false);
  neon.ring(43.1, 0.8, 18, AMBER, { at: [0, -0.4, 0] });
  for (const a of around(3)) {
    hull.bevelSlab(SPOKE, [-1.5, 0, 1.2], [0.4, 0.7], H.panel, { yaw: a }, H.base);
    hull.bevelSlab(BLADE, [-0.6, 0, 0.6], [0.4, 0.6], H.base, { yaw: a + Math.PI / 3 }, H.panel);
  }
}

/**
 * P07-R05: the Dust Devil, a gyro gunship with amber neon: a domed disc with a cockpit at its
 * front, and a slowly turning blade ring carrying three blade pods.
 */
export function buildDustDevil(scene: Scene): EnemyModel {
  return buildBossModel(DUST_DEVIL, scene, AMBER, {
    core: drawCore,
    ring: drawRing,
    parts: { 'blade-1': bladePod, 'blade-2': bladePod, 'blade-3': bladePod },
  });
}

/** A blade pod on the ring (P07-R05): an armoured airfoil, a canopy, a muzzle at each tip. */
function bladePod({ hull, neon, charge }: EnemyParts, at: Vec3): void {
  const place = { at, yaw: Math.atan2(at[0], at[2]) };
  hull.bevelSlab(scaled(POD, POD_SCALE), [-3, 0, POD_TOP], [1, 1.8], H.base, place, H.panel);
  neon.slab(POD_LIGHT, [POD_TOP, POD_TOP + 0.3], AMBER, place);
  hull.lathe(POD_DOME, 6, H.dark, { at: [at[0], POD_TOP, at[2]] });
  for (const muzzle of MUZZLES) charge.slab(scaled(muzzle, POD_SCALE), [-1.6, 2.2], WHITE, place);
}
