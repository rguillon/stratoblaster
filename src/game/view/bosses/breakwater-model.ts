import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { BREAKWATER } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { lamps, mast } from './mini-boss-greebles';
import { neonBand, offset, socket, turret } from './mini-boss-shapes';
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
  sac,
  scaleOutline,
  spine,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R05, 1-2: the Breakwater. Logical pixels, nose +Z, Y up (towards the camera).
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
/** Heights of the shell's rim: its belly, its widest line, its top. */
const HULL_Y = [-5, -1, 4] as const;
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

/**
 * The crab's body (P16-R05): a wide mantle under a domed, plated shell, ribs over its back,
 * an orange vein along its spine, eyes on stalks at its front over its mouth (the bow gun).
 */
function drawBody(p: EnemyParts): void {
  const deck = HULL_Y[2];
  mantle(p, BARGE_HULL, [HULL_Y[0], deck], F.sinew, ORANGE);
  neonBand(p.neon, BARGE_HULL, [-1.4, -0.4], [1.02, 1.02], ORANGE);
  hide(p, {
    tail: -41,
    nose: 13,
    width: 27,
    bottom: deck - 1,
    top: 16,
    segments: 4,
    shell: [F.crimson, F.membrane],
    belly: F.purple,
  });
  ribCage(p, [-30, -20, -10, 0], { halfWidth: 22, y: deck, height: 10, thickness: 1.1 });
  spine(p, [0, 16, -34], [0, 16.5, 6], { color: ORANGE, width: 1.4 });
  for (const s of SIDES) {
    tentacle(p, [s * 4, deck + 3, 12], [s * 6, deck + 9, 19], [0, 1, 0], [0.9, 0.5], F.sinew, 3);
    eyes(p, [s * 6, deck + 9, 19], { count: 1, size: 1.3 }, ORANGE);
    gland(p, [s * 16, deck + 8, -28], 2, ORANGE);
    for (const z of [-24, -10]) {
      veinLine(p, [s * 10, 14, z], [s * 26, deck + 1, z - 4], [s * 2, 3, 0], 1, ORANGE);
    }
  }
}

/** The crab's walking legs, three each side, folded under its rim (bone, jointed). */
function drawLegs(p: EnemyParts): void {
  for (const s of SIDES) {
    for (const z of [-8, -20, -32]) {
      const knee: Vec3 = [s * 36, HULL_Y[2] + 4, z - 2];
      tentacle(p, [s * 24, HULL_Y[2], z], knee, [0, 2, 0], [2.4, 1.6], F.sinew, 4);
      tentacle(p, knee, [s * 40, HULL_Y[0], z - 6], [s, 0, 0], [1.6, 0.2], F.bone, 4);
    }
  }
}

/** Grafts: a riveted back plate, armour bands on the shell's flanks, exhausts, running lights. */
function drawGrafts(p: EnemyParts): void {
  graft(p, polygon(6, 8, [1.2, 1]), [15, 16.6], [0, 0, -14]);
  graft(p, polygon(4, 6, [1.3, 0.7]), [13.6, 15], [0, 0, 2], { color: M.base });
  for (const s of SIDES) {
    graft(p, polygon(5, 5, [0.8, 1.6]), [9, 10.4], [s * 18, 0, -16], { color: M.base });
    lamps(
      p.neon,
      [16, 2, -29].map((z): Vec3 => [s * 27, HULL_Y[2] + 0.4, z]),
      1.2,
      ORANGE,
    );
  }
  mast(p, [11, 15, -22], 8, ORANGE);
}

/**
 * P07-R05, P16-R05: the Breakwater, a huge armoured shore crab with orange veins: a wide plated
 * shell over jointed legs, a bony V-shaped ram plate over its snout, a gun in its mouth and two
 * barnacle mortars on its flanks.
 */
export function buildBreakwater(scene: Scene): EnemyModel {
  return buildBossModel(BREAKWATER, scene, ORANGE, {
    core: (p) => {
      drawBody(p);
      drawLegs(p);
      drawGrafts(p);
      for (const s of SIDES) {
        socket(p.hull, [s * 34, HULL_Y[2], -12], 8, 1);
        // The ram plate's grafted brackets on the snout.
        p.hull.box([4, 3, 8], M.dark, { at: [s * 13, HULL_Y[2] - 1, 24] });
        reactorSac(p, [s * 16, -0.5, -40], 3.4, ORANGE);
      }
      p.reactor([0, -0.5, -40], 3.8);
    },
    parts: { 'ram-plate': ramPlate, 'mortar-left': mortar, 'mortar-right': mortar },
    turrets: { core: bowGun, 'mortar-left': mortarTurret, 'mortar-right': mortarTurret },
  });
}

/** The bow gun in the hold (the core's fans, bursts and rings), turning on the hold's floor. */
function bowGun(p: EnemyParts, at: Vec3): void {
  const gun = { radius: 7, barrels: 2, gap: 3, bore: 1.2, length: 6, neon: ORANGE };
  turret(p, offset(at, 0, HULL_Y[2] + 0.4, 0), gun);
}

/**
 * The ram plate (P07-R05, P16-R05): no weapon, the crab's thick bony brow shield, a V of
 * grafted armour on it, orange veins along its edge.
 */
function ramPlate(p: EnemyParts, at: Vec3): void {
  const top = 9;
  p.flesh.bevelSlab(PLATE, [-3, 1, top - 1.5], [1.5, 4], F.bone, { at }, F.sinew);
  neonBand(p.neon, PLATE, [0.6, 1.8], [1.02, 1.02], ORANGE, { at });
  for (const side of SIDES) {
    const edge: Vec3 = offset(at, side * 16, top - 1.6, 3.5);
    veinLine(p, offset(at, side, top - 1.2, 12.5), edge, [0, 0.8, 0], 1, ORANGE);
  }
  graft(p, scaleOutline(PLATE, 0.55, 0, 2), [top - 1.6, top], at);
  barbs(p, offset(at, 0, 2, 15), { count: 3, spacing: 7, size: 4, dir: [0, 0.2, 1] });
}

/**
 * A mortar (P07-R05, P16-R05): a swollen barnacle growth on the flank under its turret
 * ({@link mortarTurret}), a spawn sac beside it.
 */
function mortar(p: EnemyParts, at: Vec3): void {
  const r = BREAKWATER.stats.parts[1]?.radius ?? 13;
  growth(p, offset(at, 0, HULL_Y[2] - 2, 0), r, ORANGE, { flesh: F.purple, height: 0.4 });
  sac(p, offset(at, Math.sign(at[0]) * 8, HULL_Y[2], 6), 3.5, F.crimson, { stretch: 0.7 });
}

/** A mortar's turret: a squat dome and a short, fat, raised barrel. */
function mortarTurret(p: EnemyParts, at: Vec3): void {
  const r = BREAKWATER.stats.parts[1]?.radius ?? 13;
  const gun = { radius: r, barrels: 1, gap: 0, bore: 3.6, length: 3, elevation: 0.6, neon: ORANGE };
  turret(p, offset(at, 0, HULL_Y[2] + 3, 0), { ...gun, hatch: Math.sign(at[0]) });
}
