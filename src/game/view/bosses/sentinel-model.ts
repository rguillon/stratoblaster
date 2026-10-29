import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { SENTINEL } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { membraneWing, organ, segmentedBody } from '../../../render/geometry/organic';
import { flipX, SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { lamps, mast } from './mini-boss-greebles';
import { offset, QUARTER, scaled, socket, turret, WHITE } from './mini-boss-shapes';
import {
  barbs,
  F,
  gland,
  graft,
  growth,
  hide,
  M,
  mantle,
  polygon,
  ribCage,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R05, 1-5: the Sentinel. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];
type Rgb = readonly [number, number, number];

const BLUE = BOSS_LOOK.neon.sentinel ?? [0.15, 0.4, 1];
/** The police red of the Sentinel's other hull (its boss neon colour is the blue). */
const POLICE_RED: Rgb = [1, 0.08, 0.1];
/** Where the hulls run, either side of the centre line: the +X hull is blue, the -X one red. */
const HULL_X = 30;

/** The membrane joining the bodies through the thorax, and the right tail fin (mirrored). */
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
/** A plate on the membrane between the thorax and a body (around its centre). */
const WING_PANEL = [
  [-3, -12],
  [3, -12],
  [3, -1],
  [-3, 1],
] as const;
/** A plate grafted on the red body's back (the blue body's extra plate is the same, further back). */
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

/**
 * A body at `x` (P16-R05): a long segmented worm along Z, a shell plated on its back, lit veins
 * along its flanks in `color`, its tail fin a membrane on bone struts.
 */
function drawHull(p: EnemyParts, x: number, color: Rgb): void {
  const at: Vec3 = [x, 0, 0];
  hide(p, {
    tail: -38,
    nose: 47,
    width: 10,
    bottom: -4,
    top: BACK,
    segments: 4,
    shell: [F.purple, F.membrane],
    belly: F.crimson,
    at,
  });
  const s = Math.sign(x);
  for (const side of SIDES) {
    veinLine(p, [x + side * 9, 2.5, -24], [x + side * 9, 2.5, 30], [side, 0.5, 0], 1.1, color);
  }
  p.neon.box([0.6, 0.3, 30], color, { at: [x, BACK + 0.2, -4] });
  const fin: readonly OutlinePoint[] = x > 0 ? FIN : flipX(FIN);
  const [root, ...tips] = fin;
  membraneWing(p.flesh, p.flesh, { root: root ?? [x, -13], tips, y: 2, thickness: 1, strut: 1.2 }, [
    F.membrane,
    F.bone,
  ]);
  lamps(p.neon, [[s * 56, 3.2, -32]], 1.4, color);
  graft(p, polygon(4, 4, [1, 1.8]), [BACK - 0.2, BACK + 0.8], [x, 0, 31]);
  barbs(p, [x, BACK + 0.5, -20], { count: 3, spacing: 4, size: 2.5, dir: [0, 1, -0.4] });
}

/**
 * Grafts on the bodies (P16-R05): a radome and mast on the red one, a searchlight and an extra
 * plate on the blue one, a whip antenna off-centre on the thorax.
 */
function drawGear(p: EnemyParts): void {
  mast(p, [-HULL_X - 3, BACK, 10], 9, POLICE_RED);
  graft(p, PATCH, [BACK, BACK + 0.8], [0, 0, 0], { color: M.base });
  p.hull.cylinder(2.2, 2, 6, M.panel, { at: [HULL_X, BACK, 20] });
  p.hull.box([3.6, 2.4, 2], M.dark, { at: [HULL_X, BACK + 2, 20.5], pitch: -0.2 });
  p.charge.box([2.8, 1.6, 0.4], WHITE, { at: [HULL_X, BACK + 2.4, 21.6], pitch: -0.2 });
  graft(p, scaled(PATCH, 1, 2 * HULL_X, -14), [BACK, BACK + 1], [0, 0, 0]);
  mast(p, [-3.5, 9.4, -20], 7, BLUE);
  for (const s of SIDES) {
    graft(p, scaled(WING_PANEL, 1, s * 17.5, 0), [2.5, 3], [0, 0, 0], { color: M.base });
    veinLine(p, [s * 8, 5, 0], [s * 22, 2.2, -14], [0, 1, 0], 0.8, s > 0 ? BLUE : POLICE_RED);
  }
}

/** The thorax with its glands, the membrane joining the bodies, both bodies, the core's guns. */
function drawBody(p: EnemyParts): void {
  mantle(p, WING, [-1.5, 2.5], F.membrane);
  ribCage(p, [-14, 2], { halfWidth: HULL_X - 6, y: 1, height: 3, thickness: 0.9 });
  segmentedBody(
    p.flesh,
    { tail: -28, nose: 24, segments: 3, width: 11, bottom: -3, top: 10 },
    F.crimson,
  );
  eyes(p, [0, 7, 18], { count: 2, size: 1.2, spacing: 4 }, BLUE);
  // The light bar on the thorax's back: a red gland and a blue one.
  gland(p, [2.4, 9, -8], 1.6, BLUE);
  gland(p, [-2.4, 9, -8], 1.6, POLICE_RED);
  p.neon.box([3.6, 0.6, 2.4], BLUE, { at: [2.4, 10.4, -12] });
  p.neon.box([3.6, 0.6, 2.4], POLICE_RED, { at: [-2.4, 10.4, -12] });
  drawHull(p, HULL_X, BLUE);
  drawHull(p, -HULL_X, POLICE_RED);
  for (const s of SIDES) {
    // The core's fan guns, grafted in the membrane's leading edge either side of the thorax.
    p.hull.cylinder(1.8, 3, 6, M.dark, { at: [s * 15, 1, 7], pitch: QUARTER });
    p.charge.cylinder(1.4, 2.5, 6, WHITE, { at: [s * 15, 1, 10], pitch: QUARTER }, 1);
    p.muzzle([s * 15, 1, 12.5]);
    socket(p.hull, [s * 38, 1, 8], 7, 1);
  }
  // The brood pouch's grafted frame on the thorax's front.
  p.hull.box([18, 2, 4], M.dark, { at: [0, 0, 23] });
}

/**
 * P07-R05, P16-R05: the Sentinel, a twin-bodied city hunter: a blue body and a red one joined
 * by a membrane through its thorax, police-light glands on its back, a gun growth on each body's
 * outer flank and a brood pouch at the nose, between the bodies.
 */
export function buildSentinel(scene: Scene): EnemyModel {
  return buildBossModel(SENTINEL, scene, BLUE, {
    core: (p) => {
      drawBody(p);
      drawGear(p);
      for (const s of SIDES) reactorSac(p, [s * HULL_X, 1, -37], 3.6, s > 0 ? BLUE : POLICE_RED);
      reactorSac(p, [0, 2, -27], 3, BLUE);
    },
    parts: { 'gun-left': hullGun, 'gun-right': hullGun, 'drone-bay': droneBay },
    turrets: { 'gun-left': hullGunTurret, 'gun-right': hullGunTurret },
  });
}

/** A hull gun (P07-R05, P16-R05): an armoured growth on the body's outer flank under its turret. */
function hullGun(p: EnemyParts, at: Vec3): void {
  const sponson = at[0] > 0 ? SPONSON : flipX(SPONSON);
  p.flesh.bevelSlab(sponson, [-2, 0.5, 3], [0.8, 1.6], F.crimson, { at }, F.sinew);
  growth(p, offset(at, 0, 1, 0), 9, at[0] > 0 ? BLUE : POLICE_RED, {
    flesh: F.purple,
    height: 0.35,
  });
}

/** A hull gun's twin-barrelled turret. */
function hullGunTurret(p: EnemyParts, at: Vec3): void {
  const r = SENTINEL.stats.parts[0]?.radius ?? 13;
  const outer = at[0] > 0;
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

/**
 * The drone bay (P07-R05, P16-R05): a swollen brood pouch at the nose, its slit lit, launch
 * glands at its corners, two drones hatching from it; a grafted rim plate behind.
 */
function droneBay(p: EnemyParts, at: Vec3): void {
  p.flesh.bevelSlab(BAY, [-3, 1, BAY_TOP - 1], [1, 3], F.crimson, { at }, F.purple);
  organ(p.flesh, 10, 7, F.purple, { at: offset(at, 0, 0, 1) }, 0.35);
  p.neon.box([0.5, 0.3, 16], BLUE, { at: offset(at, 0, BAY_TOP + 0.4, 1.5) });
  for (const [x, z] of scaled(HATCH, 1.12)) {
    p.charge.box([2, 0.8, 2], WHITE, { at: offset(at, x, BAY_TOP - 1.5, z) });
  }
  for (const s of SIDES) {
    p.vein.box([0.8, 0.5, 14], s > 0 ? BLUE : POLICE_RED, {
      at: offset(at, s * 13, BAY_TOP - 2.5, -2),
    });
    // A drone hatching on each side of the slit, ready to drop.
    const drone = offset(at, s * 4, BAY_TOP + 0.2, 2);
    organ(p.flesh, 1.6, 5, F.sinew, { at: drone }, 0.6);
    p.hull.box([4.4, 0.6, 1], M.panel, { at: drone, yaw: s * 0.8 });
    p.neon.box([1, 0.6, 1], s > 0 ? BLUE : POLICE_RED, { at: offset(drone, 0, 1.4, 0) });
  }
  graft(
    p,
    [
      [-12, -9],
      [12, -9],
      [10, -13],
      [-10, -13],
    ],
    [BAY_TOP - 2.5, BAY_TOP - 1.5],
    at,
  );
}
