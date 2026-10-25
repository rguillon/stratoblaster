import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { GULL_MOTHERSHIP } from '../../config/bosses/final-bosses';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import {
  CANOPY_SECTION,
  HULL_SECTION,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { edgeStrips, mirrored, openHatch, shift, sided, turret } from './final-boss-shapes';
import {
  flakDetails,
  gullDeck,
  gullIsland,
  gullRunway,
  gullSpine,
  hangarDetails,
} from './final-boss-gull';

// P07-R05: the Gull Mothership, the final boss of 1-2. Logical pixels, nose +Z, Y up (towards
// the camera). A wide flying carrier: a flat deck, a raised hull along its middle ending in a
// big laser emitter, a hangar bay at each wing tip and two flak turrets on the front deck.
const H = ENEMY_LOOK.hull;
const N = BOSS_LOOK.neon['gull-mothership'] ?? [0.2, 1, 0.35];
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** The deck seen from above (right half, front to back); the hangars fit on its flat sides. */
const DECK = mirrored([
  [0, 50],
  [24, 46],
  [40, 32],
  [47, 20],
  [47, -30],
  [34, -48],
  [14, -56],
  [0, -56],
]);
const DECK_TOP = 4;
/** The raised hull along the deck (loft stations, tail to nose) and the bridge on its back. */
const HULL = [
  [-60, 10, 0, 7],
  [-46, 15, 0, 12],
  [-10, 17, 0, 15],
  [30, 14, 0, 13],
  [52, 10, 0, 9],
  [60, 7, 1, 7],
] as const;
const BRIDGE = [
  [-24, 4, 17, 20],
  [-14, 8, 17.5, 25],
  [0, 7, 17.5, 24],
  [6, 0, 17, 17],
] as const;
/** The big laser emitter's lens (a lathe profile along its axis), at the hull's nose. */
const LENS = [
  [0, 0],
  [5.5, 1.2],
  [4.6, 3.4],
  [0, 4.4],
] as const;
/** An engine housing on the back of the deck (loft stations, tail to front). */
const ENGINE = [
  [-50, 4.5, 0, 8],
  [-38, 5.5, 0, 9.5],
  [-24, 3, 0, 6],
] as const;
/** The right hangar around its centre, its outer side to +X, its inner side on the deck. */
const HANGAR = [
  [-17, 20],
  [17, 20],
  [21, 14],
  [21, -16],
  [17, -21],
  [-17, -21],
] as const;
const HANGAR_TOP = 10;

/** The deck, the raised hull with its bridge and neon flanks, and the launch lights. */
function drawHull(p: EnemyParts): void {
  p.hull.bevelSlab(DECK, [-5, -1, DECK_TOP], [2.5, 3], H.base, {}, H.panel);
  p.hull.loft(HULL_SECTION, HULL, H.base, { at: [0, DECK_TOP - 1, 0] });
  for (const side of [1, 3]) {
    const stripe = sideStripe(HULL_SECTION, side, [0.2, 0.5]);
    p.neon.loft(stripe, HULL.slice(1, 5), N, { at: [0, DECK_TOP - 1, 0] }, { open: true });
  }
  // The bridge's windows, painted dark across its sloped front.
  const paint = (side: number, band: number) =>
    band === 2 && (side === 1 || side === 2) ? H.dark : undefined;
  p.hull.loft(CANOPY_SECTION, BRIDGE, H.panel, {}, { open: true, paint });
  p.neon.box([1, 0.8, 16], N, { at: [0, 24.6, -9] });
  gullSpine(p, N);
  gullIsland(p, N);
  gullRunway(p, N);
  gullDeck(p, N);
}

/** The laser emitter at the nose: a barrel, neon rings, and the lens that glows as it charges. */
function drawEmitter(p: EnemyParts): void {
  const at: Vec3 = [0, DECK_TOP + 3, 58];
  p.hull.cylinder(7, 8, 8, H.dark, { at, pitch: QUARTER }, 6);
  for (const z of [1.5, 5]) {
    p.neon.ring(7.3 - z * 0.15, 1, 8, N, { at: shift(at, [0, 0, z]), pitch: QUARTER });
  }
  p.charge.lathe(LENS, 8, WHITE, { at: shift(at, [0, 0, 7.5]), pitch: QUARTER });
  // The core's laser and bullets leave from the lens's front.
  const lens = shift(at, [0, 0, 11.9]);
  p.muzzle(lens, 'laser');
  p.muzzle(lens);
}

/** The engine housings on the back of the deck and the reactors. */
function drawEngines(p: EnemyParts): void {
  for (const s of SIDES) {
    p.hull.loft(POD_SECTION, ENGINE, H.panel, { at: [s * 30, DECK_TOP - 1, 0] });
    p.reactor([s * 30, DECK_TOP + 3, -50], 3.4);
    p.reactor([s * 6, DECK_TOP + 2.5, -60], 2.8);
  }
}

/** A hangar bay: an armoured block on the deck's side, an open launch hatch, green lights. */
function drawHangar(p: EnemyParts, at: Vec3): void {
  const s = Math.sign(at[0]) || 1;
  p.hull.bevelSlab(sided(HANGAR, s), [-6, -1, HANGAR_TOP], [2, 3], H.base, { at }, H.panel);
  const hatch = shift(at, [s * 2, HANGAR_TOP, -2]);
  openHatch(p, hatch, [16, 28]);
  // Launch lights down both sides of the hatch, and a light bar across its front.
  for (const dx of [-11.5, 11.5]) {
    for (let k = 0; k < 4; k++) {
      p.neon.box([1.6, 0.8, 2.4], N, { at: shift(hatch, [dx, 0, -10.5 + k * 7]) });
    }
  }
  const [x, , z] = hatch;
  const front: OutlinePoint[] = [
    [x - 8, z + 16],
    [x + 8, z + 16],
  ];
  edgeStrips(p.neon, front, 1.4, [HANGAR_TOP - 0.2, HANGAR_TOP + 0.6], N);
  hangarDetails(p, at, N);
}

/** A flak turret on the front deck: an octagonal mount, the turret and its twin guns. */
function drawFlak(p: EnemyParts, at: Vec3): void {
  const mount = Array.from({ length: 8 }, (_, k): OutlinePoint => {
    const a = (2 * Math.PI * (k + 0.5)) / 8;
    return [Math.sin(a) * 12, Math.cos(a) * 12];
  });
  const heights = [DECK_TOP - 0.5, DECK_TOP, DECK_TOP + 2.5] as const;
  p.hull.bevelSlab(mount, heights, [0, 1.5], H.dark, { at }, H.base);
  turret(p, shift(at, [0, DECK_TOP + 2.5, 0]), 8.5, [2, N]);
  flakDetails(p, at, N);
}

/**
 * P07-R05: the Gull Mothership, a wide flying carrier 5 L across; green neon launch lights, a
 * hangar bay on each side (they launch the Gnats), two flak turrets on the front deck, and a
 * big laser emitter at the nose of its hull (the core).
 */
export function buildGullMothership(scene: Scene): EnemyModel {
  return buildBossModel(GULL_MOTHERSHIP, scene, N, {
    core: (p) => {
      drawHull(p);
      drawEmitter(p);
      drawEngines(p);
    },
    parts: {
      'hangar-left': drawHangar,
      'hangar-right': drawHangar,
      'flak-left': drawFlak,
      'flak-right': drawFlak,
    },
  });
}
