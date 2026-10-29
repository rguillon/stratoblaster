import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import {
  ARK_PARTS,
  ARK_TAPS,
  ARK_THROAT,
  FOUNDRY_ARK,
} from '../../../config/bosses/world-4/foundry-ark';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, flipX, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { grille, hazard } from '../final-boss-greebles';
import { seam, vent } from '../mini-boss-greebles';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { box2d, edgeLights, symmetric } from '../overlord-city';
import {
  ARK_ORANGE,
  ARK_RED,
  battery,
  chimneyRow,
  crucible,
  DECK_TOP,
  MOLTEN,
  railCannon,
  railMount,
  SOOT,
} from './foundry-ark-parts';
import { backRibs, glands, magmaVein, reactorSacs, SKIN } from './living-forge';
import { drawYard } from './foundry-ark-yard';

// P10-R11, 4-4: the Foundry Ark. Model space: logical pixels, nose +Z (down the screen), Y up
// towards the camera; +X is the screen's left. A huge flying foundry: an iron deck carrying a
// blast furnace at its heart, slag channels glowing from it to the crucibles aft, a chimney row
// on the foredeck, a missile battery on the bow and outriggers out to the rail cannons.
// P16-R06: a living colossus, its broad back scorched flesh ribbed in bone, its furnace a swollen
// heart, slag running in its veins, its stacks, engines, rails and guns metal grafts.

/** The deck (right half, front to tail), closed across the bow. */
const DECK = symmetric(
  [
    [16, 98],
    [40, 86],
    [56, 60],
    [60, 20],
    [62, -40],
    [56, -76],
    [42, -94],
    [14, -98],
  ],
  100,
);
/** The right outrigger (mirrored on the left), out to the rail cannon's turntable. */
const OUTRIGGER: OutlinePoint[] = [
  [56, 28],
  [80, 24],
  [86, 18],
  [86, 4],
  [80, -2],
  [56, -8],
];
/** The engine block across the stern. */
const ENGINES = box2d(70, 12, [0, -94]);
/** The blast furnace: its octagonal hearth, then its tapering stack (lathe profiles). */
const HEARTH = [
  [25, 0],
  [25, 9],
  [21, 13],
  [15, 15],
] as const;
const STACK = [
  [13, 0],
  [11.5, 12],
  [9.5, 18],
  [11, 19.5],
] as const;
const HEARTH_FOOT = DECK_TOP - 1;
const STACK_FOOT = HEARTH_FOOT + 15;
/** The slag channels from the furnace out to each crucible (the right one; mirrored). */
const CHANNEL: readonly OutlinePoint[] = [
  [18, -14],
  [36, -28],
  [ARK_PARTS.crucible[0] - 8, -ARK_PARTS.crucible[1]],
];

/** The deck with its lit rim, the outriggers, the engine block, rust and soot. */
function drawHull(p: EnemyParts): void {
  const { hull, neon } = p;
  p.flesh.bevelSlab(DECK, [-10, -3, DECK_TOP], [3, 3], SKIN.base, {}, SKIN.dark);
  backRibs(p, [-80, -66, 60, 72], { halfWidth: 46, y: 0, height: 5.5, thickness: 1.2 });
  edgeLights(neon, DECK, [1, 2, 3, 4, 13, 14, 15, 16], [-3, -1.8], ARK_ORANGE);
  hull.bevelSlab(ENGINES, [-8, -1, 7], [1, 1.5], H.dark, {}, H.panel);
  for (const s of SIDES) {
    const wing = s > 0 ? OUTRIGGER : flipX(OUTRIGGER);
    p.flesh.bevelSlab(wing, [-5, -1, DECK_TOP - 0.6], [1, 2], SKIN.panel, {}, SKIN.dark);
    magmaVein(
      p,
      [
        [s * 20, DECK_TOP + 0.3, -50],
        [s * 44, DECK_TOP + 0.3, -36],
        [s * 56, DECK_TOP + 0.3, -10],
      ],
      1.6,
      MOLTEN,
    );
    glands(
      p,
      [
        [s * 50, DECK_TOP, 10],
        [s * 18, DECK_TOP, 84],
      ],
      2.6,
      ARK_ORANGE,
    );
    edgeLights(neon, wing, [0, 1, 2, 3, 4], [-2, -1], ARK_ORANGE);
    for (const z of [-60, -20, 40]) vent(hull, [s * 48, DECK_TOP, z], [8, 10], 4);
    hazard(hull, [s * 40, 76], [10, 6], 4, DECK_TOP + 0.05);
    grille(hull, [s * 26, -72], [14, 10], [5, DECK_TOP + 0.05]);
    decal(hull, box2d(20, 14, [s * 30, 40]), DECK_TOP + 0.04, SOOT);
    seam(hull, [s * 8, 96], [s * 8, -90], [DECK_TOP, 1.4, 0.6], SHADE.edge);
  }
}

/** The blast furnace (the core): hearth, stack, glowing slits, the furnace door and tap guns. */
function drawFurnace(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  p.flesh.lathe(HEARTH, 8, SKIN.base, { at: [0, HEARTH_FOOT, 0], yaw: Math.PI / 8 });
  hull.lathe(STACK, 8, H.panel, { at: [0, STACK_FOOT, 0], yaw: Math.PI / 8 });
  hull.ring(11.2, 2.6, 8, SOOT, { at: [0, STACK_FOOT + 17, 0], yaw: Math.PI / 8 });
  neon.ring(12.3, 0.8, 8, ARK_ORANGE, { at: [0, STACK_FOOT + 6, 0], yaw: Math.PI / 8 });
  for (let k = 0; k < 8; k++) {
    const a = (k * Math.PI) / 4;
    const at: [number, number, number] = [Math.sin(a) * 25.2, HEARTH_FOOT + 3, Math.cos(a) * 25.2];
    if (k !== 0) neon.box([3, 4, 0.4], MOLTEN, { at, yaw: a });
  }
  const [throat] = [ARK_THROAT].map((m) => bossPoint(...m));
  if (throat) {
    charge.cylinder(9, 0.4, 8, WHITE, { at: [0, throat[1] - 0.6, throat[2]] });
    muzzle(throat, 'ring');
  }
  charge.box([9, 6, 0.6], WHITE, { at: [0, HEARTH_FOOT + 2, 25.2] });
  for (const tip of ARK_TAPS.map((m) => bossPoint(...m))) {
    const [x, y, z] = tip;
    hull.box([4, 4, 5], H.dark, { at: [x, y - 2, z - 9] }, SHADE.edge);
    hull.cylinder(1.4, 7.6, 6, H.dark, { at: [x, y, z - 8.4], pitch: QUARTER });
    charge.cylinder(1.45, 0.8, 6, WHITE, { at: [x, y, z - 0.8], pitch: QUARTER });
    muzzle(tip);
  }
}

/** The slag channels glowing across the deck from the furnace to the crucibles. */
function drawChannels({ hull, neon, flesh }: EnemyParts): void {
  for (const s of SIDES) {
    CHANNEL.slice(1).forEach((b, i) => {
      const a = CHANNEL[i];
      if (!a) return;
      seam(flesh, [s * a[0], a[1]], [s * b[0], b[1]], [DECK_TOP, 5, 1], SKIN.panel);
      seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [DECK_TOP + 0.4, 2.6, 0.7], MOLTEN);
    });
  }
  // Rail lines down the deck for the ore wagons, between the furnace and the battery.
  for (const s of SIDES) seam(hull, [s * 3, 34], [s * 3, 70], [DECK_TOP, 0.8, 0.5], SHADE.edge);
}

/** The engines' nozzles at the stern, and red lamps on the deck's corners. */
function drawStern(p: EnemyParts): void {
  for (const s of SIDES) {
    reactorSacs(p, [[s * 12, 1, -100.2]], 5.5, MOLTEN);
    reactorSacs(p, [[s * 28, 1, -100.2]], 4.2, MOLTEN);
    p.neon.box([1.2, 0.8, 1.2], ARK_RED, { at: [s * 56, DECK_TOP + 0.2, -74] });
    p.neon.box([1.2, 0.8, 1.2], ARK_RED, { at: [s * 40, DECK_TOP + 0.2, 86] });
  }
}

/**
 * P10-R11: the Foundry Ark, a huge flying foundry (6 L) of sooty iron under orange neon: a blast
 * furnace at its heart, slag channels glowing out to two crucibles hung in gantries aft, a chimney
 * row on the foredeck, a missile battery on the bow and two rail cannons on outriggers.
 */
export function buildFoundryArk(scene: Scene): EnemyModel {
  return buildBossModel(FOUNDRY_ARK, scene, ARK_ORANGE, {
    core: (p) => {
      drawHull(p);
      drawChannels(p);
      drawYard(p);
      drawFurnace(p);
      drawStern(p);
    },
    parts: {
      'rail-left': railMount,
      'rail-right': railMount,
      chimneys: chimneyRow,
      battery,
      'crucible-left': crucible,
      'crucible-right': crucible,
    },
    turrets: { 'rail-left': railCannon, 'rail-right': railCannon },
  });
}
