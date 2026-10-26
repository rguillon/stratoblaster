import type { OutlinePoint } from '../../../../render/geometry/outline';
import type { Placement } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { CALDERA_CELLS, CALDERA_MAGMA } from '../../../config/bosses/world-4/caldera-throne';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { around, decal, POD_SECTION } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-limbs';
import { rect } from '../final-boss-greebles';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';

// P10-R11, 4-5: the Caldera Throne's colours and its destroyable parts (magma cannons, missile
// batteries, heat shield generators), each drawn around its centre `at`, each turret around its
// pivot. Model space: logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** Crimson, its registered neon (GD-61), and gold, its second neon colour (P10-R11). */
export const CRIMSON: Rgb = BOSS_LOOK.neon['caldera-throne'] ?? WHITE;
export const GOLD: Rgb = [1, 0.72, 0.16];
/** World 4 heat over the dark metal (P10-R11): molten seams and glow, soot, heat-blued plates. */
export const HEAT = {
  molten: [1, 0.36, 0.04] as Rgb,
  glow: [0.75, 0.16, 0.03] as Rgb,
  soot: SHADE.soot,
  blued: [0.09, 0.08, 0.12] as Rgb,
};

/** Height of the deck's top, which the keep and the parts stand on, and the bastions' top. */
export const DECK_TOP = 8;
export const BASTION_TOP = 5;

/** A magma cannon's housing (loft stations around its pivot), soot-black on its back. */
const HOUSING = [
  [-14, 7, 0, 8],
  [-4, 9, -0.5, 10],
  [10, 8, 0, 9.5],
  [17, 5, 2, 8],
] as const;
const HOUSING_BACK = 2;
/** The lens at the front of its barrel (lathe profile, along the barrel). */
const LENS = [
  [0, 0],
  [3.6, 1],
  [2.6, 3],
  [0, 3.8],
] as const;
/** How far along the barrel (from the housing) its glowing cooling coils stand. */
const COILS = [3, 7, 11, 15] as const;

/**
 * A magma cannon (P10-R11), turning on its bastion's turntable (D-073): a heavy housing with
 * gold neon flanks, a long barrel ringed with molten coils, its lens glowing as the laser charges.
 */
export function magmaCannon(p: EnemyParts, [x, , z]: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const at: Vec3 = [x, BASTION_TOP, z];
  const paint = (side: number) => (side === HOUSING_BACK ? HEAT.soot : undefined);
  hull.loft(POD_SECTION, HOUSING, H.base, { at }, { paint });
  const [m] = x < 0 ? CALDERA_MAGMA : mirror(CALDERA_MAGMA);
  const tip = m ? bossPoint(...m) : at;
  const along = (dz: number): Placement => ({ at: [x, tip[1], dz], pitch: QUARTER });
  const lensAt = tip[2] - LENS[3][1];
  const start = z + 16;
  hull.cylinder(3, lensAt - start, 8, H.dark, along(start), 2.4);
  for (const dz of COILS) neon.ring(3.2 - dz * 0.03, 1.2, 8, HEAT.molten, along(start + dz));
  hull.cylinder(4.2, 3, 8, SHADE.edge, along(lensAt - 3));
  charge.lathe(LENS, 8, WHITE, along(lensAt));
  muzzle(tip, 'laser');
  for (const s of [-1, 1]) {
    neon.box([0.6, 1, 20], GOLD, { at: [x + s * 9.6, BASTION_TOP + 3, z] });
    hull.box([3, 3, 9], H.panel, { at: [x + s * 5, BASTION_TOP + 9, z - 6] }, HEAT.soot);
  }
  neon.box([5, 0.6, 0.6], CRIMSON, { at: [x, BASTION_TOP + 10.2, z + 9] });
}

/** The turntable a magma cannon turns on: a low drum on the bastion, ringed with crimson. */
export function magmaMount({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  hull.cylinder(12, BASTION_TOP, 8, H.dark, { at: [x, 0, z] });
  neon.ring(12.3, 0.7, 8, CRIMSON, { at: [x, BASTION_TOP - 0.5, z] });
  neon.ring(12.3, 0.5, 8, HEAT.glow, { at: [x, 0.6, z] });
}

/** A battery's armoured box seen from above (around its centre), its corners cut. */
const BATTERY: OutlinePoint[] = [
  [-10, -15],
  [10, -15],
  [13, -11],
  [13, 11],
  [10, 15],
  [-10, 15],
  [-13, 11],
  [-13, -11],
];
const HATCH = [7.6, 6.4] as const;

/**
 * A missile battery (P10-R11): an armoured box on the aft deck, six hatches lit as its missiles
 * load, crimson strips down its sides, a heat-blued blast shield at its front.
 */
export function missileBattery({ hull, neon, charge, muzzle }: EnemyParts, [x, , z]: Vec3): void {
  const cells = (x < 0 ? CALDERA_CELLS : mirror(CALDERA_CELLS)).map((m) => bossPoint(...m));
  const height = cells[0]?.[1] ?? 0;
  const top = height - 0.08;
  const box = BATTERY.map(([px, pz]): OutlinePoint => [x + px, z + pz]);
  hull.bevelSlab(box, [DECK_TOP - 1, DECK_TOP + 2, top], [0, 2], H.base, {}, HEAT.blued);
  for (const [cx, , cz] of cells) {
    decal(hull, rect([cx, cz], HATCH), top + 0.04, H.dark);
    decal(charge, rect([cx, cz], [HATCH[0] - 2.4, HATCH[1] - 2.4]), height, WHITE);
    muzzle([cx, height, cz], 'missile');
  }
  for (const s of [-1, 1]) {
    neon.box([0.6, 1.4, 20], CRIMSON, { at: [x + s * 13.3, DECK_TOP + 2.4, z] });
  }
  hull.box([22, 5, 2], H.panel, { at: [x, top - 1, z + 16], pitch: -0.3 }, HEAT.blued);
  neon.box([16, 0.6, 0.6], GOLD, { at: [x, top + 2.4, z + 16.6] });
}

/** A generator's heat sinks: how many fins round it, and their size. */
const FINS = { count: 8, reach: 12, height: 11, thick: 1.2 } as const;
/** The glowing core of a generator (lathe profile), and its dome. */
const CORE = [
  [0, 0],
  [4.4, 2],
  [4.8, 6],
  [3.4, 10],
  [0, 12],
] as const;

/**
 * A heat shield generator (P10-R11; no weapon, it shields the core): a molten core glowing in a
 * crown of heat-sink fins edged with gold, on an armoured drum ringed with crimson.
 */
export function shieldGenerator({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  const base = DECK_TOP;
  hull.cylinder(13, 4, 8, H.dark, { at: [x, base - 1, z], yaw: Math.PI / 8 }, 12);
  neon.ring(12.4, 0.7, 8, CRIMSON, { at: [x, base + 2.8, z], yaw: Math.PI / 8 });
  neon.lathe(CORE, 6, HEAT.molten, { at: [x, base + 3, z] });
  for (const a of around(FINS.count)) {
    const [c, s] = [Math.cos(a), Math.sin(a)];
    const mid: Vec3 = [x + s * FINS.reach * 0.62, base + 3, z + c * FINS.reach * 0.62];
    hull.box([FINS.thick, FINS.height, FINS.reach * 0.7], H.panel, { at: mid, yaw: a }, H.dark);
    const edge: Vec3 = [x + s * FINS.reach * 0.96, base + 3, z + c * FINS.reach * 0.96];
    neon.box([FINS.thick * 1.1, FINS.height * 0.8, 0.5], GOLD, { at: edge, yaw: a });
  }
  neon.ring(7.4, 0.6, 8, GOLD, { at: [x, base + 3 + FINS.height, z] });
}
