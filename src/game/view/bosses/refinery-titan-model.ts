import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { REFINERY_TITAN } from '../../config/bosses/final-bosses';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import {
  angryEyes,
  decal,
  HULL_SECTION,
  POD_SECTION,
  sideStripe,
  SIDES,
} from '../enemies/enemy-shapes';
import { buildBossModel } from './boss-model';
import {
  drawMissileBattery,
  drawTank,
  drawTurret,
  rect,
  TITAN_DECK,
  TITAN_NEON,
} from './refinery-titan-parts';

// P07-R05: the Refinery Titan, World 1's 1-4 final boss. Model space: logical pixels, nose +Z
// (down the screen), Y up towards the camera. A heavy industrial hull with pipes, a beam across
// it cradling the two fuel tanks, a sponson in front carrying the two rotary turrets.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** The heavy hull (loft stations: z, half width, bottom, top), tail to nose. */
const TITAN_HULL = [
  [-62, 24, -5, 9],
  [-50, 29, -6, 12],
  [-34, 34, -7, 15],
  [-8, 36, -8, 16],
  [12, 34, -7.5, 15],
  [32, 29, -6.5, 13],
  [50, 20, -5, 9],
  [62, 11, -4, 6],
  [68, 5, -3, 3.5],
] as const;
/** Armour over the hull's front, between the bridge and the nose: a chevron, chamfered. */
const PROW_ARMOUR: OutlinePoint[] = [
  [0, 50],
  [14, 40],
  [17, 28],
  [9, 30],
  [0, 36],
  [-9, 30],
  [-17, 28],
  [-14, 40],
];
/** A cracking column (lathe profile, bottom to top). */
const COLUMN = [
  [5, 0],
  [4, 1.5],
  [4, 15],
  [2.5, 17],
  [0, 17.5],
] as const;

/** The engine nacelles at the tail (loft stations), sunk in the hull's back. */
const NACELLE = [
  [-62, 7.5, -3, 11],
  [-52, 8.5, -3.5, 13],
  [-36, 6, -2, 12.5],
  [-28, 0, 9, 9],
] as const;
/** The beam across the hull the tanks lie on, and the cradle arms outside them. */
const TANK_BEAM: OutlinePoint[] = [
  [-94, -4],
  [-94, -30],
  [-86, -42],
  [86, -42],
  [94, -30],
  [94, -4],
  [84, 4],
  [-84, 4],
];
/** The front sponson the turrets stand on. */
const SPONSON: OutlinePoint[] = [
  [-50, 12],
  [-50, 32],
  [-42, 40],
  [42, 40],
  [50, 32],
  [50, 12],
  [42, 4],
  [-42, 4],
];
/** The bridge on the hull's back, over the core. */
const BRIDGE: OutlinePoint[] = [
  [0, 24],
  [12, 18],
  [16, 4],
  [16, -14],
  [10, -20],
  [-10, -20],
  [-16, -14],
  [-16, 4],
  [-12, 18],
];

/** The hull, its flank stripes, the beam with its cradle arms and the sponson. */
function drawStructure({ hull, neon }: EnemyParts): void {
  hull.loft(HULL_SECTION, TITAN_HULL, H.base);
  for (const side of [1, 3]) {
    const stripe = sideStripe(HULL_SECTION, side, [0.2, 0.45], 1.07);
    neon.loft(stripe, TITAN_HULL.slice(2, 7), TITAN_NEON, {}, { open: true });
  }
  hull.bevelSlab(TANK_BEAM, [-5, -1, TITAN_DECK.beam], [1, 2], H.dark, {}, H.base);
  hull.bevelSlab(SPONSON, [-4, 0, TITAN_DECK.sponson], [2, 3], H.base, {}, H.panel);
  // A neon edge along the sponson's front.
  neon.box([72, 1.2, 0.8], TITAN_NEON, { at: [0, -0.6, 40.2] });
  for (const s of SIDES) {
    // The cradle arm outside each tank, lit along its top.
    hull.bevelSlab(rect(8, 40, [s * 87, -18]), [3, 3, 13], [0, 2], H.panel, {}, H.base);
    decal(neon, rect(1.6, 30, [s * 87, -18]), 13.05, TITAN_NEON);
  }
}

/** The fuel lines: pipes across into the tanks, along the back, with their couplings. */
function drawPipes({ hull }: EnemyParts): void {
  // Rolled a quarter turn, a cylinder runs along +X from where it stands.
  for (const z of [-10, -26]) {
    hull.cylinder(2.2, 108, 6, H.panel, { at: [-54, 9, z], roll: -QUARTER });
    for (const s of SIDES) {
      hull.cylinder(3.1, 2.4, 6, H.dark, { at: [s * 44 - 1.2, 9, z], roll: -QUARTER });
    }
  }
  for (const s of SIDES) {
    hull.cylinder(2, 44, 6, H.panel, { at: [s * 19, 15.6, -22], pitch: QUARTER });
  }
}

/** The gantries over each tank: posts on the hull and the cradle arm, a lit bar between. */
function drawGantries({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    for (const z of [-28.5, -4.5]) {
      hull.box([3, 19, 3], H.dark, { at: [s * 51, 9, z] });
      hull.box([3, 15, 3], H.dark, { at: [s * 87, 13, z] });
      hull.bevelSlab(rect(39, 3.4, [s * 69, z]), [27, 27, 29.5], [0, 0.7], H.panel, {}, H.base);
      decal(neon, rect(2.2, 1.6, [s * 86, z]), 29.55, TITAN_NEON);
    }
  }
}

/** The engine nacelles at the tail, with neon stripes, and the armour over the prow. */
function drawArmour({ hull, neon }: EnemyParts): void {
  // Pitched to lie on the hull's back as it slopes down to the nose.
  const prow = { at: [0, 20, 0] as const, pitch: 0.22 };
  hull.bevelSlab(PROW_ARMOUR, [-1.5, -1.5, 2.5], [0, 1.5], H.panel, prow, H.base);
  for (const s of SIDES) {
    hull.loft(POD_SECTION, NACELLE, H.panel, { at: [s * 11, 0, 0] });
    const stripe = sideStripe(POD_SECTION, s > 0 ? 1 : 3, [0.3, 0.6]);
    neon.loft(stripe, NACELLE.slice(0, 3), TITAN_NEON, { at: [s * 11, 0, 0] }, { open: true });
  }
}

/** Two cracking columns on the beam behind the hull, ringed with neon, joined by a pipe. */
function drawColumns({ hull, neon }: EnemyParts): void {
  for (const s of SIDES) {
    const at = [s * 42, TITAN_DECK.beam - 0.5, -34] as const;
    hull.lathe(COLUMN, 8, H.panel, { at });
    for (const dy of [5, 10]) neon.ring(4.15, 1, 8, TITAN_NEON, { at: [at[0], at[1] + dy, at[2]] });
  }
  hull.cylinder(1.6, 84, 6, H.dark, { at: [-42, 13, -34], roll: -QUARTER });
}

/** The bridge over the core: its angry visor, smoke stacks and twin cannon (the core's weapon). */
function drawBridge({ hull, neon, charge }: EnemyParts): void {
  hull.bevelSlab(BRIDGE, [14, 14, 24], [0, 3], H.panel, {}, H.base);
  for (const eye of angryEyes([0, 15], 2, [7, 1.4], 0.35)) decal(neon, eye, 24.05, TITAN_NEON);
  for (const s of SIDES) {
    neon.box([0.5, 1.2, 14], TITAN_NEON, { at: [s * 14.9, 17.4, -5] });
    // Refinery stacks behind the visor, glowing at the top.
    hull.cylinder(3.2, 8, 6, H.dark, { at: [s * 9, 22, -14] }, 2.6);
    neon.ring(2.7, 0.8, 6, TITAN_NEON, { at: [s * 9, 29.5, -14] });
    // The twin cannon's barrels, out of a mantlet on the bridge's front.
    hull.cylinder(1.8, 14, 6, H.dark, { at: [s * 4.5, 19, 20], pitch: QUARTER });
    charge.cylinder(2.2, 1.8, 6, WHITE, { at: [s * 4.5, 19, 34], pitch: QUARTER });
  }
  hull.bevelSlab(rect(15, 7, [0, 21]), [15, 15, 22.5], [0, 1.5], H.base, {}, H.panel);
  // Headlights on the nose.
  for (const eye of angryEyes([0, 60], 2, [6, 1.4], 0.3)) decal(neon, eye, 7.4, TITAN_NEON);
}

/** The core: hull, beam, sponson, pipes, bridge, and four reactors at the tail. */
function drawCore(parts: EnemyParts): void {
  drawStructure(parts);
  drawPipes(parts);
  drawBridge(parts);
  drawGantries(parts);
  drawArmour(parts);
  drawColumns(parts);
  for (const s of SIDES) {
    parts.reactor([s * 11, 4, -62], 6);
    parts.reactor([s * 48, -1, -42], 4);
  }
}

/**
 * P07-R05: the Refinery Titan, a heavy tanker-gunship (5.5 L) with orange neon: two big fuel
 * tanks glowing on its sides, two rotary turrets on its front sponson, a missile battery on its
 * back, and a bridge with a twin cannon over the core.
 */
export function buildRefineryTitan(scene: Scene): EnemyModel {
  return buildBossModel(REFINERY_TITAN, scene, TITAN_NEON, {
    core: drawCore,
    parts: {
      'tank-left': drawTank,
      'tank-right': drawTank,
      'turret-left': drawTurret,
      'turret-right': drawTurret,
      'missile-battery': drawMissileBattery,
    },
  });
}
