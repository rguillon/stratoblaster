import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { BREAKWATER } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { H, neonBand, offset, scaled, socket, turret } from './mini-boss-shapes';

// P07-R05, 1-2: the Breakwater. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const ORANGE = BOSS_LOOK.neon.breakwater ?? [1, 0.5, 0.05];

/** The barge's hull seen from above: a long, square-cut hull, bulging where the mortars sit. */
const BARGE_HULL = [
  [-24, 27],
  [24, 27],
  [31, 20],
  [31, 6],
  [39, 0],
  [39, -24],
  [31, -30],
  [31, -34],
  [24, -40],
  [-24, -40],
  [-31, -34],
  [-31, -30],
  [-39, -24],
  [-39, 0],
  [-31, 6],
  [-31, 20],
] as const;
/** Heights of the hull: its keel, its widest line, its deck. */
const HULL_Y = [-5, -1, 4] as const;
/** The right gunwale, a raised armoured wall along the deck's edge (mirrored for the left). */
const GUNWALE = [
  [21, 22],
  [27, 17],
  [27, -32],
  [21, -36],
  [21, -16],
  [23, -12],
  [23, 8],
  [21, 12],
] as const;
/** The hold between the gunwales: a dark floor, and the bow ramp sloping down at its front. */
const HOLD = [
  [-20, 18],
  [20, 18],
  [20, -18],
  [-20, -18],
] as const;
const RAMP = [
  [-16, 27],
  [16, 27],
  [18, 19],
  [-18, 19],
] as const;
/** The bridge tower at the stern, and its visor (along the tower's front, just under its top). */
const TOWER = [
  [-12, -18],
  [12, -18],
  [15, -24],
  [15, -34],
  [-15, -34],
  [-15, -24],
] as const;
const VISOR = [
  [-10, -18.4],
  [10, -18.4],
  [12.4, -23.2],
  [11.2, -23.2],
  [9.2, -19.6],
  [-9.2, -19.6],
  [-11.2, -23.2],
  [-12.4, -23.2],
] as const;
/** The ram plate around its centre: a V of chamfered armour over the bow. */
const PLATE = [
  [0, 17],
  [20, 5],
  [21, -5],
  [15, -10],
  [-15, -10],
  [-21, -5],
  [-20, 5],
] as const;
/** The plate's right warning light, along its upper front edge (mirrored for the left). */
const PLATE_LIGHT = [
  [1, 12.5],
  [15.5, 3.6],
  [15, 2.2],
  [1, 10.8],
] as const;
/** A mortar's mounting plate on its sponson (an octagon, in units of the part's radius). */
const MOUNT = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)] as const;
});

/** The hull, the gunwales, the hold with its ramp and the bridge tower. */
function drawBody({ hull, neon }: EnemyParts): void {
  const deck = HULL_Y[2];
  hull.bevelSlab(BARGE_HULL, HULL_Y, [3, 2.5], H.base, {}, H.panel);
  neonBand(neon, BARGE_HULL, [-1.4, -0.4], [1.02, 1.02], ORANGE);
  for (const wall of [GUNWALE, flipX(GUNWALE)]) {
    hull.bevelSlab(wall, [deck, deck, 9], [0, 1.4], H.base, {}, H.panel);
  }
  hull.slab(HOLD, [deck, deck + 0.4], H.dark);
  // Cargo hatches in the hold, outlined in orange.
  for (const z of [-11, 0, 11]) {
    hull.box([26, 0.6, 7], H.panel, { at: [0, deck + 0.4, z] });
    neon.box([27, 0.4, 0.6], ORANGE, { at: [0, deck + 0.5, z - 3.8] });
  }
  hull.bevelSlab(RAMP, [-1, deck - 1, deck], [0, 0.8], H.panel, {}, H.dark);
  hull.bevelSlab(TOWER, [deck, deck, 14], [0, 2], H.base, {}, H.panel);
  neon.slab(VISOR, [11.2, 12.4], ORANGE);
  hull.box([3, 4, 3], H.panel, { at: [6, 14, -29] });
}

/**
 * P07-R05: the Breakwater, an armoured flying landing barge with orange neon: a long hull with
 * raised gunwales, a hold and a bow ramp, a bridge tower at the stern, a V-shaped ram plate over
 * its bow and two mortar turrets on its side sponsons.
 */
export function buildBreakwater(scene: Scene): EnemyModel {
  return buildBossModel(BREAKWATER, scene, ORANGE, {
    core: (p) => {
      drawBody(p);
      // The bow gun in the hold (the core's fans, bursts and rings).
      const gun = { radius: 7, barrels: 2, gap: 3, bore: 1.2, length: 6, neon: ORANGE };
      turret(p, [0, HULL_Y[2] + 0.4, 21], gun);
      for (const s of SIDES) {
        socket(p.hull, [s * 34, HULL_Y[2], -12], 8, 1);
        // The ram plate's brackets on the bow.
        p.hull.box([4, 3, 8], H.dark, { at: [s * 13, HULL_Y[2] - 1, 24] });
        p.reactor([s * 16, -0.5, -40], 3.4);
      }
      p.reactor([0, -0.5, -40], 3.8);
    },
    parts: { 'ram-plate': ramPlate, 'mortar-left': mortar, 'mortar-right': mortar },
  });
}

/** The ram plate (P07-R05): no weapon, a thick V of armour with orange warning lights. */
function ramPlate({ hull, neon }: EnemyParts, at: Vec3): void {
  const top = 9;
  hull.bevelSlab(PLATE, [-3, 1, top], [1.5, 4], H.panel, { at }, H.base);
  for (const light of [PLATE_LIGHT, flipX(PLATE_LIGHT)]) {
    const place = scaled(light, 1, at[0], at[2]);
    decal(neon, place, top + 0.05, ORANGE);
  }
  neonBand(neon, PLATE, [0.6, 1.8], [1.02, 1.02], ORANGE, { at });
}

/** A mortar turret (P07-R05): a mounting plate, a squat dome and a short, fat, raised barrel. */
function mortar(p: EnemyParts, at: Vec3): void {
  const r = BREAKWATER.stats.parts[1]?.radius ?? 13;
  const base = HULL_Y[2];
  p.hull.bevelSlab(
    scaled(MOUNT, r),
    [base - 1, base + 1, base + 3],
    [0.5, 1.5],
    H.base,
    { at },
    H.panel,
  );
  const gun = { radius: r, barrels: 1, gap: 0, bore: 3.6, length: 3, elevation: 0.6, neon: ORANGE };
  turret(p, offset(at, 0, base + 3, 0), gun);
}
