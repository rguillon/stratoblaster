import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { organ, segmentedBody } from '../../../render/geometry/organic';
import { REFINERY_TITAN } from '../../config/bosses/final-bosses';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { SIDES } from '../enemies/enemy-shapes';
import { eyes, reactorSac } from '../enemies/organic-parts';
import { buildBossModel } from './boss-model';
import {
  drawMissileBattery,
  drawRotary,
  drawTank,
  drawTurret,
  TITAN_DECK,
  TITAN_NEON,
} from './refinery-titan-parts';
import {
  barbs,
  F,
  gland,
  graft,
  hide,
  M,
  mantle,
  polygon,
  ribCage,
  spine,
  tentacle,
  veinLine,
} from './world-1-organic-kit';

// P07-R05, P16-R06: the Refinery Titan, World 1's 1-4 final boss. Model space: logical pixels,
// nose +Z (down the screen), Y up towards the camera. A bloated industrial beetle: a huge
// shelled body plumbed with grafted pipes, limbs cradling two glowing fuel bladders, smoking
// chimneys of flesh on its back, a fleshy apron in front carrying the two rotary turrets.
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

/** The apron of flesh the turrets stand on. */
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
/** A chimney of flesh (lathe profile, bottom to top). */
const COLUMN = [
  [5, 0],
  [4, 1.5],
  [3.4, 13],
  [4, 15],
  [2.5, 17],
] as const;

/** The body (P16-R06): a huge shelled abdomen, ribs, a spine vein, armour plates grafted on. */
function drawStructure(p: EnemyParts): void {
  hide(p, {
    tail: -62,
    nose: 68,
    width: 36,
    bottom: -8,
    top: 18,
    segments: 6,
    shell: [F.sinew, F.crimson],
    belly: F.purple,
  });
  mantle(p, SPONSON, [-4, TITAN_DECK.sponson], F.crimson, TITAN_NEON);
  p.neon.box([72, 1.2, 0.8], TITAN_NEON, { at: [0, -0.6, 40.2] });
  ribCage(p, [-46, -36, 50], { halfWidth: 33, y: 0, height: 15, thickness: 1.5 });
  spine(p, [0, 18.5, -55], [0, 18.5, 25], { color: TITAN_NEON, width: 1.8 });
  for (const s of SIDES) {
    for (const z of [-48, 8]) {
      graft(p, polygon(6, 6, [1.2, 1.8]), [13, 14.6], [s * 20, 0, z], { color: M.base });
    }
    for (const z of [-40, -18]) {
      veinLine(p, [s * 12, 17, z], [s * 34, 4, z + 6], [s * 3, 4, 0], 1.4, TITAN_NEON);
    }
    gland(p, [s * 28, 8, 34], 2, TITAN_NEON);
  }
}

/**
 * The limbs holding the fuel bladders (P16-R06): a jointed bone-and-sinew limb out to each, its
 * claw curled round the bladder's outer side, lit along its top.
 */
function drawCradles(p: EnemyParts): void {
  for (const s of SIDES) {
    for (const z of [-30, -6]) {
      const elbow: [number, number, number] = [s * 86, 14, z];
      tentacle(p, [s * 30, 6, z], elbow, [0, 8, 0], [4, 3], F.sinew, 5);
      tentacle(p, elbow, [s * 92, -3, z + 4], [s * 2, 0, 0], [3, 0.6], F.bone, 4);
      veinLine(p, [s * 40, 13, z], [s * 84, 17, z], [0, 5, 0], 1, TITAN_NEON);
    }
    p.neon.box([1.6, 0.6, 30], TITAN_NEON, { at: [s * 88, 13, -18] });
  }
}

/** The fuel lines: grafted pipes across into the bladders, along the back, with couplings. */
function drawPipes({ hull }: EnemyParts): void {
  // Rolled a quarter turn, a cylinder runs along +X from where it stands.
  for (const z of [-10, -26]) {
    hull.cylinder(2.2, 108, 6, M.panel, { at: [-54, 9, z], roll: -QUARTER });
    for (const s of SIDES) {
      hull.cylinder(3.1, 2.4, 6, M.dark, { at: [s * 44 - 1.2, 9, z], roll: -QUARTER });
    }
  }
}

/** Two chimneys of flesh behind the body, ringed with neon, joined by a grafted pipe. */
function drawColumns(p: EnemyParts): void {
  for (const s of SIDES) {
    const at = [s * 42, TITAN_DECK.beam - 0.5, -34] as const;
    p.flesh.lathe(COLUMN, 7, F.crimson, { at });
    for (const dy of [5, 10]) p.neon.ring(4, 1, 7, TITAN_NEON, { at: [at[0], at[1] + dy, at[2]] });
    p.vein.ring(2.6, 0.8, 7, TITAN_NEON, { at: [at[0], at[1] + 16.6, at[2]] });
  }
  p.hull.cylinder(1.6, 84, 6, M.dark, { at: [-42, 13, -34], roll: -QUARTER });
}

/**
 * The head over the core (P16-R06): a plated skull with clustered eyes, two smoking spiracles,
 * the twin cannon grafted under its brow (the core's weapon), mandibles at its front.
 */
function drawBridge(p: EnemyParts): void {
  organ(p.flesh, 17, 8, F.crimson, { at: [0, 12, 2], yaw: Math.PI / 8 }, 0.38);
  graft(p, polygon(6, 11, [1, 1.3]), [23, 24.5], [0, 0, 0]);
  eyes(p, [0, 22, 15], { count: 4, size: 1.2, spacing: 3.4 }, TITAN_NEON);
  for (const s of SIDES) {
    p.flesh.cylinder(3.2, 8, 6, F.sinew, { at: [s * 9, 22, -14] }, 2.6);
    p.neon.ring(2.7, 0.8, 6, TITAN_NEON, { at: [s * 9, 29.5, -14] });
    // The twin cannon's barrels, out of a mantlet on the head's front.
    p.hull.cylinder(1.8, 14, 6, M.dark, { at: [s * 4.5, 19, 20], pitch: QUARTER });
    p.charge.cylinder(2.2, 1.8, 6, WHITE, { at: [s * 4.5, 19, 34], pitch: QUARTER });
    p.muzzle([s * 4.5, 19, 35.8]);
    tentacle(p, [s * 8, 4, 62], [s * 3, 3, 70], [s * 3, 0, 0], [2.4, 0.2], F.bone, 4);
  }
  p.hull.box([15, 4, 7], M.base, { at: [0, 17, 21] }, M.panel);
  eyes(p, [0, 6.5, 60], { count: 2, size: 1.2, spacing: 6 }, TITAN_NEON);
  barbs(p, [0, 17, -50], { count: 3, spacing: 0.1, size: 4, dir: [0, 1, -0.5] });
}

/** The core: body, cradles, pipes, head, chimneys, and four reactors at the tail in sacs. */
function drawCore(p: EnemyParts): void {
  drawStructure(p);
  drawCradles(p);
  drawPipes(p);
  drawBridge(p);
  drawColumns(p);
  for (const s of SIDES) {
    segmentedBody(
      p.flesh,
      { tail: -62, nose: -30, segments: 2, width: 8, bottom: -3, top: 12 },
      F.crimson,
      { at: [s * 11, 0, 0] },
    );
    reactorSac(p, [s * 11, 4, -62], 6, TITAN_NEON);
    reactorSac(p, [s * 48, -1, -42], 4, TITAN_NEON);
  }
}

/**
 * P07-R05, P16-R06: the Refinery Titan, a bloated industrial beetle (5.5 L) with orange veins:
 * two big fuel bladders glowing in its limbs, two rotary turrets on its front apron, a missile
 * brood on its back, and its plated head with a twin cannon over the core.
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
    turrets: { 'turret-left': drawRotary, 'turret-right': drawRotary },
  });
}
