import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { OVERLORD } from '../../config/bosses/final-bosses';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import { box2d, edgeLights, OVERLORD_DECK, OVERLORD_NEON, symmetric } from './overlord-city';
import { drawOverlordArmour } from './overlord-armour';
import { drawDeck } from './overlord-deck';
import { drawBattery, drawGenerator, drawLaser, WING_TOP } from './overlord-parts';
import { drawSkyline } from './overlord-skyline';

// P07-R05: the Overlord, World 1's last boss (1-5). Model space: logical pixels, nose +Z (down
// the screen), Y up towards the camera. A flying city block: a wide armoured deck with towers,
// a raised boulevard down its middle carrying the citadel, wings out to the laser cannons.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;
const N = OVERLORD_NEON;

/** The deck (right half, front to tail), the boulevard on it, and the right wing. */
const DECK = symmetric(
  [
    [26, 60],
    [52, 42],
    [64, 18],
    [64, -30],
    [52, -50],
    [36, -60],
  ],
  64,
);
const BOULEVARD = symmetric(
  [
    [14, 54],
    [18, 26],
    [26, -10],
    [26, -46],
    [16, -54],
  ],
  56,
);
const WING: OutlinePoint[] = [
  [60, 24],
  [98, 10],
  [104, 2],
  [104, -14],
  [96, -20],
  [60, -34],
];
/** The engine block across the tail. */
const ENGINES = box2d(72, 12, [0, -62]);
/** The citadel over the core: a stepped octagonal tower (lathe profile, bottom to top). */
const CITADEL = [
  [24, 0],
  [23, 7],
  [18, 10],
  [17.5, 16],
  [12, 19],
  [11, 24],
  [0, 25],
] as const;
/** The weapon array on the citadel's front. */
const GUN_DECK: OutlinePoint[] = [
  [-12, 14],
  [12, 14],
  [10, 34],
  [-10, 34],
];
const LENS = [
  [0, -1.5],
  [3.2, 0],
  [0, 2.5],
] as const;

/** The deck, its neon rim, the boulevard, the engine block and the wings with lit edges. */
function drawHull({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(DECK, [-8, -2, OVERLORD_DECK.top], [3, 3], H.base, {}, H.panel);
  edgeLights(
    neon,
    DECK,
    DECK.map((_, i) => i),
    [-2.6, -1.4],
    N,
  );
  const { top, boulevard } = OVERLORD_DECK;
  hull.bevelSlab(BOULEVARD, [top - 1, top, boulevard], [0, 1.5], H.panel, {}, H.base);
  edgeLights(
    neon,
    BOULEVARD,
    BOULEVARD.map((_, i) => i),
    [top + 0.2, top + 1],
    N,
  );
  hull.bevelSlab(ENGINES, [-7, -1, 5], [1, 1.5], H.dark, {}, H.base);
  for (const s of SIDES) {
    const wing = s > 0 ? WING : flipX(WING);
    hull.bevelSlab(wing, [-4, -1, WING_TOP], [1, 2], H.base, {}, H.panel);
    // The leading edge and the tip, lit.
    edgeLights(neon, wing, [0, 1, 2], [-1.5, -0.5], N);
    decal(neon, box2d(1.6, 12, [s * 100.5, -6]), WING_TOP + 0.05, N);
  }
}

/** The citadel over the core: neon tiers, a ring emitter on top, the front weapon array. */
function drawCitadel({ hull, neon, charge, muzzle }: EnemyParts): void {
  // Turned an eighth of a turn, a flat of the octagon faces the front.
  const tiers = { at: [0, OVERLORD_DECK.top, 0] as const, yaw: Math.PI / 8 };
  hull.lathe(CITADEL, 8, H.panel, tiers);
  const lit = (r: number, y: number, h: number): void => {
    neon.ring(r, h, 8, N, { at: [0, OVERLORD_DECK.top + y, 0], yaw: Math.PI / 8 });
  };
  lit(18.1, 12, 1.2);
  lit(11.9, 21.5, 1);
  // The ring emitter on top of the citadel.
  charge.lathe(
    [
      [5, 0],
      [3.5, 1.8],
      [0, 2.6],
    ],
    8,
    WHITE,
    { at: [0, OVERLORD_DECK.top + 25, 0] },
  );
  muzzle([0, OVERLORD_DECK.top + 27.6, 0], 'ring');
  const deck = OVERLORD_DECK.boulevard;
  hull.bevelSlab(GUN_DECK, [deck, deck, deck + 9], [0, 1.5], H.base, {}, H.panel);
  decal(neon, box2d(14, 1.2, [0, 24]), deck + 9.05, N);
  // A laser lens between twin cannons, all charging before they fire.
  const axis = deck + 4.5;
  hull.cylinder(4.2, 3, 8, H.dark, { at: [0, axis, 31], pitch: QUARTER });
  charge.lathe(LENS, 6, WHITE, { at: [0, axis, 35.5], pitch: QUARTER });
  muzzle([0, axis, 38], 'laser');
  for (const s of SIDES) {
    hull.cylinder(1.6, 10, 6, H.dark, { at: [s * 7, axis + 1, 28], pitch: QUARTER });
    charge.cylinder(2, 1.6, 6, WHITE, { at: [s * 7, axis + 1, 38], pitch: QUARTER });
    muzzle([s * 7, axis + 1, 39.6]);
  }
}

/** The missile hatches on the boulevard behind the citadel, lit as missiles load. */
function drawHatches({ hull, charge, muzzle }: EnemyParts): void {
  const y = OVERLORD_DECK.boulevard;
  for (const x of [-6, 6]) {
    for (const z of [-30, -38]) {
      decal(hull, box2d(6.4, 5.4, [x, z]), y + 0.03, H.dark);
      decal(charge, box2d(4.6, 3.6, [x, z]), y + 0.06, WHITE);
      muzzle([x, y + 0.06, z], 'missile');
    }
  }
}

/** The core: hull, city, citadel and hatches, four reactors in the engine block. */
function drawCore(parts: EnemyParts): void {
  drawHull(parts);
  drawDeck(parts);
  drawSkyline(parts);
  drawOverlordArmour(parts);
  drawCitadel(parts);
  drawHatches(parts);
  for (const s of SIDES) {
    parts.reactor([s * 12, -1, -68], 5.5);
    parts.reactor([s * 28, -1, -68], 4.2);
  }
}

/**
 * P07-R05: the Overlord, a city-ship (6 L) under purple neon: towers with lit windows over a
 * wide deck, two wing laser cannons, two missile batteries at the back, two shield generators
 * in front, and a citadel over the core carrying a laser, twin cannons, a ring emitter and
 * missile hatches.
 */
export function buildOverlord(scene: Scene): EnemyModel {
  return buildBossModel(OVERLORD, scene, N, {
    core: drawCore,
    parts: {
      'laser-left': drawLaser,
      'laser-right': drawLaser,
      'battery-left': drawBattery,
      'battery-right': drawBattery,
      'generator-left': drawGenerator,
      'generator-right': drawGenerator,
    },
  });
}
