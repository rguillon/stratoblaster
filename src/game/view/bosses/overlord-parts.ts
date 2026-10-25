import type { OutlinePoint } from '../../../render/geometry/outline';
import type { Placement } from '../../../render/geometry/solids';
import { ENEMY_LOOK } from '../../config/enemy-look';
import type { EnemyParts } from '../enemies/enemy-mesh';
import { around, decal, POD_SECTION, radial, sideStripe } from '../enemies/enemy-shapes';
import { box2d, OVERLORD_DECK, OVERLORD_NEON } from './overlord-city';

// P07-R05: the Overlord's destroyable parts (wing laser cannons, missile batteries, shield
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

/** P07-R05: a wing laser cannon: an armoured pod, a long barrel, coils and a lens charging. */
export function drawLaser({ hull, neon, charge }: EnemyParts, [x, y, z]: Vec3): void {
  const at: Vec3 = [x, y + WING_TOP - 1, z];
  hull.loft(POD_SECTION, LASER_POD, H.base, { at });
  for (const side of [1, 3]) {
    const stripe = sideStripe(POD_SECTION, side, [0.25, 0.55]);
    neon.loft(stripe, LASER_POD.slice(0, 3), OVERLORD_NEON, { at }, { open: true });
  }
  const axis = at[1] + 3;
  const along = (dz: number): Placement => ({ at: [x, axis, z + dz], pitch: QUARTER });
  const { from, length, radius } = LASER_BARREL;
  hull.cylinder(radius, length, 6, H.dark, along(from));
  // The coils and the lens brighten through the warning line, full while the beam fires.
  for (const dz of [from + 2.5, from + 6]) charge.ring(radius * 1.25, 1.3, 6, WHITE, along(dz));
  charge.lathe(LASER_LENS, 6, WHITE, along(from + length));
  // Heat sinks on the pod's back, a neon slit between them.
  for (const s of [-1, 1]) {
    hull.bevelSlab(
      box2d(2, 9, [x + s * 3.2, z - 4]),
      [at[1] + 7, at[1] + 7, at[1] + 9.5],
      [0, 0.6],
      H.panel,
    );
  }
  decal(neon, box2d(1.2, 8, [x, z - 4]), at[1] + 8.1, OVERLORD_NEON);
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

/** P07-R05: a missile battery on the deck: an armoured block, six hatches lit as it loads. */
export function drawBattery({ hull, neon, charge }: EnemyParts, [x, y, z]: Vec3): void {
  const base = y + OVERLORD_DECK.top;
  const top = base + 8;
  hull.bevelSlab(BATTERY, [base - 1, base, top], [0, 2], H.base, { at: [x, 0, z] }, H.panel);
  for (const [cx, cz] of CELLS) {
    decal(hull, box2d(7, 5.6, [x + cx, z + cz]), top + 0.04, H.dark);
    decal(charge, box2d(5, 3.6, [x + cx, z + cz]), top + 0.08, WHITE);
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

/** P07-R05: a shield generator: a neon dome in a dark coil, three emitter pylons around it. */
export function drawGenerator({ hull, neon }: EnemyParts, [x, y, z]: Vec3): void {
  const base = y + OVERLORD_DECK.top;
  hull.lathe(PEDESTAL, 8, H.panel, { at: [x, base, z], yaw: Math.PI / 8 });
  neon.ring(12.6, 0.8, 8, OVERLORD_NEON, { at: [x, base + 0.6, z], yaw: Math.PI / 8 });
  neon.lathe(DOME, 8, OVERLORD_NEON, { at: [x, base + 4, z] });
  hull.ring(9.2, 1.6, 8, H.dark, { at: [x, base + 5.2, z] });
  for (const a of around(3)) {
    const [px, , pz] = radial(a + Math.PI / 3, 10.5, 0);
    const pylon = box2d(2.6, 2.6, [x + px, z + pz]);
    hull.bevelSlab(pylon, [base + 4, base + 4, base + 15], [0, 0.6], H.dark, {}, H.panel);
    decal(neon, box2d(1.4, 1.4, [x + px, z + pz]), base + 15.05, OVERLORD_NEON);
  }
}
