import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import { mirror } from '../../../config/bosses/boss-kit';
import { VERDANT_SEEDS, VERDANT_THORN } from '../../../config/bosses/world-3/verdant-crown';
import { ENEMY_LOOK } from '../../../config/enemy-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, decal, POD_SECTION, radial } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';
import { DECK_TOP, EMERALD, JUNGLE, MAGENTA, strut } from './verdant-crown-garden';

// P09-R09, 3-5: the Verdant Crown's destroyable parts (thorn cannons, seed batteries, root
// generators), each drawn around its centre `at`, each turret around its pivot. Model space:
// logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

const H = ENEMY_LOOK.hull;
const WHITE: Rgb = [1, 1, 1];
const QUARTER = Math.PI / 2;

/** Height of the outriggers' top, where the thorn cannons turn. */
export const OUTRIGGER_TOP = 3;

/** A rectangle `w` wide and `d` long around (x, z). */
export function rect(w: number, d: number, [x, z]: OutlinePoint = [0, 0]): OutlinePoint[] {
  return [
    [x - w / 2, z - d / 2],
    [x + w / 2, z - d / 2],
    [x + w / 2, z + d / 2],
    [x - w / 2, z + d / 2],
  ];
}

/** A thorn cannon's pod (loft stations around its pivot), mossy on its back. */
const THORN_POD = [
  [-13, 5.5, 0, 7],
  [-4, 7.5, -0.5, 9],
  [9, 6.5, 0, 8.5],
  [15, 4, 2, 7],
] as const;
const POD_BACK = 2;
/** The lens at the front of its barrel (lathe profile, along the barrel). */
const LENS = [
  [0, 0],
  [3.2, 1],
  [2.2, 3],
  [0, 3.6],
] as const;
/** The thorns along its barrel: how far along from the pod, and how they are turned (roll). */
const THORNS = [
  [3, 0],
  [6, 1.1],
  [9, -1.1],
  [12, 0],
  [15, 1.1],
  [18, -1.1],
] as const;

/**
 * A thorn cannon (P09-R09), turning on its outrigger's turntable (D-073): a mossy pod crowned
 * with magenta spikes, a long barrel bristling with thorns, its lens glowing as the laser
 * charges.
 */
export function thornCannon(p: EnemyParts, [x, , z]: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const at: Vec3 = [x, OUTRIGGER_TOP, z];
  const paint = (side: number) => (side === POD_BACK ? JUNGLE.moss : undefined);
  hull.loft(POD_SECTION, THORN_POD, H.base, { at }, { paint });
  const [m] = x < 0 ? VERDANT_THORN : mirror(VERDANT_THORN);
  const tip = m ? bossPoint(...m) : at;
  const along = (dz: number): Placement => ({ at: [x, tip[1], dz], pitch: QUARTER });
  const lensAt = tip[2] - LENS[3][1];
  const start = z + 14;
  hull.cylinder(2.4, lensAt - start, 6, JUNGLE.bark, along(start), 1.9);
  for (const [dz, roll] of THORNS) {
    const [sx, sy] = [-Math.sin(roll) * 2, Math.cos(roll) * 2];
    hull.lathe(
      [
        [0.9, 0],
        [0, 3],
      ],
      3,
      H.panel,
      { at: [x + sx, tip[1] + sy, start + dz], roll },
    );
  }
  charge.lathe(LENS, 6, WHITE, along(lensAt));
  muzzle(tip, 'laser');
  for (const dx of [-3, 0, 3]) {
    neon.lathe(
      [
        [1, 0],
        [0, 4 + (dx === 0 ? 2 : 0)],
      ],
      4,
      MAGENTA,
      { at: [x + dx, OUTRIGGER_TOP + 8.6, z - 2] },
    );
  }
  neon.box([0.6, 0.8, 18], EMERALD, { at: [x + 7, OUTRIGGER_TOP + 3, z] });
  neon.box([0.6, 0.8, 18], EMERALD, { at: [x - 7, OUTRIGGER_TOP + 3, z] });
}

/** The turntable a thorn cannon turns on: a low drum on the outrigger, ringed with magenta. */
export function thornMount({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  hull.cylinder(10, OUTRIGGER_TOP, 8, H.dark, { at: [x, 0, z] });
  neon.ring(10.3, 0.6, 8, MAGENTA, { at: [x, OUTRIGGER_TOP - 0.4, z] });
}

/** A seed battery's pod seen from above (around its centre): a long, rounded seed. */
const SEED_POD: OutlinePoint[] = around(10).map((a): OutlinePoint => {
  const [px, , pz] = radial(a, 1, 0);
  return [px * 12, pz * 15.5];
});
const HATCH = [7, 5.6] as const;

/**
 * A seed battery (P09-R09): a mossy armoured seed pod on the deck, six hatches lit as its
 * missiles load, magenta strips down its sides, leaves sprouting at its ends.
 */
export function seedBattery({ hull, neon, charge, muzzle }: EnemyParts, [x, , z]: Vec3): void {
  const cells = (x < 0 ? VERDANT_SEEDS : mirror(VERDANT_SEEDS)).map((m) => bossPoint(...m));
  const height = cells[0]?.[1] ?? 0;
  const top = height - 0.08;
  const pod = SEED_POD.map(([px, pz]): OutlinePoint => [x + px, z + pz]);
  hull.bevelSlab(pod, [DECK_TOP - 1, DECK_TOP + 2, top], [0, 3], JUNGLE.moss, {}, H.base);
  for (const [cx, , cz] of cells) {
    decal(hull, rect(...HATCH, [cx, cz]), top + 0.04, H.dark);
    decal(charge, rect(HATCH[0] - 2, HATCH[1] - 2, [cx, cz]), height, WHITE);
    muzzle([cx, height, cz], 'missile');
  }
  for (const s of [-1, 1]) {
    neon.box([0.6, 1.2, 18], MAGENTA, { at: [x + s * 12.1, DECK_TOP + 1.6, z] });
    const leaf = { at: [x, top - 1, z + s * 14] as Vec3, pitch: s * 0.6 };
    hull.box([5, 0.6, 7], JUNGLE.leaf, leaf);
  }
}

/** The roots of a root generator: their turns around it (from the nose), and how far they reach. */
const ROOTS = [0.3, 1.5, 2.6, 3.7, 4.9] as const;
const ROOT_REACH = 12;

/**
 * A root generator (P09-R09; no weapon, it shields the core): a glowing magenta seed on a stone
 * pedestal, gnarled roots arching from it into the deck, an emerald ring round its foot.
 */
export function rootGenerator({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  hull.lathe(
    [
      [8, 0],
      [7, 3],
      [4.5, 5],
    ],
    6,
    JUNGLE.stone,
    { at: [x, DECK_TOP, z] },
  );
  neon.lathe(
    [
      [0, 0],
      [4.4, 2.4],
      [3.8, 6],
      [0, 8],
    ],
    6,
    MAGENTA,
    { at: [x, DECK_TOP + 5, z] },
  );
  ROOTS.forEach((a, i) => {
    const top: Vec3 = [x + Math.sin(a) * 3, DECK_TOP + 8 + (i % 2), z + Math.cos(a) * 3];
    const knee: Vec3 = [x + Math.sin(a) * 8, DECK_TOP + 6.5, z + Math.cos(a) * 8];
    const foot: Vec3 = [x + Math.sin(a) * ROOT_REACH, DECK_TOP, z + Math.cos(a) * ROOT_REACH];
    strut(hull, [top, knee], [1.7, 1.5], JUNGLE.bark, 5);
    strut(hull, [knee, foot], [1.5, 1.1], i % 2 === 0 ? JUNGLE.moss : JUNGLE.bark, 5);
  });
  neon.ring(ROOT_REACH + 0.6, 0.6, 10, EMERALD, { at: [x, DECK_TOP + 0.1, z] });
}
