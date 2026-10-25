import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { DUST_DEVIL } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { around, canopyPaint, FIGHTER_SECTION, POD_SECTION, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import type { OutlinePoint } from '../../../render/geometry/outline';
import { dish, hazard, mast, plate, seam, vent } from './mini-boss-greebles';
import { cog, conduit, GEAR, glowLine } from './mini-boss-mechanism';
import { H, QUARTER, scaled, SHADE, WHITE } from './mini-boss-shapes';

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
/** A patch on the first pod's armour (around the pod's centre). */
const PATCH = [
  [-13, 1],
  [-8, 5.5],
  [-5, 3],
  [-9, -1],
] as const;
/** The pods are drawn this much bigger than their outlines. */
const POD_SCALE = 1.15;

/** The armour sectors on the disc's left (+X) shoulder, as turns from the nose (mirrored). */
const SECTORS = [
  [0.62, 1.32],
  [1.82, 2.52],
] as const;

/** An annular sector seen from above, turns `a0` to `a1` from +Z, radii `r0` to `r1`. */
function sector(a0: number, a1: number, r0: number, r1: number): OutlinePoint[] {
  const arc = (r: number): OutlinePoint[] =>
    Array.from({ length: 4 }, (_, k): OutlinePoint => {
      const a = a0 + ((a1 - a0) * k) / 3;
      return [Math.sin(a) * r, Math.cos(a) * r];
    });
  return [...arc(r1), ...arc(r0).reverse()];
}

/**
 * The disc's fat armour sectors (phase 7 review), and in the gaps between them the pinions that
 * drive the ring, their conduits and amber light; a dish to port, an ammunition drum and a mast
 * to starboard.
 */
function drawArmour(p: EnemyParts): void {
  const { hull, neon } = p;
  for (const s of SIDES) {
    for (const [a0, a1] of SECTORS) {
      hull.bevelSlab(
        sector(s * a0, s * a1, 11.5, 19.5),
        [3, 4, 7.5],
        [0, 1.6],
        H.base,
        {},
        H.panel,
      );
    }
    cog(hull, [s * 17, 1.4, 0], 2.8, 8, 0.2);
    conduit(hull, [s * 9.5, 6.5, 0], [s * 15, 3, 0], 0.8, 2);
    glowLine(neon, [s * 11, 2.6, 2.2], [s * 18, 1.2, 2.2], 0.9, AMBER);
    glowLine(neon, [s * 11, 2.6, -2.2], [s * 18, 1.2, -2.2], 0.9, AMBER);
  }
  dish(hull, [12.5, 7.5, 7.5], 3.2, 0.5, 0.9);
  hull.cylinder(2.6, 6, 8, SHADE.patch, { at: [-10, 9.6, -11], roll: QUARTER, yaw: 0.6 });
  hazard(hull, [-14, 7.5, 7.6], [4, 2], 3, -1);
  mast(p, [-5, 7.2, -4], 6, AMBER);
}

/** The core's disc with its amber band, cockpit, engines and ring emitter. */
function drawCore(p: EnemyParts): void {
  const { hull, neon, charge, reactor } = p;
  hull.lathe(GYRO_DISC, 12, H.base, { yaw: Math.PI / 12 });
  neon.ring(18.2, 1.2, 12, AMBER, { at: [0, -0.4, 0], yaw: Math.PI / 12 });
  hull.loft(FIGHTER_SECTION, COCKPIT, H.panel, {}, { paint: canopyPaint([0, 1], H.dark) });
  for (const s of SIDES) {
    hull.loft(POD_SECTION, ENGINES, H.panel, { at: [s * 6, 0, 0] });
    neon.box([0.6, 0.4, 8], AMBER, { at: [s * 6, 8, -17] });
    reactor([s * 6, 4, -23], 2.6);
  }
  // Brightens as the core's next volley charges; its bullets leave from its top.
  charge.lathe(EMITTER, 6, WHITE);
  p.muzzle([0, 10, 0]);
  drawArmour(p);
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
  drawRingDetail(hull);
}

/** The ring's gear teeth round the hub, its rim plates, and one hazard-striped spoke. */
function drawRingDetail(hull: EnemyParts['hull']): void {
  for (const a of around(24)) {
    hull.box([1.4, 1.2, 1.8], GEAR, { at: [Math.sin(a) * 21, 1.2, Math.cos(a) * 21], yaw: a });
  }
  for (const a of around(6)) {
    const rim = a + Math.PI / 6;
    const at: [number, number, number] = [Math.sin(rim) * 40, 1.7, Math.cos(rim) * 40];
    hull.box([5, 0.6, 2.2], (a * 10) % 3 < 1.5 ? SHADE.edge : H.panel, { at, yaw: rim });
  }
  hazard(hull, [0, 1.2, 30], [3, 9], 3, 0);
  seam(hull, [-3.6, 25], [3.6, 25], [1.2, 0.6, 0.4], SHADE.edge);
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
function bladePod({ hull, neon, charge, muzzle }: EnemyParts, at: Vec3): void {
  const place = { at, yaw: Math.atan2(at[0], at[2]) };
  hull.bevelSlab(scaled(POD, POD_SCALE), [-3, 0, POD_TOP], [1, 1.8], H.base, place, H.panel);
  neon.slab(POD_LIGHT, [POD_TOP, POD_TOP + 0.3], AMBER, place);
  hull.lathe(POD_DOME, 6, H.dark, { at: [at[0], POD_TOP, at[2]] });
  for (const muzzle of MUZZLES) charge.slab(scaled(muzzle, POD_SCALE), [-1.6, 2.2], WHITE, place);
  const put = (x: number, z: number): [number, number, number] => [
    at[0] + x * Math.cos(place.yaw) + z * Math.sin(place.yaw),
    POD_TOP,
    at[2] - x * Math.sin(place.yaw) + z * Math.cos(place.yaw),
  ];
  // Its bullets leave from the tips, both ways along the ring.
  for (const side of [-1, 1]) {
    const [x, , z] = put(side * 14.6 * POD_SCALE, side < 0 ? -1.2 * POD_SCALE : 0);
    muzzle([x, 0.3, z]);
  }
  vent(hull, put(-8.5, -2), [6, 3], 3, place.yaw + Math.PI / 2);
  vent(hull, put(8.5, -1.5), [6, 3], 3, place.yaw + Math.PI / 2);
  seam(hull, ...edge(put(-6, -5), put(6, -5)), [POD_TOP, 0.6, 0.4], H.dark);
  // The first pod (at the ring's nose at rest) was patched after a hit.
  if (Math.abs(at[0]) < 1) plate(hull, scaled(PATCH, 1), [POD_TOP, 0.5], SHADE.patch, place);
}

/** The flat ends of a seam from two 3D points. */
function edge(
  a: readonly [number, number, number],
  b: readonly [number, number, number],
): [readonly [number, number], readonly [number, number]] {
  return [
    [a[0], a[2]],
    [b[0], b[2]],
  ];
}
