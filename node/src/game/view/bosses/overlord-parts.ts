import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { ROUND_SECTION } from '../../../render/geometry/organic';
import { around, decal, radial, sideStripe } from '../enemies/enemy-shapes';
import { F, graft, polygon, tentacle, veinLine } from './world-1-organic-kit';
import { box2d, OVERLORD_DECK, OVERLORD_NEON } from './overlord-city';

// P07-R05, P16-R06: the Overlord's destroyable parts (wing laser cannons, missile batteries, shield
// generators), each drawn around its centre `at` (model space: logical pixels, nose +Z, Y up).
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** Height of the wings' top, where the laser cannons sit. */
export const WING_TOP = 2;

/** A laser cannon's pod (loft stations around its centre), its barrel and its lens. */
const LASER_POD = [
  [-15, 5, -2, 5],
  [-6, 8, -3, 8],
  [8, 7, -2.5, 7],
  [15, 4, -1, 4.5],
] as const;
const LASER_BARREL = { from: 15, length: 10, radius: 2.4 } as const;
const LASER_LENS = [
  [0, 0],
  [3.2, 1],
  [2.2, 3],
  [0, 3.6],
] as const;

/**
 * P07-R05, P16-R06: a wing laser cannon: a swollen gland on the wing, a grafted collar, a long
 * barrel, coils and a lens charging.
 */
export function drawLaser(p: EnemyParts, [x, y, z]: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const at: Vec3 = [x, y + WING_TOP - 1, z];
  p.flesh.loft(ROUND_SECTION, LASER_POD, F.crimson, { at });
  graft(p, polygon(6, 4, [1.2, 1.4]), [at[1] + 6.6, at[1] + 7.6], [x, 0, z + 8]);
  for (const side of [1, 3]) {
    const stripe = sideStripe(ROUND_SECTION, side, [0.25, 0.55]);
    neon.loft(stripe, LASER_POD.slice(0, 3), OVERLORD_NEON, { at }, { open: true });
  }
  const axis = at[1] + 3;
  const along = (dz: number): Placement => ({ at: [x, axis, z + dz], pitch: QUARTER });
  const { from, length, radius } = LASER_BARREL;
  hull.cylinder(radius, length, 6, H.dark, along(from));
  // The coils and the lens brighten through the warning line, full while the beam fires.
  for (const dz of [from + 2.5, from + 6]) charge.ring(radius * 1.25, 1.3, 6, WHITE, along(dz));
  charge.lathe(LASER_LENS, 6, WHITE, along(from + length));
  muzzle([x, axis, z + from + length + 3.6], 'laser');
  // Bone fins on the gland's back, a vein between them.
  for (const s of [-1, 1]) {
    tentacle(
      p,
      [x + s * 3.2, at[1] + 7, z - 10],
      [x + s * 4, at[1] + 10, z - 2],
      [0, 1, 0],
      [1.2, 0.2],
      F.bone,
      3,
    );
  }
  veinLine(p, [x, at[1] + 8, z - 12], [x, at[1] + 8, z + 2], [0, 0.6, 0], 1.2, OVERLORD_NEON);
}

/** A missile battery's block, and its cells: 2 columns by 3 rows on its top. */
const BATTERY: OutlinePoint[] = [
  [-10, -13],
  [10, -13],
  [12.5, -9],
  [12.5, 10],
  [8.5, 13.5],
  [-8.5, 13.5],
  [-12.5, 10],
  [-12.5, -9],
];
const CELLS = [-5, 5].flatMap((cx) => [-7.5, 0, 7.5].map((cz) => [cx, cz] as const));

/**
 * P07-R05, P16-R06: a missile brood on the mantle: a swollen mound under a grafted plate, six
 * hatches lit as it loads.
 */
export function drawBattery(p: EnemyParts, [x, y, z]: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const base = y + OVERLORD_DECK.top;
  const top = base + 8;
  p.flesh.bevelSlab(
    BATTERY,
    [base - 1, base, top - 1],
    [0, 3],
    F.crimson,
    { at: [x, 0, z] },
    F.sinew,
  );
  hull.bevelSlab(BATTERY, [top - 1.2, top - 1.2, top], [0, 1], H.base, { at: [x, 0, z] }, H.panel);
  veinLine(p, [x, base, z - 13], [x, base - 2, z - 22], [0, 1.5, 0], 1.1, OVERLORD_NEON);
  for (const [cx, cz] of CELLS) {
    decal(hull, box2d(7, 5.6, [x + cx, z + cz]), top + 0.04, H.dark);
    decal(charge, box2d(5, 3.6, [x + cx, z + cz]), top + 0.08, WHITE);
    muzzle([x + cx, top + 0.08, z + cz], 'missile');
  }
  for (const s of [-1, 1]) {
    neon.box([0.6, 1.4, 16], OVERLORD_NEON, { at: [x + s * 11.7, base + 3.2, z] });
  }
}

/** A shield generator's pedestal and glowing dome (lathe profiles, bottom to top). */
const PEDESTAL = [
  [12, 0],
  [12.5, 2],
  [10.5, 4.5],
  [0, 4.5],
] as const;
const DOME = [
  [8.5, 0],
  [7.5, 3.5],
  [4.5, 6],
  [0, 7],
] as const;

/**
 * P07-R05, P16-R06: a shield generator: a glowing neon gland in a ring of grafted coil, swelling
 * out of a flesh mound, three bone horns around it tipped with neon.
 */
export function drawGenerator(p: EnemyParts, [x, y, z]: Vec3): void {
  const { hull, neon } = p;
  const base = y + OVERLORD_DECK.top;
  p.flesh.lathe(PEDESTAL, 8, F.purple, { at: [x, base, z], yaw: Math.PI / 8 });
  neon.ring(12.6, 0.8, 8, OVERLORD_NEON, { at: [x, base + 0.6, z], yaw: Math.PI / 8 });
  neon.lathe(DOME, 8, OVERLORD_NEON, { at: [x, base + 4, z] });
  hull.ring(9.2, 1.6, 8, H.dark, { at: [x, base + 5.2, z] });
  for (const a of around(3)) {
    const [px, , pz] = radial(a + Math.PI / 3, 10.5, 0);
    const horn: Vec3 = [x + px * 1.1, base + 15, z + pz * 1.1];
    tentacle(p, [x + px, base + 3, z + pz], horn, [0, 0, 0], [1.6, 0.4], F.bone, 4);
    neon.box([1, 1, 1], OVERLORD_NEON, { at: horn });
  }
}
