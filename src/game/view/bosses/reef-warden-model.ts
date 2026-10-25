import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../render/game-view';
import { BOSS_LOOK } from '../../config/boss-look';
import { REEF_WARDEN } from '../../config/bosses/mini-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import {
  canopyPaint,
  decal,
  FIGHTER_SECTION,
  flipX,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { H, neonBand, offset, scaled, socket, turret } from './mini-boss-shapes';

// P07-R05, 1-1: the Reef Warden. Logical pixels, nose +Z, Y up (towards the camera).
type Vec3 = [number, number, number];

const CYAN = BOSS_LOOK.neon['reef-warden'] ?? [0.1, 0.9, 1];

/** The hover skirt seen from above: a wide hull, pointed at the prow, the cannons on its beam. */
const REEF_HULL = [
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
/** Heights of the skirt: its bottom, its rim (the widest), its deck. */
const SKIRT = [-5, -1, 3] as const;
/** The raised deck on the skirt: the hull's outline scaled down and moved back. */
const DECK = scaled(REEF_HULL, 0.66, 0, -3);
/** The bridge along the centre line (loft stations: z, half width, bottom, top). */
const BRIDGE = [
  [-24, 7, 5, 9],
  [-14, 10, 5, 13],
  [2, 10, 5, 14],
  [12, 7, 5, 11],
  [18, 3, 5, 7],
] as const;
/** The engine nacelles on the aft deck, either side of the bridge (loft stations). */
const NACELLE = [
  [-31, 4.5, 1.5, 8.5],
  [-22, 5.5, 1.5, 10],
  [-12, 4, 2.5, 7.5],
  [-6, 0, 5, 5],
] as const;
/** The radar mast on the bridge: a lathe profile. */
const MAST = [
  [1.6, 0],
  [1.2, 3],
  [3.4, 3.6],
  [3.4, 4.2],
  [0, 4.6],
] as const;
/** The right prow light, along the skirt's front edge, on its deck (mirrored for the left). */
const PROW_LIGHT = [
  [4, 32.5],
  [21, 18.5],
  [19.5, 17],
  [3, 30.5],
] as const;
/** The cannons' mounting plate (an octagon, in units of the part's radius). */
const MOUNT = Array.from({ length: 8 }, (_, k) => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)] as const;
});

/** The skirt with its cyan ring under the rim, the deck, the bridge and the engine nacelles. */
function drawBody({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(REEF_HULL, SKIRT, [3, 3], H.base, {}, H.panel);
  // The cyan ring under the rim, standing just out of the skirt's lower slope.
  neonBand(neon, REEF_HULL, [-3.4, -1.1], [0.985, 1.02], CYAN);
  hull.bevelSlab(DECK, [3, 3, 5], [0, 1.6], H.panel, {}, H.base);
  hull.loft(FIGHTER_SECTION, BRIDGE, H.base, {}, { paint: canopyPaint([2, 3], H.dark) });
  for (const side of [1, 6]) {
    const stripe = sideStripe(FIGHTER_SECTION, side, [0.3, 0.75]);
    neon.loft(stripe, BRIDGE.slice(0, 3), CYAN, {}, { open: true });
  }
  for (const light of [PROW_LIGHT, flipX(PROW_LIGHT)]) decal(neon, light, SKIRT[2] + 0.05, CYAN);
  hull.lathe(MAST, 6, H.panel, { at: [0, 13, -8] });
  for (const s of SIDES) {
    hull.loft(POD_SECTION, NACELLE, H.base, { at: [s * 13, 0, 0] });
    neon.box([0.6, 0.4, 10], CYAN, { at: [s * 13, 10, -23] });
  }
}

/**
 * P07-R05: the Reef Warden, a wide hover-gunboat with a cyan neon ring under its rim, a bridge
 * along its deck and a prow cannon; its two side cannons are mounted on its beam.
 */
export function buildReefWarden(scene: Scene): EnemyModel {
  return buildBossModel(REEF_WARDEN, scene, CYAN, {
    core: (p) => {
      drawBody(p);
      // The prow cannon (the core's fans).
      turret(p, [0, SKIRT[2], 27], {
        radius: 7,
        barrels: 1,
        gap: 0,
        bore: 1.5,
        length: 7,
        neon: CYAN,
      });
      for (const s of SIDES) {
        socket(p.hull, [s * 34, 3, 2], 8, 1.2);
        p.reactor([s * 13, 5, -31], 3.4);
      }
      p.reactor([0, -1, -30], 3);
    },
    parts: { 'cannon-left': cannon, 'cannon-right': cannon },
  });
}

/** A side cannon (P07-R05): a mounting plate on the beam and a twin-barrelled turret. */
function cannon(p: EnemyParts, at: Vec3): void {
  const r = REEF_WARDEN.stats.parts[0]?.radius ?? 14;
  p.hull.bevelSlab(scaled(MOUNT, r * 0.92), [1, 2.5, 4], [0.6, 1.4], H.base, { at }, H.panel);
  turret(p, offset(at, 0, 4, 0), {
    radius: r,
    barrels: 2,
    gap: 5,
    bore: 1.6,
    length: 9,
    neon: CYAN,
  });
}
