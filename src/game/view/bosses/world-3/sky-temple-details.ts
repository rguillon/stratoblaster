import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { lamps } from '../mini-boss-greebles';
import { H, QUARTER } from '../mini-boss-shapes';
import { SUMMIT, TEMPLE_CYAN, TEMPLE_GOLD, TIERS } from './sky-temple-parts';
import { leaf, moss, STONE, vine } from './stone-idol-stone';

// P09-R09, 3-3: the Sky Temple's dressing (phase 7 review: detail and some asymmetry; World 3
// theme: dark metal with neon, plus moss, vines and stone). Logical pixels, nose +Z, Y up.
type Vec3 = [number, number, number];

/** The thrusters' bank behind the pyramid: its centre along Z, and its nozzles across. */
const THRUSTERS = { z: -81, nozzles: [-22, 0, 22] } as const;

/**
 * The fortress under the stones: a bank of thrusters at the back, and armoured buttresses on
 * the sides with gold and cyan lights.
 */
export function templeMachinery(p: EnemyParts): void {
  const { hull, neon } = p;
  hull.box([66, 12, 14], H.base, { at: [0, -6, THRUSTERS.z] }, H.panel);
  neon.box([60, 0.6, 0.5], TEMPLE_CYAN, { at: [0, 4, THRUSTERS.z - 7.1] });
  for (const x of THRUSTERS.nozzles) {
    hull.cylinder(5.4, 3, 8, H.dark, { at: [x, 0, THRUSTERS.z - 7], pitch: -QUARTER });
    p.reactor([x, 0, THRUSTERS.z - 7.4], 4.5);
  }
  const base = TIERS.halves[0];
  for (const s of SIDES) {
    hull.box([6, 11, 44], H.base, { at: [s * (base + 2.4), -6, -6] }, H.panel);
    neon.box([0.5, 0.6, 38], TEMPLE_GOLD, { at: [s * (base + 5.5), 2, -6] });
    lamps(
      neon,
      [[s * (base + 2.4), 5, 18] as Vec3, [s * (base + 2.4), 5, -30] as Vec3],
      1.4,
      TEMPLE_CYAN,
    );
  }
}

/** Moss patches on the tiers' steps (x, z, which tier's top, size). */
const MOSS: readonly (readonly [number, number, number, number])[] = [
  [-48, 64, 1, 5],
  [62, 30, 1, 4],
  [-64, -20, 1, 4.5],
  [30, -62, 1, 5],
  [-49, -30, 2, 3.5],
  [48, 30, 2, 3],
  [-24, 40, 3, 3.2],
  [20, -30, 4, 3],
];
/** Vines draped over a tier's edge: from its top, down its side (x, z on the edge, tier). */
const DRAPED: readonly (readonly [number, number, number])[] = [
  [-30, 1, 0],
  [20, 1, 1],
  [-12, -1, 2],
  [30, 1, 3],
  [-50, -1, 0],
];

/** The jungle over the stones: moss on the steps, vines over the edges, shrubs on a tier. */
export function templeJungle({ hull }: EnemyParts): void {
  for (const [x, z, tier, size] of MOSS) moss(hull, [x, tier * TIERS.height, z], size, x);
  DRAPED.forEach(([along, side, tier], i) => {
    const half = TIERS.halves[tier] ?? 74;
    const top = (tier + 1) * TIERS.height;
    // `side`: ±1 an east / west edge (x = ±half, `along` z), 0 the back edge (z = -half).
    const at = (inset: number, y: number): Vec3 =>
      side === 0 ? [along, y, -half - inset] : [side * (half + inset), y, along];
    vine(hull, [at(-3, top), at(0.4, top - 0.2), at(0.8, top - 4), at(0.6, top - 9 - (i % 3) * 2)]);
  });
  // Roots hanging under the rock's rim.
  for (const [x, z] of [
    [40, 70],
    [-66, 30],
    [70, -50],
    [-20, -72],
  ] as const) {
    vine(
      hull,
      [
        [x, -2, z],
        [x * 0.96, -10, z * 0.96],
        [x * 0.9, -18, z * 0.9],
      ],
      1.4,
    );
  }
  // Shrubs grown on the second tier, to the left of the stair.
  for (const [x, z] of [
    [-38, 50],
    [-30, 52],
  ] as const) {
    hull.cylinder(3.2, 4.5, 5, STONE.leaf, { at: [x, 2 * TIERS.height, z] }, 0.8);
    leaf(hull, [x + 2, 2 * TIERS.height + 1, z - 2], 3.4, x);
  }
  leaf(hull, [10, SUMMIT, -30], 3, 1);
}
