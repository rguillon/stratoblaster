import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { OVERLORD } from '../../config/bosses/final-bosses';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { segmentedBody } from '../../../render/geometry/organic';
import { decal, flipX, SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import { box2d, edgeLights, OVERLORD_DECK, OVERLORD_NEON, symmetric } from './overlord-city';
import { drawBattery, drawGenerator, drawLaser, WING_TOP } from './overlord-parts';
import { drawSkyline } from './overlord-skyline';
import {
  barbs,
  F,
  graft,
  M,
  mantle,
  polygon,
  ribCage,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Overlord, World 1's last boss (1-5). Model space: logical pixels, nose
// +Z (down the screen), Y up towards the camera. A city-sized organism: a vast mantle with a
// city of living towers grown on its back, a shelled spine down its middle carrying the citadel
// (its brain), membrane wings out to the laser cannons.
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

/**
 * The body (P16-R06): a vast purple mantle with a neon rim, a shelled spine down its middle (the
 * boulevard) carrying the citadel, ribs across it, veins out to its edges, membrane wings out to
 * the laser cannons on bone struts, swim bladders across its tail.
 */
function drawHull(p: EnemyParts): void {
  const { top, boulevard } = OVERLORD_DECK;
  mantle(p, DECK, [-8, top], F.purple);
  edgeLights(
    p.neon,
    DECK,
    DECK.map((_, i) => i),
    [-2.6, -1.4],
    N,
  );
  mantle(p, BOULEVARD, [top - 1, boulevard], F.crimson, N);
  ribCage(p, [-44, -20, 20, 44], { halfWidth: 30, y: top - 1, height: 7, thickness: 1.3 });
  segmentedBody(
    p.flesh,
    { tail: -68, nose: -50, segments: 3, width: 36, bottom: -7, top: 6 },
    F.sinew,
  );
  for (const s of SIDES) {
    const wing = s > 0 ? WING : flipX(WING);
    p.flesh.bevelSlab(wing, [-4, -1, WING_TOP], [1, 2], F.membrane, {}, F.purple);
    edgeLights(p.neon, wing, [0, 1, 2], [-1.5, -0.5], N);
    tentacle(p, [s * 56, 1, 20], [s * 102, 2, 2], [0, 2, 0], [2.6, 0.8], F.bone, 4);
    tentacle(p, [s * 56, 1, -30], [s * 100, 2, -16], [0, 2, 0], [2.4, 0.8], F.bone, 4);
    for (const z of [-40, -6, 30]) {
      veinLine(p, [s * 24, boulevard, z], [s * 60, top + 0.2, z + 6], [0, 2, 0], 1.3, N);
    }
    graft(p, polygon(5, 6, [1.4, 1]), [top - 0.4, top + 0.8], [s * 30, 0, 44], { color: M.base });
  }
  barbs(p, [0, top, 58], { count: 5, spacing: 8, size: 4, dir: [0, -0.2, 1] });
}

/**
 * The citadel over the core (P16-R06): a swollen, tiered brain-head ringed with neon, eyes on its
 * front, a ring emitter on top, the grafted weapon array before it.
 */
function drawCitadel(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  // Turned an eighth of a turn, a flat of the octagon faces the front.
  const tiers = { at: [0, OVERLORD_DECK.top, 0] as const, yaw: Math.PI / 8 };
  p.flesh.lathe(CITADEL, 8, F.crimson, tiers);
  eyes(p, [0, OVERLORD_DECK.top + 17, 17], { count: 3, size: 1.3, spacing: 4 }, N);
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
function drawHatches(p: EnemyParts): void {
  const { hull, charge, muzzle } = p;
  const y = OVERLORD_DECK.boulevard;
  graft(p, box2d(22, 18, [0, -34]), [y - 0.6, y], [0, 0, 0], { color: M.base });
  for (const x of [-6, 6]) {
    for (const z of [-30, -38]) {
      decal(hull, box2d(6.4, 5.4, [x, z]), y + 0.03, H.dark);
      decal(charge, box2d(4.6, 3.6, [x, z]), y + 0.06, WHITE);
      muzzle([x, y + 0.06, z], 'missile');
    }
  }
}

/** The core: body, city, citadel and hatches, four reactors in sacs across the tail. */
function drawCore(parts: EnemyParts): void {
  drawHull(parts);
  drawSkyline(parts);
  drawCitadel(parts);
  drawHatches(parts);
  for (const s of SIDES) {
    reactorSac(parts, [s * 12, -1, -68], 5.5, N);
    reactorSac(parts, [s * 28, -1, -68], 4.2, N);
  }
}

/**
 * P07-R05, P16-R06: the Overlord, a city-sized organism (6 L) under purple neon: living towers
 * lit with window glands grown out of its vast mantle, two wing laser cannons, two missile batteries at the back, two shield generators
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
