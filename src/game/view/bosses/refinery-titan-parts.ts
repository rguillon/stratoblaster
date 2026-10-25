import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement } from '../../../render/geometry/solids';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { decal, POD_SECTION } from '../enemies/enemy-shapes';

// P07-R05: the Refinery Titan's destroyable parts (fuel tanks, rotary turrets, missile battery),
// each drawn around its centre `at` (model space: logical pixels, nose +Z, Y up).
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;
/** Orange: the boss's neon (GD-61). */
export const TITAN_NEON = BOSS_LOOK.neon['refinery-titan'] ?? WHITE;

type Vec3 = [number, number, number];

/** Heights the parts stand on: the tank beam, the turret sponson, the hull's back. */
export const TITAN_DECK = { beam: 3, sponson: 8, back: 13 } as const;

/** A rectangle `w` wide and `d` long around (x, z). */
export function rect(w: number, d: number, [x, z]: OutlinePoint = [0, 0]): OutlinePoint[] {
  return [
    [x - w / 2, z - d / 2],
    [x + w / 2, z - d / 2],
    [x + w / 2, z + d / 2],
    [x - w / 2, z + d / 2],
  ];
}

/**
 * A fuel tank lying along Z (a lathe profile along its axis): a capsule of octagonal section,
 * a flat on top, ringed with glowing bands.
 */
const TANK_PROFILE = [
  [0, -22],
  [8, -21],
  [12.5, -17],
  [14, -10],
  [14, 10],
  [12.5, 17],
  [8, 21],
  [0, 22],
] as const;
const TANK_RADIUS = 14;
/** Where the bands sit along the tank, and the lit windows between them. */
const TANK_BANDS = [-13.2, -1.2, 10.8] as const;
const TANK_WINDOWS = [-6, 6] as const;

/** P07-R05: a big fuel tank cradled on the beam, orange bands and windows glowing on it. */
export function drawTank({ hull, neon }: EnemyParts, [x, y, z]: Vec3): void {
  const axis = y + TITAN_DECK.beam + 9;
  // Pitched, the lathe's axis runs along +Z; rolled by an eighth of a turn, a flat faces up.
  const along = (dz: number): Placement => ({
    at: [x, axis, z + dz],
    pitch: QUARTER,
    roll: Math.PI / 8,
  });
  hull.lathe(TANK_PROFILE, 8, H.panel, along(0));
  for (const dz of TANK_BANDS) neon.ring(TANK_RADIUS * 1.04, 2.4, 8, TITAN_NEON, along(dz));
  // The top flat of the octagon, a little above it: two lit windows and a valve.
  const top = axis + TANK_RADIUS * Math.cos(Math.PI / 8);
  for (const dz of TANK_WINDOWS) decal(neon, rect(3.2, 7, [x, z + dz]), top + 0.05, TITAN_NEON);
  hull.cylinder(2.6, 3.2, 6, H.dark, { at: [x, top - 1.2, z + 15] }, 1.8);
  hull.cylinder(2.6, 3.2, 6, H.dark, { at: [x, top - 1.2, z - 15] }, 1.8);
}

/** A rotary turret's base: a low faceted dome, its armoured barrel housing. */
const TURRET_BASE = [
  [12.5, 0],
  [13, 2.5],
  [10.5, 5.5],
  [6, 8],
  [0, 8.6],
] as const;
const TURRET_HOUSING = [
  [-5, 5, -3.2, 3.4],
  [4, 5.4, -3.6, 3.8],
  [11, 4.4, -3, 3.2],
] as const;
/** The barrels around the rotary axis (x, y), their length and radius. */
const BARRELS = [
  [0, 1.8],
  [-2.2, -1.2],
  [2.2, -1.2],
] as const;
const BARREL = { length: 10, radius: 1.3 } as const;

/** P07-R05: a rotary turret on the front sponson, three barrels with charge-lit muzzles. */
export function drawTurret(
  { hull, neon, charge, muzzle: mark }: EnemyParts,
  [x, y, z]: Vec3,
): void {
  const base = y + TITAN_DECK.sponson;
  hull.lathe(TURRET_BASE, 8, H.base, { at: [x, base, z] });
  neon.ring(13.3, 0.9, 8, TITAN_NEON, { at: [x, base + 1, z] });
  const axis = base + 9;
  hull.loft(POD_SECTION, TURRET_HOUSING, H.panel, { at: [x, axis, z] });
  const front = z + TURRET_HOUSING[2][0];
  // The barrel shroud, then the barrels; their muzzles light up as the spiral charges.
  hull.cylinder(4.6, 1.6, 6, H.dark, { at: [x, axis, front], pitch: QUARTER });
  for (const [bx, by] of BARRELS) {
    const muzzle: Placement = { at: [x + bx, axis + by, front], pitch: QUARTER };
    hull.cylinder(BARREL.radius, BARREL.length, 6, H.dark, muzzle);
    const tip: Vec3 = [x + bx, axis + by, front + BARREL.length];
    charge.cylinder(BARREL.radius * 1.25, 1.6, 6, WHITE, { at: tip, pitch: QUARTER });
    mark([tip[0], tip[1], tip[2] + 1.6]);
  }
  // A neon sight slit along the housing's top.
  decal(neon, rect(1.4, 8, [x, z + 2]), axis + 3.9, TITAN_NEON);
}

/** The missile battery's cells: 2 columns by 3 rows on its top. */
const CELLS = [-5.5, 5.5].flatMap((cx) => [-7.5, 0, 7.5].map((cz) => [cx, cz] as const));

/** P07-R05: an armoured missile battery on the hull's back, six hatches lit as it loads. */
export function drawMissileBattery(
  { hull, neon, charge, muzzle }: EnemyParts,
  [x, y, z]: Vec3,
): void {
  const base = y + TITAN_DECK.back;
  const top = base + 8;
  const block: OutlinePoint[] = [
    [-11, -13],
    [11, -13],
    [13.5, -9],
    [13.5, 10],
    [9, 13.5],
    [-9, 13.5],
    [-13.5, 10],
    [-13.5, -9],
  ];
  hull.bevelSlab(block, [base - 2, base, top], [0, 2], H.base, { at: [x, 0, z] }, H.panel);
  for (const [cx, cz] of CELLS) {
    decal(hull, rect(7.4, 5.6, [x + cx, z + cz]), top + 0.04, H.dark);
    decal(charge, rect(5.4, 3.6, [x + cx, z + cz]), top + 0.08, WHITE);
    muzzle([x + cx, top + 0.08, z + cz], 'missile');
  }
  // Neon strips down both flanks of the block.
  for (const s of [-1, 1]) {
    neon.box([0.6, 1.4, 16], TITAN_NEON, { at: [x + s * 12.6, base + 3.2, z] });
  }
}
