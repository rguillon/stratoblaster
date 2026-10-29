import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { REEF_WARDEN } from '../../config/bosses/mini-bosses';
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

// P07-R05, P16-R05, 1-1: the Reef Warden. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const CYAN = BOSS_LOOK.neon['reef-warden'] ?? [0.1, 0.9, 1];
/** Navigation lights: red to port (+X, the screen's left), green to starboard. */
const PORT_RED = [1, 0.1, 0.12] as const;
const STARBOARD_GREEN = [0.2, 1, 0.35] as const;

/** The mantle seen from above: a wide ray, pointed at the snout, the cannons on its flanks. */
const MANTLE = [
  [0, 38],
  [12, 34],
  [24, 23],
  [35, 11],
  [40, 1],
  [38, -10],
  [28, -22],
  [14, -30],
  [-14, -30],
  [-28, -22],
  [-38, -10],
  [-40, 1],
  [-35, 11],
  [-24, 23],
  [-12, 34],
] as const;
/** Heights of the mantle: its belly, its back. */
const SKIRT = [-5, 3] as const;

/**
 * The reef creature's body (P16-R05): a teal ray-like mantle lined with a cyan vein, a crimson
 * shelled back along its spine, bone ribs and coral barbs, gill glands either side.
 */
function drawBody(p: EnemyParts): void {
  mantle(p, MANTLE, SKIRT, F.teal, CYAN);
  neonBand(p.neon, MANTLE, [-3.4, -1.1], [0.97, 1], CYAN);
  mantle(p, scaleOutline(MANTLE, 0.7, 0, -3), [SKIRT[1] - 1, SKIRT[1] + 1.5], F.purple);
  hide(p, {
    tail: -31,
    nose: 24,
    width: 12,
    bottom: 3,
    top: 13,
    segments: 5,
    shell: [F.crimson, F.membrane],
    belly: F.sinew,
  });
  ribCage(p, [-20, -12, -4, 4], { halfWidth: 14, y: 4, height: 7, thickness: 0.9 });
  spine(p, [0, 13, -26], [0, 13.5, 18], { color: CYAN });
  for (const s of SIDES) {
    for (const z of [-8, 0, 8]) {
      veinLine(p, [s * 13, 4.5, z], [s * 28, 3.4, z - 6], [0, 1, 0], 0.9, CYAN);
    }
    gland(p, [s * 20, 3.5, 14], 2, CYAN);
    tentacle(p, [s * 8, 2, -28], [s * 14, 1, -36], [s * 3, 0, 0], [2, 0.3], F.teal);
  }
  barbs(p, [0, 13, -16], { count: 3, spacing: 0.1, size: 3, dir: [0, 1, -0.3] });
  eyes(p, [0, 9.5, 23], { count: 2, size: 1.3, spacing: 6 }, CYAN);
}

/** Grafts: a riveted nose plate, a back plate, flank plates, exhausts, navigation lights. */
function drawGrafts(p: EnemyParts): void {
  graft(p, polygon(5, 6, [1.2, 0.8]), [11, 12.3], [0, 0, 14]);
  graft(p, polygon(4, 5, [1.4, 0.8]), [12.6, 13.6], [0, 0, -10], { color: M.base });
  for (const s of SIDES) {
    graft(p, polygon(6, 4, [1, 1.4]), [SKIRT[1], SKIRT[1] + 0.8], [s * 26, 0, -14], {
      color: M.base,
    });
  }
  lamps(p.neon, [[27, SKIRT[1], -19]], 1.6, PORT_RED);
  lamps(p.neon, [[-27, SKIRT[1], -19]], 1.6, STARBOARD_GREEN);
  mast(p, [-4, 13.5, -16], 7, CYAN);
}

/**
 * P07-R05, P16-R05: the Reef Warden, a wide ray-like reef creature, a cyan vein ring round its
 * mantle and a prow cannon grafted on its snout; its two side cannons grow from its flanks.
 */
export function buildReefWarden(scene: Scene): EnemyModel {
  return buildBossModel(REEF_WARDEN, scene, CYAN, {
    core: (p) => {
      drawBody(p);
      drawGrafts(p);
      for (const s of SIDES) {
        socket(p.hull, [s * 34, 3, 2], 8, 1.2);
        reactorSac(p, [s * 13, 5, -31], 3.4, CYAN, { flesh: F.teal });
      }
      p.reactor([0, -1, -30], 3);
    },
    parts: { 'cannon-left': cannon, 'cannon-right': cannon },
    turrets: { core: prowTurret, 'cannon-left': cannonTurret, 'cannon-right': cannonTurret },
  });
}

/** The prow cannon (the core's gun), grafted on the snout, turning around its pivot `at`. */
function prowTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, SKIRT[1], 0), {
    radius: 7,
    barrels: 1,
    gap: 0,
    bore: 1.5,
    length: 7,
    neon: CYAN,
  });
}

/**
 * A side cannon (P07-R05, P16-R05): an armoured coral growth on the flank under its
 * twin-barrelled turret ({@link cannonTurret}), a feeding sac behind it, barbs before it.
 */
function cannon(p: EnemyParts, at: Vec3): void {
  const r = REEF_WARDEN.stats.parts[0]?.radius ?? 14;
  growth(p, offset(at, 0, -1, 0), r * 0.95, CYAN, { flesh: F.purple, height: 0.32 });
  sac(p, offset(at, Math.sign(at[0]) * 5, 1, -9), 4, F.crimson, { stretch: 0.5 });
  barbs(p, offset(at, 0, 2, 9), { count: 3, spacing: 4, size: 3, dir: [0, 0.3, 1] });
}

/** A side cannon's twin-barrelled turret. */
function cannonTurret(p: EnemyParts, at: Vec3): void {
  turret(p, offset(at, 0, 4, 0), {
    radius: REEF_WARDEN.stats.parts[0]?.radius ?? 14,
    barrels: 2,
    gap: 5,
    bore: 1.6,
    length: 9,
    neon: CYAN,
    hatch: -Math.sign(at[0]),
  });
}
