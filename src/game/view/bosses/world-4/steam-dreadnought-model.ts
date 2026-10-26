import type { Scene } from '@babylonjs/core/scene';
import type { EnemyModel } from '../../../../render/game-view';
import {
  DREAD_BEACON,
  DREAD_BOW_GUNS,
  DREAD_HEIGHTS,
  DREAD_LENS,
  STEAM_DREADNOUGHT,
} from '../../../config/bosses/world-4/steam-dreadnought';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { HULL_SECTION, sideStripe, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { mast } from '../final-boss-greebles';
import { seam, vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, WHITE } from '../mini-boss-shapes';
import { edgeLights, symmetric } from '../overlord-city';
import { barrelTo, blot, bolts, FORGE, moltenSeam, soot } from './black-sands-kit';
import {
  barbette,
  broadside,
  DREAD_RED as N,
  missileRack,
  smokestack,
} from './steam-dreadnought-parts';

// P10-R11, 4-1: the Steam Dreadnought. Logical pixels, nose +Z (down the screen), Y up towards
// the camera; +X is the screen's left. A flying battleship: a long armoured hull under a deck
// with sponsons for its broadside turrets, a stepped bridge over the core, two smokestacks
// amidships, a laser ram at the bow and a missile rack on the stern.

const DECK = DREAD_HEIGHTS.deck;
/** The hull under the deck (loft stations, stern to bow: z, half width, bottom, top). */
const HULL = [
  [-80, 16, 2, 7],
  [-72, 24, -3, 8],
  [-40, 28, -6, 8.5],
  [10, 28, -6, 8.5],
  [46, 22, -5, 8],
  [70, 13, -2, 7.5],
  [84, 5, 0, 7],
] as const;
/** The deck (right half, bow to stern), wide at the sponsons, closed across the bow. */
const DECK_OUTLINE = symmetric(
  [
    [10, 78],
    [22, 56],
    [36, 40],
    [66, 32],
    [70, 20],
    [66, 8],
    [40, 2],
    [39, -30],
    [32, -60],
    [20, -76],
  ],
  84,
);
/** The bridge's tiers (width, height, depth, z of their middle), bottom to top. */
const BRIDGE = [
  [34, 8, 34, 4],
  [24, 8, 24, 6],
  [14, 8, 14, 7],
] as const;
/** The raised citadel amidships, under the bridge and between the stacks (w, h, d, z). */
const CITADEL = [36, 3, 74, -9] as const;
/** The laser lens at the stem (a lathe profile along its axis). */
const LENS = [
  [0, 0],
  [3, 0.8],
  [2, 2.4],
  [0, 3],
] as const;

/** The hull, its glowing seams low on the sides, the deck with its red-lit rim, the reactors. */
function drawHull(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.loft(HULL_SECTION, HULL, H.dark);
  for (const side of [0, 4]) {
    neon.loft(
      sideStripe(HULL_SECTION, side, [0.35, 0.6], 1.03),
      HULL.slice(1, 6),
      FORGE.molten,
      {},
      { open: true },
    );
  }
  hull.bevelSlab(DECK_OUTLINE, [4.5, 7, DECK], [1, 0.8], H.base, {}, H.panel);
  edgeLights(
    neon,
    DECK_OUTLINE,
    DECK_OUTLINE.map((_, i) => i),
    [5.8, 6.8],
    N,
  );
  p.reactor([0, 3, -82], 5);
  for (const s of SIDES) p.reactor([s * 14, 3, -78], 4);
}

/** The deck's dressing: molten seams between its plates, soot behind the stacks, cowls, bolts. */
function drawDeck({ hull, neon }: EnemyParts): void {
  const [w, h, d, middle] = CITADEL;
  hull.box([w, h, d], H.base, { at: [0, DECK, middle] }, H.panel);
  for (const [y, half, at] of [
    [DECK, 24, 34],
    [DECK + h, w / 2 - 2, -30],
  ] as const) {
    moltenSeam(
      neon,
      [
        [-half, at],
        [-half * 0.4, at + 1.5],
        [half * 0.15, at - 1],
        [half, at + 0.8],
      ],
      y + 0.05,
    );
  }
  for (const x of [-44, 44]) seam(hull, [x, 36], [x, 4], [DECK, 0.6, 0.15]);
  for (const s of SIDES) {
    soot(hull, blot([s * 30, -32], 7, 1.6, s), DECK);
    soot(hull, blot([s * 50, 20], 5, 0.8, 2 * s), DECK);
    for (const z of [-4, -44]) {
      hull.cylinder(1.6, 3, 5, H.panel, { at: [s * 22, DECK, z] });
      hull.box([3, 2.2, 2.4], H.dark, { at: [s * 22, DECK + 3, z + 0.6] });
    }
    bolts(
      hull,
      [-60, -50, 40, 50].map((z) => [s * 14, z] as const),
      DECK,
      1.1,
    );
  }
  soot(hull, blot([0, -70], 8, 0.6, 7), DECK);
  vent(hull, [0, DECK + 0.05, 30], [10, 6], 4);
}

/** The bridge over the core: stepped tiers, red-lit windows, wings, a mast and its beacon. */
function drawBridge(p: EnemyParts): void {
  const { hull, neon, charge } = p;
  let y = DECK;
  for (const [w, h, d, z] of BRIDGE) {
    hull.box([w, h, d], H.base, { at: [0, y, z] }, H.panel);
    neon.box([w * 0.7, 0.9, 0.4], N, { at: [0, y + h * 0.55, z + d / 2 + 0.05] });
    y += h;
  }
  hull.box([44, 1.2, 4], H.panel, { at: [0, DECK + 13, 16] });
  for (const s of SIDES) neon.box([1.2, 1, 1.2], N, { at: [s * 21.5, DECK + 14.2, 16] });
  mast(p, [-4, y, 3], 6, N);
  const [emitter] = DREAD_BEACON;
  if (!emitter) return;
  const top = bossPoint(...emitter);
  hull.cylinder(3.6, top[1] - y - 0.6, 6, H.panel, { at: [top[0], y, top[2]] }, 2.4);
  neon.ring(3.7, 0.7, 6, N, { at: [top[0], y + 0.6, top[2]] });
  charge.cylinder(2.4, 0.6, 6, WHITE, { at: offset(top, 0, -0.6, 0) }, 1);
  p.muzzle(top, 'ring');
}

/** The bow: the gun block with its twin guns, and the laser ram at the stem, lit as it charges. */
function drawBow(p: EnemyParts): void {
  const { hull, charge, muzzle } = p;
  hull.box([24, 3.5, 10], H.base, { at: [0, DECK, 62] }, H.panel);
  for (const tip of DREAD_BOW_GUNS) barrelTo(p, tip, [1.4, 8]);
  const [lens] = DREAD_LENS;
  if (!lens) return;
  const tip = bossPoint(...lens);
  const back = tip[2] - (LENS.at(-1)?.[1] ?? 0);
  hull.cylinder(3.8, 12, 8, H.panel, { at: [0, tip[1], back - 12], pitch: QUARTER }, 3.2);
  hull.ring(4.2, 1.4, 8, FORGE.soot, { at: [0, tip[1], back - 2], pitch: QUARTER });
  charge.lathe(LENS, 6, WHITE, { at: [0, tip[1], back], pitch: QUARTER });
  muzzle(tip, 'laser');
}

/**
 * P10-R11: the Steam Dreadnought, a flying battleship 5 L long, red neon: a soot-black armoured
 * hull with glowing seams, a stepped bridge over its core, two smokestacks puffing steam, two
 * broadside turrets on sponsons, a laser ram at the bow and a missile rack on the stern.
 */
export function buildSteamDreadnought(scene: Scene): EnemyModel {
  return buildBossModel(STEAM_DREADNOUGHT, scene, N, {
    core: (p) => {
      drawHull(p);
      drawDeck(p);
      drawBridge(p);
      drawBow(p);
    },
    parts: {
      'stack-left': smokestack,
      'stack-right': smokestack,
      'turret-left': barbette,
      'turret-right': barbette,
      rack: missileRack,
    },
    turrets: { 'turret-left': broadside, 'turret-right': broadside },
  });
}
