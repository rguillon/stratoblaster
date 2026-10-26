import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import type { EnemyModel } from '../../../../render/game-view';
import {
  CALDERA_GUNS,
  CALDERA_HATCHES,
  CALDERA_LENS,
  CALDERA_THRONE,
} from '../../../config/bosses/world-4/caldera-throne';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { grille, hazard, plate, rect } from '../final-boss-greebles';
import { glowLine } from '../final-boss-mechanism';
import { H, QUARTER, WHITE } from '../mini-boss-shapes';
import { edgeLights, symmetric } from '../overlord-city';
import { drawKeep } from './caldera-throne-keep';
import {
  BASTION_TOP,
  CRIMSON,
  DECK_TOP,
  GOLD,
  HEAT,
  magmaCannon,
  magmaMount,
  missileBattery,
  shieldGenerator,
} from './caldera-throne-parts';

// P10-R11, 4-5: the Caldera Throne, World 4's last boss. Model space: logical pixels, nose +Z
// (down the screen), Y up towards the camera; +X is the screen's left. A war fortress: an
// armoured hull carrying a stepped keep over the core, a prow gun deck, side bastions out to the
// magma cannons, missile batteries and smokestacks aft.

/** The hull (right half, front to tail), closed across the prow. */
const HULL = symmetric(
  [
    [14, 94],
    [30, 80],
    [46, 58],
    [58, 34],
    [64, 8],
    [66, -20],
    [62, -52],
    [52, -78],
    [36, -96],
    [16, -102],
  ],
  100,
);
/** The right bastion (mirrored on the left), out to the magma cannon's turntable. */
const BASTION: OutlinePoint[] = [
  [58, 36],
  [90, 28],
  [104, 18],
  [104, -2],
  [90, -12],
  [60, -22],
];
/** The engine block across the stern. */
const ENGINES = rect([0, -96], [72, 12]);
/** The prow's gun deck, and its top. */
const PROW = rect([0, 78], [30, 30]);
const PROW_TOP = 14;
/** The block the core's missile hatches open in, behind the keep. */
const HATCH_BLOCK = rect([0, -63], [28, 22]);
const LENS = [
  [0, 0],
  [3.8, 1],
  [2.6, 3],
  [0, 4],
] as const;
/** The molten seams across the deck (right half, `[x, z]` from and to). */
const SEAMS = [
  [
    [40, 30],
    [56, 6],
  ],
  [
    [42, -24],
    [58, -46],
  ],
  [
    [14, 52],
    [22, 40],
  ],
  [
    [30, -84],
    [46, -70],
  ],
] as const satisfies readonly (readonly [OutlinePoint, OutlinePoint])[];
/** Armour plates on the deck (right half): centre, size, turn. */
const PLATES = [
  [[48, 14], [12, 20], -0.25],
  [[50, -30], [12, 22], 0.2],
  [[20, -82], [14, 10], 0],
] as const;

/** The hull with its crimson rim, the engine block, the bastions out to the turntables. */
function drawHull({ hull, neon }: EnemyParts): void {
  hull.bevelSlab(HULL, [-10, -2, DECK_TOP], [3, 3], H.dark, {}, H.base);
  const all = HULL.map((_, i) => i);
  edgeLights(neon, HULL, all, [-2.8, -1.4], CRIMSON);
  edgeLights(neon, HULL, all, [-8.6, -7.8], HEAT.glow, 0.2);
  hull.bevelSlab(ENGINES, [-8, -1, 6], [1, 1.5], H.dark, {}, HEAT.soot);
  for (const s of SIDES) {
    const bastion = s > 0 ? BASTION : flipX(BASTION);
    hull.bevelSlab(bastion, [-5, -1, BASTION_TOP], [1, 2], H.base, {}, HEAT.blued);
    edgeLights(neon, bastion, [0, 1, 2, 3, 4], [-1.4, -0.4], GOLD);
    edgeLights(neon, bastion, [1, 2, 3], [-4.2, -3.6], CRIMSON);
  }
}

/** The deck's dressing: molten seams, armour plates, vents and hazard bands. */
function drawDeck({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    for (const [a, b] of SEAMS) {
      glowLine(
        neon,
        [
          [s * a[0], a[1]],
          [s * b[0], b[1]],
        ],
        DECK_TOP - 0.3,
        HEAT.molten,
      );
    }
    for (const [[x, z], size, turn] of PLATES) {
      plate(hull, rect([s * x, z], size, s * turn), DECK_TOP, H.panel, 0.8);
    }
    grille(hull, [s * 30, -40], [10, 12], [4, DECK_TOP + 0.05]);
    grille(hull, [s * 44, 40], [8, 10], [3, DECK_TOP + 0.05], s * 0.4);
  }
  hazard(hull, [0, 46], [24, 4], 6, DECK_TOP + 0.05);
  hazard(hull, [0, -80], [30, 4], 7, DECK_TOP + 0.05);
}

/** The prow's gun deck: twin cannons and a laser lens, charging before they fire. */
function drawProw({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.bevelSlab(PROW, [DECK_TOP - 1, DECK_TOP, PROW_TOP], [0, 1.5], H.panel, {}, HEAT.blued);
  edgeLights(neon, PROW, [0, 1, 2, 3], [PROW_TOP - 2.6, PROW_TOP - 1.8], CRIMSON);
  decal(neon, rect([0, 70], [20, 1.4]), PROW_TOP + 0.05, GOLD);
  const front = 92;
  for (const m of CALDERA_GUNS) {
    const tip = bossPoint(...m);
    const along = (z: number): Placement => ({ at: [tip[0], tip[1], z], pitch: QUARTER });
    hull.cylinder(2.4, 6, 6, H.dark, along(front - 14));
    hull.cylinder(1.9, tip[2] - 2 - (front - 8), 6, H.dark, along(front - 8), 1.6);
    charge.cylinder(1.8, 2, 6, WHITE, along(tip[2] - 2), 1.3);
    muzzle(tip);
  }
  const lens = bossPoint(...CALDERA_LENS);
  const lensAt = lens[2] - LENS[3][1];
  const along = (z: number): Placement => ({ at: [0, lens[1], z], pitch: QUARTER });
  hull.cylinder(4.6, lensAt - (front - 16), 8, H.base, along(front - 16), 4);
  neon.ring(4.5, 1.2, 8, HEAT.molten, along(lensAt - 6));
  charge.lathe(LENS, 8, WHITE, along(lensAt));
  muzzle(lens, 'laser');
}

/** The missile hatches in their block behind the keep, lit as missiles load. */
function drawHatches({ hull, neon, charge, muzzle }: EnemyParts): void {
  const height = CALDERA_HATCHES[0]?.[2] ?? DECK_TOP;
  hull.bevelSlab(HATCH_BLOCK, [DECK_TOP - 1, DECK_TOP, height - 0.08], [0, 1], H.base);
  for (const m of CALDERA_HATCHES) {
    const [x, y, z] = bossPoint(...m);
    decal(hull, rect([x, z], [7, 6]), y - 0.06, H.dark);
    decal(charge, rect([x, z], [5, 4]), y, WHITE);
    muzzle([x, y, z], 'missile');
  }
  neon.box([22, 0.8, 0.6], GOLD, { at: [0, DECK_TOP + 1, -51.6] });
}

/**
 * P10-R11: the Caldera Throne, the enemy's war fortress rising from the magma lake (6.5 L),
 * crimson and gold neon over its whole hull: a stepped keep and throne tower over its core, a
 * prow carrying twin cannons and a laser, magma cannons on its bastions, missile batteries and
 * smokestacks aft, heat shield generators ahead of the keep.
 */
export function buildCalderaThrone(scene: Scene): EnemyModel {
  return buildBossModel(CALDERA_THRONE, scene, CRIMSON, {
    core: (p) => {
      drawHull(p);
      drawDeck(p);
      drawKeep(p);
      drawProw(p);
      drawHatches(p);
      for (const s of SIDES) {
        p.reactor([s * 12, -1, -102], 6);
        p.reactor([s * 28, -1, -102], 4.5);
      }
    },
    parts: {
      'magma-left': magmaMount,
      'magma-right': magmaMount,
      'battery-left': missileBattery,
      'battery-right': missileBattery,
      'shield-left': shieldGenerator,
      'shield-right': shieldGenerator,
    },
    turrets: { 'magma-left': magmaCannon, 'magma-right': magmaCannon },
  });
}
