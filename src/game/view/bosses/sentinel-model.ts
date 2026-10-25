import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { SENTINEL } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import {
  canopyPaint,
  FIGHTER_SECTION,
  flipX,
  HULL_SECTION,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { hazard, lamps, mast, plate, seam, vent } from './mini-boss-greebles';
import { H, offset, QUARTER, scaled, SHADE, socket, turret, WHITE } from './mini-boss-shapes';

// P07-R05, 1-5: the Sentinel. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];
type Rgb = readonly [number, number, number];

const BLUE = BOSS_LOOK.neon.sentinel ?? [0.15, 0.4, 1];
/** The police red of the Sentinel's other hull (its boss neon colour is the blue). */
const POLICE_RED: Rgb = [1, 0.08, 0.1];
/** Where the hulls run, either side of the centre line: the +X hull is blue, the -X one red. */
const HULL_X = 30;

/** Each hull (loft stations along Z: half width, bottom, top), its nose ahead of the bay. */
const HULL = [
  [-37, 7, -3, 5],
  [-22, 10, -4, 7.5],
  [12, 10, -4, 7.5],
  [34, 7, -3, 5.5],
  [46, 2, -1, 2],
] as const;
/** The cockpit pod between the hulls, its canopy painted on its back. */
const POD = [
  [-27, 7, -2, 6],
  [-12, 11, -3, 9],
  [6, 10, -3, 10],
  [16, 7, -2, 7],
  [23, 3, -1, 3],
] as const;
/** The wing joining the hulls through the pod, and the right tail fin (mirrored on the left). */
const WING = [
  [-14, 12],
  [14, 12],
  [HULL_X, 4],
  [HULL_X, -16],
  [14, -22],
  [-14, -22],
  [-HULL_X, -16],
  [-HULL_X, 4],
] as const;
const FIN = [
  [37, -13],
  [57, -29],
  [57, -34],
  [37, -31],
] as const;
/** Height of the hulls' flat backs. */
const BACK = 7.5;
/** The red hull's radome, a canoe along its back (loft stations). */
const RADOME = [
  [-22, 1.5, 0, 1.5],
  [-16, 3.5, 0, 3.8],
  [-2, 3.5, 0, 3.8],
  [4, 0, 2, 2],
] as const;
/** A panel on the wing between the pod and a hull (around its centre). */
const WING_PANEL = [
  [-3, -12],
  [3, -12],
  [3, -1],
  [-3, 1],
] as const;
/** A patch welded on the red hull's back (the blue hull's extra plate is the same, further back). */
const PATCH = [
  [-34, -6],
  [-26, -7],
  [-26, 2],
  [-33, 3],
] as const;
/** A gun's sponson on the hull's outer flank, around the gun's centre. */
const SPONSON = [
  [-10, 9],
  [5, 11],
  [12, 5],
  [12, -6],
  [5, -11],
  [-10, -9],
] as const;
/** The drone bay around its centre: its housing, and the hatch in its top. */
const BAY = [
  [-9, 15],
  [9, 15],
  [15, 7],
  [15, -12],
  [-15, -12],
  [-15, 7],
] as const;
const HATCH = [
  [-7, 10],
  [7, 10],
  [10, 5],
  [10, -7],
  [-10, -7],
  [-10, 5],
] as const;
const BAY_TOP = 6;

/** A hull at `x`: its neon stripes along both flanks, in `color`, and its tail fin. */
function drawHull({ hull, neon }: EnemyParts, x: number, color: Rgb): void {
  const at: Vec3 = [x, 0, 0];
  hull.loft(HULL_SECTION, HULL, H.base, { at });
  for (const side of [1, 3]) {
    const stripe = sideStripe(HULL_SECTION, side, [0.25, 0.6]);
    neon.loft(stripe, HULL.slice(1, 4), color, { at }, { open: true });
  }
  const fin: readonly OutlinePoint[] = x > 0 ? FIN : flipX(FIN);
  hull.bevelSlab(fin, [-0.8, 0, 1.2], [0.3, 0.6], H.panel, { at: [0, 2, 0] }, H.base);
  const s = Math.sign(x);
  lamps(neon, [[s * 56, 3.2, -32]], 1.4, color);
  vent(hull, [x, BACK, -27], [6, 6], 4);
  vent(hull, [x, BACK, 31], [5, 4], 3);
  for (const z of [-15, 6]) seam(hull, [x - 6, z], [x + 6, z], [BACK, 0.6, 0.3], H.dark);
  // Police livery: a checkered band across the wing beside the hull.
  for (let i = 0; i < 4; i++) {
    const at: Vec3 = [s * (12.5 + i * 2.2), 2.5, -17];
    hull.box([2.2, 0.4, 2.2], i % 2 === 0 ? SHADE.edge : H.dark, { at });
    hull.box([2.2, 0.4, 2.2], i % 2 === 0 ? H.dark : SHADE.edge, { at: offset(at, 0, 0, 2.2) });
  }
}

/**
 * The hulls' differences: the red one carries a radome, its mast and a patched flank; the blue
 * one a searchlight on its bow and an extra armour plate; a whip antenna off-centre on the pod.
 */
function drawGear(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.loft(POD_SECTION, RADOME, H.panel, { at: [-HULL_X, BACK, 0] });
  neon.box([0.6, 0.3, 10], POLICE_RED, { at: [-HULL_X, BACK + 3.8, -12] });
  mast(p, [-HULL_X - 3, BACK, 10], 9, POLICE_RED);
  plate(hull, PATCH, [BACK, 0.6], SHADE.patch);
  hull.cylinder(2.2, 2, 6, H.panel, { at: [HULL_X, BACK, 20] });
  hull.box([3.6, 2.4, 2], H.dark, { at: [HULL_X, BACK + 2, 20.5], pitch: -0.2 });
  charge.box([2.8, 1.6, 0.4], WHITE, { at: [HULL_X, BACK + 2.4, 21.6], pitch: -0.2 });
  plate(hull, scaled(PATCH, 1, 2 * HULL_X, -14), [BACK, 1], H.panel);
  hazard(hull, [HULL_X, BACK + 1, -7], [8, 1.6], 5, 0);
  mast(p, [-3.5, 7.4, -20], 7, BLUE);
  for (const s of SIDES) {
    plate(hull, scaled(WING_PANEL, 1, s * 17.5, 0), [2.5, 0.5], H.base);
    seam(hull, [s * 12, 9], [s * 21, 4.5], [2.5, 0.6, 0.3], H.dark);
  }
}

/** The pod with its light bar, the wing, both hulls, and the core's guns on the wing's front. */
function drawBody(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  hull.bevelSlab(WING, [-1.5, 0, 2.5], [0.6, 1.2], H.panel, {}, H.base);
  hull.loft(FIGHTER_SECTION, POD, H.base, {}, { paint: canopyPaint([1, 2], H.dark) });
  // The light bar on the pod's back, red on one side and blue on the other.
  neon.box([3.6, 1.4, 2.4], BLUE, { at: [2.4, 9, -8] });
  neon.box([3.6, 1.4, 2.4], POLICE_RED, { at: [-2.4, 9, -8] });
  drawHull(p, HULL_X, BLUE);
  drawHull(p, -HULL_X, POLICE_RED);
  for (const s of SIDES) {
    // The core's fan guns, in the wing's leading edge either side of the pod.
    charge.cylinder(1.4, 2.5, 6, WHITE, { at: [s * 15, 1, 10], pitch: QUARTER }, 1);
    p.muzzle([s * 15, 1, 12.5]);
    socket(hull, [s * 38, 1, 8], 7, 1);
  }
  // The drone bay's mounting frame on the pod's nose.
  hull.box([18, 2, 4], H.dark, { at: [0, 0, 23] });
}

/**
 * P07-R05: the Sentinel, a twin-hull police interceptor: a blue hull and a red one joined by a
 * wing through the cockpit pod, a light bar on the pod, a gun on each hull's outer flank and a
 * drone bay at the nose, between the hulls.
 */
export function buildSentinel(scene: Scene): EnemyModel {
  return buildBossModel(SENTINEL, scene, BLUE, {
    core: (p) => {
      drawBody(p);
      drawGear(p);
      for (const s of SIDES) p.reactor([s * HULL_X, 1, -37], 3.6);
      p.reactor([0, 2, -27], 3);
    },
    parts: { 'gun-left': hullGun, 'gun-right': hullGun, 'drone-bay': droneBay },
  });
}

/** A hull gun (P07-R05): a sponson on the hull's outer flank and a twin-barrelled turret. */
function hullGun(p: EnemyParts, at: Vec3): void {
  const r = SENTINEL.stats.parts[0]?.radius ?? 13;
  const outer = at[0] > 0;
  const sponson = outer ? SPONSON : flipX(SPONSON);
  p.hull.bevelSlab(sponson, [-2, 0.5, 4], [0.8, 1.6], H.base, { at }, H.panel);
  const neon = outer ? BLUE : POLICE_RED;
  turret(p, offset(at, 0, 4, 0), {
    radius: r * 0.85,
    barrels: 2,
    gap: 3.6,
    bore: 1.3,
    length: 7,
    neon,
    hatch: outer ? -1 : 1,
  });
}

/** The drone bay (P07-R05): a housing at the nose, a dark hatch and launch lights around it. */
function droneBay({ hull, neon, charge }: EnemyParts, at: Vec3): void {
  hull.bevelSlab(BAY, [-3, 1, BAY_TOP], [1, 2], H.base, { at }, H.panel);
  hull.slab(HATCH, [BAY_TOP, BAY_TOP + 0.2], H.dark, { at });
  // The hatch's two doors' seam, and launch lights at its corners, flashing red and blue.
  neon.box([0.5, 0.3, 16], BLUE, { at: offset(at, 0, BAY_TOP + 0.2, 1.5) });
  for (const [x, z] of scaled(HATCH, 1.12)) {
    charge.box([2, 0.8, 2], WHITE, { at: offset(at, x, BAY_TOP - 0.5, z) });
  }
  for (const s of SIDES) {
    neon.box([0.8, 0.5, 14], s > 0 ? BLUE : POLICE_RED, {
      at: offset(at, s * 13, BAY_TOP - 1.5, -2),
    });
    // A drone docked on each hatch door, ready to drop.
    const drone = offset(at, s * 4, BAY_TOP + 0.2, 2);
    hull.box([4.4, 0.8, 1], H.panel, { at: drone, yaw: 0.8 });
    hull.box([4.4, 0.8, 1], H.panel, { at: drone, yaw: -0.8 });
    neon.box([1, 0.6, 1], s > 0 ? BLUE : POLICE_RED, { at: offset(drone, 0, 0.6, 0) });
  }
  hazard(hull, offset(at, 0, BAY_TOP, -10.5), [14, 1.6], 7, 0);
}
