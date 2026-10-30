import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { EnemyModel } from '../../../../render/game-view';
import {
  OBELISKS,
  SKY_TEMPLE,
  TEMPLE_CRYSTAL,
  TEMPLE_GUNS,
  TEMPLE_PARTS,
} from '../../../config/bosses/world-3/sky-temple';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint, buildBossModel } from '../boss-model';
import { barrels } from '../final-boss-shapes';
import { H, neonBand, socket, WHITE } from '../mini-boss-shapes';
import {
  beacon,
  obelisk,
  SQUARE,
  SUMMIT,
  TEMPLE_CYAN,
  TEMPLE_GOLD,
  TIERS,
} from './sky-temple-parts';
import { templeJungle, templeMachinery } from './sky-temple-details';
import { templeBody } from './sky-temple-flesh';
import { F } from './jungle-flesh';
import { bar, STONE } from './stone-idol-stone';

// P09-R09, 3-3: the Sky Temple. Logical pixels, nose +Z (its grand stair, down the screen), Y up
// (towards the camera).

/** A square outline `half` from the centre to each side. */
const square = (half: number): OutlinePoint[] => [
  [half, half],
  [-half, half],
  [-half, -half],
  [half, -half],
];
/** The rock it was torn from, under its base: an upside-down four-sided cone (lathe profile). */
const ROOTS = [
  [0, -34],
  [57, -20],
  [99, -4],
  [104.6, 0],
] as const;
/** The grand stair up its front face: steps from beyond the base to the summit. */
const STAIR = { steps: 9, width: 20, front: 88, depth: 5.8, bottom: -4 } as const;
/** The sanctum on the summit (the core): its centre along Z, its size, its door's face. */
const SANCTUM = { z: -8, size: [30, 10, 24], door: 4 } as const;

/** The stepped pyramid: its tiers, each trimmed with neon, and the rock under it. */
function drawPyramid(p: EnemyParts): void {
  const { hull, neon } = p;
  // P16-R06: the lowest tier is the living beast itself; the stone tiers grew on its back.
  templeBody(p);
  TIERS.halves.forEach((half, i) => {
    const y = i * TIERS.height;
    if (i > 0)
      hull.box([half * 2, TIERS.height, half * 2], STONE.base, { at: [0, y, 0] }, STONE.light);
    const trim = i === 0 ? TEMPLE_CYAN : TEMPLE_GOLD;
    neonBand(
      neon,
      square(half),
      [y + TIERS.height - 1.4, y + TIERS.height - 0.6],
      [1.006, 1.006],
      trim,
    );
  });
  p.flesh.lathe(ROOTS, 4, F.sinew, { yaw: SQUARE }, false);
}

/** The grand stair, its walls and its cyan balustrades. */
function drawStair({ hull, neon }: EnemyParts): void {
  const { steps, width, front, depth, bottom } = STAIR;
  const rise = (SUMMIT - bottom) / steps;
  for (let i = 0; i < steps; i++) {
    const top = i === steps - 1 ? STONE.light : STONE.base;
    const at: [number, number, number] = [0, bottom, front - depth * (i + 0.5)];
    hull.box([width, rise * (i + 1), depth], STONE.dark, { at }, top);
  }
  const [low, high] = [front, front - depth * steps];
  for (const s of SIDES) {
    const x = s * (width / 2 + 1.2);
    bar(hull, [x, rise + bottom + 1, low], [x, SUMMIT + 2, high], [2.4, 3], STONE.base);
    bar(neon, [x, rise + bottom + 2.6, low], [x, SUMMIT + 3.6, high], [0.7, 0.6], TEMPLE_CYAN);
  }
}

/** The sanctum (the core): its roofs, its crystal (rings, spirals), its door and twin cannons. */
function drawSanctum(p: EnemyParts): void {
  const { hull, neon, charge, muzzle } = p;
  const [w, h, d] = SANCTUM.size;
  hull.box([w, h, d], STONE.base, { at: [0, SUMMIT, SANCTUM.z] }, STONE.light);
  hull.box([w - 6, 3, d - 6], STONE.base, { at: [0, SUMMIT + h, SANCTUM.z] }, STONE.light);
  hull.box([w - 14, 3, d - 12], STONE.gilt, { at: [0, SUMMIT + h + 3, SANCTUM.z] });
  neonBand(neon, square(w / 2), [SUMMIT + h - 1.4, SUMMIT + h - 0.6], [1, 1], TEMPLE_GOLD, {
    at: [0, 0, SANCTUM.z],
  });
  const roof = SUMMIT + h + 6;
  for (const crystal of TEMPLE_CRYSTAL.map((m) => bossPoint(...m))) {
    const [x, y, z] = crystal;
    hull.cylinder(3.6, 2, 6, STONE.dark, { at: [x, roof, z] }, 3);
    const gem = [
      [2.4, roof + 2],
      [3.6, roof + 6],
      [0, y],
    ] as const;
    charge.lathe(gem, 6, WHITE, { at: [x, 0, z] });
    neon.ring(3.8, 0.6, 6, TEMPLE_CYAN, { at: [x, roof + 5.6, z] });
    muzzle(crystal, 'ring');
  }
  // The door, framed in cyan, between two pillars.
  const door = SANCTUM.door;
  hull.box([10, 8, 0.6], STONE.deep, { at: [0, SUMMIT, door + 0.1] });
  neon.box([12, 0.7, 0.5], TEMPLE_CYAN, { at: [0, SUMMIT + 8, door + 0.3] });
  for (const s of SIDES) {
    neon.box([0.7, 8, 0.5], TEMPLE_CYAN, { at: [s * 5.6, SUMMIT, door + 0.3] });
    hull.box([3, h, 3], STONE.light, { at: [s * 13, SUMMIT, door + 1] });
  }
  drawCannons(p);
}

/** The twin cannons either side of the door (aimed shots, spreads, bursts, fans). */
function drawCannons(p: EnemyParts): void {
  const [gun] = TEMPLE_GUNS.map((m) => bossPoint(...m));
  if (!gun) return;
  const [x, y, z] = gun;
  const radius = 1.4;
  // The charge light at a barrel's tip is `1.4 radius` long (see `barrels`).
  const length = z - SANCTUM.door - radius * 1.4;
  for (const s of SIDES) {
    p.hull.box([5, 5, 6], H.panel, { at: [s * x, y - 2.5, SANCTUM.door] }, H.base);
    p.neon.box([5.2, 0.5, 0.5], TEMPLE_GOLD, { at: [s * x, y + 1.6, SANCTUM.door + 3.1] });
  }
  barrels(p, [0, y, SANCTUM.door], [2, Math.abs(x) * 2], [radius, length]);
}

/** Braziers on the summit's corners, flaring as the next attack charges. */
function drawBraziers({ hull, charge }: EnemyParts): void {
  const at = TIERS.halves.at(-1) ?? 34;
  for (const x of SIDES) {
    for (const z of SIDES) {
      const spot: [number, number, number] = [x * (at - 4), SUMMIT, z * (at - 4)];
      hull.cylinder(2.6, 2.4, 6, STONE.dark, { at: spot }, 3);
      charge.cylinder(2, 3, 6, WHITE, { at: [spot[0], SUMMIT + 2.4, spot[2]] }, 0.3);
    }
  }
}

/**
 * P09-R09: the Sky Temple, a flying stepped pyramid with four corner obelisks, gold and cyan
 * neon: a sanctum on its summit, a beacon before it, a grand stair, the jungle's moss and vines
 * over its stones, and the dark metal of a fortress under them (thrusters, buttresses).
 */
export function buildSkyTemple(scene: Scene): EnemyModel {
  const parts = Object.fromEntries(Object.keys(OBELISKS).map((id) => [id, obelisk]));
  return buildBossModel(SKY_TEMPLE, scene, TEMPLE_GOLD, {
    core: (p) => {
      drawPyramid(p);
      drawStair(p);
      drawSanctum(p);
      drawBraziers(p);
      templeMachinery(p);
      templeJungle(p);
      for (const [x, y] of Object.values(OBELISKS)) {
        socket(p.hull, bossPoint(x, y, TIERS.height), 7, 0.6);
      }
      socket(p.hull, bossPoint(...TEMPLE_PARTS.beacon, SUMMIT), 7, 0.6);
    },
    parts: { ...parts, beacon },
  });
}
