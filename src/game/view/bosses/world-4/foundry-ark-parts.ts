import type { Placement } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { ARK_CELLS, ARK_RAIL } from '../../../config/bosses/world-4/foundry-ark';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { decal, SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { rod } from '../final-boss-greebles';
import { lamps, seam } from '../mini-boss-greebles';
import { H, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { box2d } from '../overlord-city';

// P10-R11, 4-4: the Foundry Ark's destroyable parts (rail cannons, chimney row, missile battery,
// crucibles), each drawn around its centre `at`, each turret around its pivot, and its forge
// colours. Model space: logical pixels, nose +Z, Y up.
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Ark's orange neon, its molten metal (hotter, yellower), and its red warning lamps. */
export const ARK_ORANGE: Rgb = BOSS_LOOK.neon['foundry-ark'] ?? [1, 0.55, 0.12];
export const MOLTEN: Rgb = [1, 0.78, 0.25];
export const ARK_RED: Rgb = [1, 0.12, 0.05];
/** Soot-blackened iron, and rust on the old plates (World 4: heavy industry). */
export const SOOT: Rgb = SHADE.soot;
export const RUST: Rgb = [0.18, 0.08, 0.04];
/** Height of the deck, and of the outriggers' top, where the rail cannons turn. */
export const DECK_TOP = 4;

/** The turntable a rail cannon turns on: a low drum on its outrigger, ringed with orange. */
export function railMount({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  hull.cylinder(11, DECK_TOP + 1, 8, H.dark, { at: [x, 0, z], yaw: Math.PI / 8 });
  neon.ring(11.3, 0.6, 8, ARK_ORANGE, { at: [x, DECK_TOP - 0.2, z], yaw: Math.PI / 8 });
}

/** The coils wound round the rails, where the charge builds before a shot (along the rails). */
const COILS = [22, 30, 38] as const;

/**
 * A rail cannon (P10-R11), turning on its outrigger's turntable (D-073): an armoured breech, two
 * long rails out to the emitter between their tips, glowing coils along them, the emitter lit as
 * the laser charges.
 */
export function railCannon(p: EnemyParts, [x, , z]: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const [m] = x < 0 ? ARK_RAIL : mirror(ARK_RAIL);
  if (!m) return;
  const tip = bossPoint(...m);
  const y = tip[1];
  hull.box([15, 6.4, 17], H.base, { at: [x, DECK_TOP + 1, z] }, H.panel);
  hull.box([9, 2.6, 6], SOOT, { at: [x, DECK_TOP + 7.4, z - 4] });
  for (const s of SIDES) {
    const rail: Placement = { at: [x + s * 3.6, y - 1.2, (z + tip[2]) / 2 + 2] };
    hull.box([2, 2.4, tip[2] - z - 4], H.dark, rail, SHADE.edge);
    neon.box([0.4, 0.5, tip[2] - z - 12], ARK_ORANGE, { at: [x + s * 4.7, y, z + 18] });
  }
  for (const dz of COILS) {
    charge.box([9.6, 1, 1.6], WHITE, { at: [x, y - 2, z + dz] });
  }
  hull.cylinder(2, 2.4, 6, H.dark, { at: [x, y, tip[2] - 3.2], pitch: QUARTER });
  charge.cylinder(1.6, 0.8, 6, WHITE, { at: [x, y, tip[2] - 0.8], pitch: QUARTER }, 1);
  muzzle(tip, 'laser');
}

/** The chimneys of the row, across the foredeck (x), and their height. */
const CHIMNEYS = [-15, -5, 5, 15] as const;
const CHIMNEY_TOP = 32;

/**
 * The chimney row (P10-R11; no weapon, it shields the core): four tall stacks on a brick-dark
 * plinth, sooty at the top with a heat glow under their lips, a red lamp on each.
 */
export function chimneyRow({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  hull.bevelSlab(box2d(46, 15, [x, z]), [DECK_TOP - 1, DECK_TOP, 10], [0, 1.2], H.base, {}, RUST);
  CHIMNEYS.forEach((dx, i) => {
    const top = CHIMNEY_TOP - (i % 2) * 3;
    const at: Vec3 = [x + dx, 10, z];
    hull.cylinder(4, top - 10, 6, H.panel, { at }, 3.2);
    hull.ring(3.5, 2.4, 6, SOOT, { at: [x + dx, top - 0.4, z] });
    neon.ring(3.45, 0.7, 6, ARK_ORANGE, { at: [x + dx, top - 3.6, z] });
    hull.ring(4.1, 0.8, 6, H.dark, { at: [x + dx, 14 + i, z] });
    lamps(neon, [[x + dx + 3.6, top - 6, z]], 0.9, ARK_RED);
  });
  seam(hull, [x - 22, z + 6.6], [x + 22, z + 6.6], [10, 1.6, 0.8], H.dark);
}

/** The missile hatches' size on the battery's top. */
const HATCH = [8, 7] as const;

/**
 * The missile battery on the bow (P10-R11): an armoured block, four hatches lit as missiles load,
 * hazard-orange strips down its sides.
 */
export function battery({ hull, neon, charge, muzzle }: EnemyParts, [x, , z]: Vec3): void {
  const cells = ARK_CELLS.map((m) => bossPoint(...m));
  const height = cells[0]?.[1] ?? 9;
  const top = height - 0.08;
  hull.bevelSlab(box2d(24, 24, [x, z]), [DECK_TOP - 1, DECK_TOP, top], [0, 2], H.base, {}, H.panel);
  for (const [cx, , cz] of cells) {
    decal(hull, box2d(...HATCH, [cx, cz]), top + 0.04, H.dark);
    decal(charge, box2d(HATCH[0] - 2.4, HATCH[1] - 2.4, [cx, cz]), height, WHITE);
    muzzle([cx, height, cz], 'missile');
  }
  for (const s of SIDES) neon.box([0.6, 1.2, 18], ARK_ORANGE, { at: [x + s * 12.2, 5, z] });
  hull.box([18, 1, 2], SOOT, { at: [x, top - 0.4, z - 11] });
}

/** A crucible's bucket (a lathe profile around its axis, up). */
const BUCKET = [
  [7.5, 0],
  [10.5, 3],
  [12, 11],
  [12.6, 13],
] as const;
const BUCKET_FOOT = DECK_TOP + 2;

/**
 * A crucible (P10-R11): a heavy bucket brimming with glowing molten metal, hung from a gantry
 * on chains, a pouring lip on its inboard side, a hot band round its belly. Destroyed, it spills
 * into a ring of bullets.
 */
export function crucible({ hull, neon }: EnemyParts, [x, , z]: Vec3): void {
  const inboard = -Math.sign(x);
  hull.lathe(BUCKET, 8, SOOT, { at: [x, BUCKET_FOOT, z] }, false);
  neon.ring(11.7, 0.8, 8, ARK_ORANGE, { at: [x, BUCKET_FOOT + 7, z] });
  neon.cylinder(11.9, 0.3, 8, MOLTEN, { at: [x, BUCKET_FOOT + 11.4, z] });
  hull.box([5, 1.2, 5], H.dark, { at: [x + inboard * 12.5, BUCKET_FOOT + 11.6, z] });
  neon.box([3, 0.4, 3], MOLTEN, { at: [x + inboard * 13, BUCKET_FOOT + 12.8, z] });
  // The gantry: two legs either side of the bucket (along Z), a beam over it, chains to the rim.
  for (const s of SIDES) {
    hull.box([2.4, 26, 2.4], H.panel, { at: [x, DECK_TOP, z + s * 15] }, SHADE.edge);
    rod(hull, [x + 4, DECK_TOP + 28, z + s * 4], [x + 9, BUCKET_FOOT + 13, z + s * 7], 0.4);
    rod(hull, [x - 4, DECK_TOP + 28, z + s * 4], [x - 9, BUCKET_FOOT + 13, z + s * 7], 0.4);
  }
  hull.box([3, 2.4, 33], H.base, { at: [x, DECK_TOP + 26, z] }, H.panel);
  hull.box([9, 2, 4], H.dark, { at: [x, DECK_TOP + 27, z] });
  lamps(neon, [[x, DECK_TOP + 28.6, z + 15]], 0.9, ARK_RED);
}
