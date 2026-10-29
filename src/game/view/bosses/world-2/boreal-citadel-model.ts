import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  BOREAL_CITADEL,
  BOREAL_GUNS,
  BOREAL_HATCHES,
  BOREAL_LENS,
  BOREAL_SPIRE,
} from '../../../config/bosses/world-2/boreal-citadel';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { edgeLights, symmetric } from '../overlord-city';
import { ribs } from '../../../../render/geometry/organic';
import { reactorSac } from '../../enemies/organic-parts';
import { glowVein, ICE_FLESH, sinew } from './w2-organic';
import { AURORA, CITADEL_DECK, drawCity, icicles, rect, VIOLET } from './boreal-citadel-city';
import { drawDetails } from './boreal-citadel-details';
import {
  drawBattery,
  drawCannon,
  drawCannonMount,
  drawDome,
  OUTRIGGER_TOP,
} from './boreal-citadel-parts';

// P08-R10, 2-5: the Boreal Citadel, World 2's last boss. Model space: logical pixels, nose +Z
// (down the screen), Y up towards the camera. A polar city on a flying hull: a snowed deck
// with towers and heated domes, an avenue down its middle carrying the keep, outriggers out to
// the aurora cannons.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** The deck (right half, front to tail), the avenue on it, and the right outrigger. */
const DECK = symmetric(
  [
    [20, 84],
    [44, 66],
    [60, 36],
    [62, -20],
    [54, -56],
    [36, -78],
    [18, -84],
  ],
  86,
);
const AVENUE = rect(32, 94, [0, -17]);
const OUTRIGGER: OutlinePoint[] = [
  [56, 26],
  [94, 18],
  [100, 10],
  [100, -6],
  [94, -14],
  [56, -24],
];
/** The deck's bow edges (right half), icicles hanging under them. */
const BOW_EDGES = [
  [
    [20, 84],
    [44, 66],
  ],
  [
    [44, 66],
    [60, 36],
  ],
] as const;
/** The engine block across the tail. */
const ENGINES = rect(62, 12, [0, -86]);

/** The keep over the core: a stepped octagonal tower (lathe profile, bottom to top) and its spire. */
const KEEP = [
  [22, 0],
  [21.5, 12],
  [17, 14],
  [16.5, 21],
  [11, 23],
  [10.5, 28],
  [6, 30],
  [0, 30.5],
] as const;
/**
 * The keep's ledges (from the profile's outer to its inner edge), snowed over, and the radius of
 * the lit band round the wall under each.
 */
const LEDGES = [
  [[21.5, 12], [17, 14], AURORA, 21.8],
  [[16.5, 21], [11, 23], VIOLET, 16.9],
  [[10.5, 28], [6, 30], AURORA, 11],
] as const;
const SPIRE = [
  [3.5, 0],
  [2.4, 5],
  [1.2, 7],
] as const;
const SPIRE_TIP = [
  [1.4, 0],
  [0, 2],
] as const;
/** The gun deck on the keep's front, and the laser lens between its cannons. */
const GUN_DECK = rect(22, 16, [0, 34]);
const GUN_DECK_TOP = 21;
const LENS = [
  [0, 0],
  [3.2, 1],
  [2, 3],
  [0, 3.6],
] as const;

/** The deck with its snow and lit rim, the avenue, the engine block, the outriggers. */
function drawHull(p: EnemyParts): void {
  const { hull, flesh, neon } = p;
  const { top, avenue } = CITADEL_DECK;
  // P16-R06: the back of a colossal beast, rimed flesh, its spine (the avenue) a ridge of bone.
  flesh.bevelSlab(DECK, [-8, -2, top], [3, 3], ICE_FLESH.teal, {}, ICE_FLESH.rime);
  edgeLights(
    neon,
    DECK,
    DECK.map((_, i) => i),
    [-2.6, -1.4],
    AURORA,
  );
  flesh.bevelSlab(AVENUE, [top - 1, top, avenue], [0, 3], ICE_FLESH.bone, {}, ICE_FLESH.sinew);
  ribs(
    flesh,
    [-60, -48, -36],
    { halfWidth: 17, y: top, height: 8, thickness: 1.1 },
    ICE_FLESH.bone,
  );
  edgeLights(neon, AVENUE, [1, 3], [top + 0.4, top + 1.4], VIOLET);
  hull.bevelSlab(ENGINES, [-7, -1, 5], [1, 1.5], H.dark, {}, H.base);
  for (const s of SIDES) {
    const wing = s > 0 ? OUTRIGGER : flipX(OUTRIGGER);
    flesh.bevelSlab(
      wing,
      [-4, -1, OUTRIGGER_TOP],
      [1, 2],
      ICE_FLESH.membrane,
      {},
      ICE_FLESH.purple,
    );
    sinew(
      flesh,
      [s * 58, OUTRIGGER_TOP, 0],
      [s * 98, OUTRIGGER_TOP, 2],
      1.6,
      ICE_FLESH.bone,
      [0, 1, 6],
    );
    glowVein(p, [s * 18, top + 1, 40], [s * 56, top, 0], 1.4, AURORA);
    edgeLights(neon, wing, [0, 1, 2], [-1.5, -0.5], AURORA);
    icicles(flesh, [wing[0] ?? [0, 0], wing[1] ?? [0, 0]], -1, 5);
    for (const [[ax, az], [bx, bz]] of BOW_EDGES) {
      const edge: [OutlinePoint, OutlinePoint] = [
        [s * ax, az],
        [s * bx, bz],
      ];
      icicles(flesh, edge, -2, 4);
    }
  }
}

/** The keep over the core: tiers lit green and violet, its spire and ring emitter on top. */
function drawKeep({ hull, flesh, neon, charge, muzzle }: EnemyParts): void {
  const base = CITADEL_DECK.top;
  // P16-R06: the keep is the beast's heart, a stepped mound of flesh, metal bands on its ledges.
  flesh.lathe(KEEP, 8, ICE_FLESH.purple, { at: [0, base, 0], yaw: Math.PI / 8 });
  for (const [[r0, y0], [r1, y1], color, lit] of LEDGES) {
    hull.lathe(
      [
        [r0 + 0.2, y0 + 0.05],
        [r1 + 0.1, y1 + 0.1],
      ],
      8,
      H.panel,
      { at: [0, base, 0], yaw: Math.PI / 8 },
      false,
    );
    neon.ring(lit, 1.1, 8, color, { at: [0, base + y0 - 2.6, 0], yaw: Math.PI / 8 });
  }
  const spire = base + 30;
  flesh.lathe(SPIRE, 6, ICE_FLESH.crystal, { at: [0, spire, 0] });
  charge.lathe(SPIRE_TIP, 6, WHITE, { at: [0, spire + 7, 0] });
  muzzle(bossPoint(...BOREAL_SPIRE), 'ring');
}

/** The gun deck on the keep's front: twin cannons and a laser lens, charging before they fire. */
function drawGunDeck({ hull, neon, charge, muzzle }: EnemyParts): void {
  const base = CITADEL_DECK.top;
  hull.bevelSlab(GUN_DECK, [base, base, GUN_DECK_TOP], [0, 1.5], H.base, {}, H.panel);
  decal(neon, rect(16, 1.2, [0, 39]), GUN_DECK_TOP + 0.05, VIOLET);
  const front = 42;
  for (const m of BOREAL_GUNS) {
    const tip = bossPoint(...m);
    const along = (z: number): Placement => ({ at: [tip[0], tip[1], z], pitch: QUARTER });
    hull.cylinder(1.7, tip[2] - 2 - (front - 6), 6, H.dark, along(front - 6), 1.4);
    charge.cylinder(1.6, 2, 6, WHITE, along(tip[2] - 2), 1.1);
    muzzle(tip);
  }
  const lens = bossPoint(...BOREAL_LENS);
  const lensAt = lens[2] - LENS[3][1];
  const along = (z: number): Placement => ({ at: [0, lens[1], z], pitch: QUARTER });
  hull.cylinder(4, lensAt - (front - 4), 8, H.dark, along(front - 4));
  charge.lathe(LENS, 6, WHITE, along(lensAt));
  muzzle(lens, 'laser');
}

/** The missile hatches on the avenue behind the keep, lit as missiles load. */
function drawHatches({ hull, charge, muzzle }: EnemyParts): void {
  for (const m of BOREAL_HATCHES) {
    const [x, y, z] = bossPoint(...m);
    decal(hull, rect(6.4, 5.4, [x, z]), y - 0.06, H.dark);
    decal(charge, rect(4.6, 3.6, [x, z]), y, WHITE);
    muzzle([x, y, z], 'missile');
  }
}

/** The core: hull, city, keep, gun deck and hatches, four reactors in the engine block. */
function drawCore(parts: EnemyParts): void {
  drawHull(parts);
  drawCity(parts);
  drawKeep(parts);
  drawGunDeck(parts);
  drawHatches(parts);
  drawDetails(parts);
  for (const s of SIDES) {
    reactorSac(parts, [s * 12, -1, -92], 5.5, AURORA, { flesh: ICE_FLESH.purple, veinLength: 8 });
    reactorSac(parts, [s * 26, -1, -92], 4.2, AURORA, { flesh: ICE_FLESH.crimson, veinLength: 6 });
  }
}

/**
 * P08-R10: the Boreal Citadel, the polar city's flying fortress (6 L) under aurora green and
 * violet neon: towers and heated domes on a snowed deck, two aurora cannons on its outriggers,
 * two missile batteries aft, two dome generators ahead, and a keep over the core carrying a
 * laser, twin cannons, a ring emitter and missile hatches.
 * P16-R06: now a colossal living beast carrying its city on its back: rimed flesh, a spine of
 * bone, spires of crystal and flesh where the towers were, its heart (the keep) banded in metal,
 * membrane fins out to its cannons, glowing blisters for domes.
 */
export function buildBorealCitadel(scene: Scene): EnemyModel {
  return buildBossModel(BOREAL_CITADEL, scene, AURORA, {
    core: drawCore,
    parts: {
      'cannon-left': drawCannonMount,
      'cannon-right': drawCannonMount,
      'battery-left': drawBattery,
      'battery-right': drawBattery,
      'dome-left': drawDome,
      'dome-right': drawDome,
    },
    turrets: { 'cannon-left': drawCannon, 'cannon-right': drawCannon },
  });
}
