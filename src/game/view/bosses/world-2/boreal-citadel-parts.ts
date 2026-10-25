import type { Placement } from '../../../../render/geometry/solids';
import { mirror } from '../../../config/bosses/boss-kit';
import { BOREAL_BATTERY, BOREAL_CANNON } from '../../../config/bosses/world-2/boreal-citadel';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, decal, POD_SECTION, radial } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';
import { AURORA, CITADEL_DECK, FROST, icicles, rect, VIOLET } from './boreal-citadel-city';

// P08-R10, 2-5: the Boreal Citadel's destroyable parts (aurora cannons, missile batteries, dome
// generators), each drawn around its centre `at` (model space: logical pixels, nose +Z, Y up).
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** Height of the outriggers' top, where the aurora cannons sit. */
export const OUTRIGGER_TOP = 3;

/** An aurora cannon's pod (loft stations around its centre), snowed over on its back. */
const CANNON_POD = [
  [-14, 6, 0, 7],
  [-4, 8, -0.5, 9],
  [12, 7, 0, 8],
  [21, 4.5, 1.5, 6],
] as const;
const POD_BACK = 2;
/** The lens at the front of its barrel (lathe profile, along the barrel). */
const LENS = [
  [0, 0],
  [3.4, 1],
  [2.4, 3],
  [0, 3.6],
] as const;
/** The aurora curtains on its back: thin lit fins, green below and violet along their tops. */
const CURTAINS = [-3.2, 0, 3.2] as const;

/**
 * P08-R10: an aurora cannon on an outrigger: a frosted pod, a long barrel with charge coils,
 * a lens where its laser leaves, and lit aurora curtains rippling along its back.
 */
export function drawCannon({ hull, neon, charge, muzzle }: EnemyParts, [x, , z]: Vec3): void {
  const at: Vec3 = [x, OUTRIGGER_TOP, z];
  hull.loft(
    POD_SECTION,
    CANNON_POD,
    H.base,
    { at },
    {
      paint: (side) => (side === POD_BACK ? FROST.snow : undefined),
    },
  );
  const [m] = BOREAL_CANNON;
  const tip = bossPoint(-x, m?.[1] ?? 0, m?.[2] ?? 0);
  const along = (dz: number): Placement => ({ at: [x, tip[1], dz], pitch: QUARTER });
  const lensAt = tip[2] - LENS[3][1];
  hull.cylinder(2.6, lensAt - (z + 20), 6, H.dark, along(z + 20));
  for (const dz of [z + 23, z + 27]) charge.ring(3.2, 1.3, 6, WHITE, along(dz));
  charge.lathe(LENS, 6, WHITE, along(lensAt));
  muzzle(tip, 'laser');
  CURTAINS.forEach((dx, i) => {
    const top = OUTRIGGER_TOP + 9 + (i % 2) * 1.5;
    const sway = (i - 1) * 0.12;
    neon.box([0.35, 3.2, 14 - i * 2], AURORA, { at: [x + dx, top, z - 2], yaw: sway });
    neon.box([0.45, 0.8, 14 - i * 2], VIOLET, { at: [x + dx, top + 3.2, z - 2], yaw: sway });
  });
  hull.box([12, 1.2, 5], H.panel, { at: [x, OUTRIGGER_TOP + 1, z - 13] }, FROST.snow);
  // Radiator fins on its flanks, snowed over.
  for (const s of [-1, 1]) {
    for (const dz of [-7, -3.5, 0, 3.5]) {
      hull.box(
        [2.6, 0.6, 2.2],
        H.panel,
        { at: [x + s * 8.6, OUTRIGGER_TOP + 4.5, z + dz] },
        FROST.snow,
      );
    }
  }
}

/** A missile battery's armoured block (around its centre), and the size of a cell's hatch. */
const BATTERY = rect(24, 26);
const HATCH = [7, 5.6] as const;

/**
 * P08-R10: a missile battery on the deck: a snowed-over armoured block, six hatches lit as its
 * missiles load, violet strips down its sides, icicles under its front.
 */
export function drawBattery({ hull, neon, charge, muzzle }: EnemyParts, [x, , z]: Vec3): void {
  const cells = (x < 0 ? BOREAL_BATTERY : mirror(BOREAL_BATTERY)).map((m) => bossPoint(...m));
  const height = cells[0]?.[1] ?? 0;
  const top = height - 0.08;
  const base = CITADEL_DECK.top;
  hull.bevelSlab(BATTERY, [base - 1, base, top], [0, 2], H.base, { at: [x, 0, z] }, FROST.snow);
  for (const [cx, , cz] of cells) {
    decal(hull, rect(...HATCH, [cx, cz]), top + 0.04, H.dark);
    decal(charge, rect(HATCH[0] - 2, HATCH[1] - 2, [cx, cz]), height, WHITE);
    muzzle([cx, height, cz], 'missile');
  }
  for (const s of [-1, 1]) {
    neon.box([0.6, 1.4, 20], VIOLET, { at: [x + s * 12.2, base + 3.4, z] });
  }
  neon.box([18, 1.2, 0.6], AURORA, { at: [x, base + 3.4, z + 13.2] });
  icicles(
    hull,
    [
      [x - 10, z + 13.4],
      [x + 10, z + 13.4],
    ],
    top,
    4,
  );
}

/** A dome generator's pedestal and heated glass dome (lathe profiles, bottom to top). */
const PEDESTAL = [
  [12, 0],
  [12.5, 2],
  [10.5, 4.5],
  [0, 4.5],
] as const;
const DOME = [
  [9, 0],
  [8, 3.8],
  [5, 6.6],
  [0, 7.6],
] as const;

/**
 * P08-R10: a dome generator (no weapon; it shields the core): a heated glass dome glowing
 * aurora green through its ring of ice, three pylons with violet lights.
 */
export function drawDome({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  const base = CITADEL_DECK.top;
  hull.lathe(PEDESTAL, 8, H.panel, { at: [x, base, z], yaw: Math.PI / 8 });
  hull.ring(12.6, 1, 8, FROST.snow, { at: [x, base + 1.2, z], yaw: Math.PI / 8 });
  neon.ring(12.7, 0.6, 8, VIOLET, { at: [x, base + 0.4, z], yaw: Math.PI / 8 });
  neon.lathe(DOME, 8, AURORA, { at: [x, base + 4.5, z] });
  hull.ring(9.4, 1, 8, FROST.ice, { at: [x, base + 4.4, z] });
  for (const a of around(3)) {
    const [px, , pz] = radial(a + Math.PI / 3, 11, 0);
    const pylon = rect(2.6, 2.6, [x + px, z + pz]);
    hull.bevelSlab(pylon, [base + 4, base + 4, base + 15], [0, 0.6], H.dark, {}, FROST.snow);
    decal(neon, rect(1.4, 1.4, [x + px, z + pz]), base + 15.05, VIOLET);
  }
}
