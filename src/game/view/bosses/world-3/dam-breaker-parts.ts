import type { SolidBuilder } from '../../../../render/geometry/solids';
import { BOSS_LOOK } from '../../../config/boss-look';
import { mirror } from '../../../config/bosses/boss-kit';
import { DAM_SPOUT } from '../../../config/bosses/world-3/dam-breaker';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { rod } from '../final-boss-greebles';
import { cog } from '../mini-boss-mechanism';
import { hazard, lamps, rect, vent } from '../mini-boss-greebles';
import { H, offset, QUARTER, SHADE, WHITE } from '../mini-boss-shapes';
import { F, gland, veinTo } from './jungle-flesh';

// P09-R09, 3-4: the Dam Breaker's parts (sluice cannons, chemical tanks, armour plate, drone
// hangar) and its swamp growth. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Dam Breaker's toxic green neon. */
export const TOXIC: Rgb = BOSS_LOOK.neon['dam-breaker'] ?? [0.6, 1, 0.1];
/** Swamp moss on its ledges, the vines hanging over its sides, and rust (World 3 growth). */
export const MOSS: Rgb = [0.13, 0.2, 0.07];
export const VINE: Rgb = [0.08, 0.14, 0.05];
export const RUST: Rgb = [0.2, 0.1, 0.05];
/** Height of the barge's deck. */
export const DECK_Y = 4;

/** Moss cushions at each point (`[x, y, z]`). */
export function moss(hull: SolidBuilder, points: readonly Vec3[], size = 3): void {
  points.forEach((at, i) => {
    const r = size * (0.75 + (i % 3) * 0.2);
    hull.cylinder(r, r * 0.45, 5, MOSS, { at, yaw: i * 0.9 }, r * 0.4);
  });
}

/** Vines hanging over an edge from each point (`[x, y, z]`), drooping by `drop`. */
export function vines(hull: SolidBuilder, points: readonly Vec3[], drop = 7): void {
  points.forEach(([x, y, z], i) => {
    const out = Math.sign(x) * 1.5;
    const low: Vec3 = [x + out, y - drop * (0.7 + (i % 2) * 0.4), z + (i % 3) - 1];
    rod(hull, [x, y, z], low, 0.45, VINE);
  });
}

/**
 * A sluice cannon around its centre `at` (P09-R09): a gate house on the deck, its sluice gate
 * raised over a chute whose lip lets out the sludge, a hand wheel on top, a green glow inside.
 */
export function sluice(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  // The left sluice (screen left) is on the model's +X side.
  const spouts = at[0] > 0 ? DAM_SPOUT : mirror(DAM_SPOUT);
  const [lip] = spouts.map((m) => bossPoint(...m));
  if (!lip) return;
  // P16-R06: a gland swelling out of the beast's back, a metal sluice gate grafted in its mouth.
  p.flesh.box([22, 12, 14], F.crimson, { at: offset(at, 0, DECK_Y, -2) }, F.sinew);
  gland(p, offset(at, 0, DECK_Y + 12, -5), 3, TOXIC);
  // The gate, raised in its frame, and the dark culvert under it.
  hull.box([16, 6, 1.6], SHADE.edge, { at: offset(at, 0, DECK_Y + 8, 5.6) });
  hull.box([15, 6, 0.6], H.dark, { at: offset(at, 0, DECK_Y + 0.5, 5.4) });
  for (const s of SIDES) {
    hull.box([2, 16, 2.4], H.panel, { at: offset(at, s * 9, DECK_Y, 5.4) });
    neon.box([0.6, 14, 0.5], TOXIC, { at: offset(at, s * 7.7, DECK_Y + 1, 6.7) });
  }
  // The chute out to its lip.
  hull.box([14, 1.2, 11], H.panel, { at: [lip[0], lip[1] - 1.6, lip[2] - 5.5], pitch: -0.12 });
  charge.box([11, 0.4, 9], WHITE, { at: [lip[0], lip[1] - 1, lip[2] - 5.5], pitch: -0.12 });
  neon.box([14, 0.6, 0.6], TOXIC, { at: [lip[0], lip[1] - 0.6, lip[2] - 0.3] });
  muzzle(lip);
  cog(hull, offset(at, 0, DECK_Y + 14.4, -3), 4.2, 8);
  hull.cylinder(0.8, 2.4, 4, H.dark, { at: offset(at, 0, DECK_Y + 12, -3) });
  moss(hull, [offset(at, 7, DECK_Y + 12, -7), offset(at, -8, DECK_Y + 12, -6)], 2.2);
}

/** A chemical tank's body: a capsule lying along Z (a lathe profile, its axis along +Y). */
const TANK = [
  [0, -17],
  [7, -16],
  [11, -13],
  [12, -9],
  [12, 9],
  [11, 13],
  [7, 16],
  [0, 17],
] as const;

/**
 * A chemical tank around its centre `at` (P09-R09): a fat capsule on cradles at the barge's
 * side, glowing green through bands of glass, hooped with rusty straps, vines hanging off it.
 */
export function tank(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  const s = Math.sign(at[0]);
  const axis = offset(at, 0, 12, 0);
  // P16-R06: a bloated toxin bladder of teal flesh, hooped by rusty grafted straps.
  p.flesh.lathe(TANK, 7, F.teal, { at: axis, pitch: QUARTER, yaw: Math.PI / 8 });
  for (const dz of [-9, 0, 9]) {
    neon.ring(12.2, 3, 8, TOXIC, { at: offset(axis, 0, 0, dz - 1.5), pitch: QUARTER });
  }
  for (const dz of [-13, -4.5, 4.5, 13]) {
    hull.ring(12.4, 1.6, 8, RUST, { at: offset(axis, 0, 0, dz - 0.8), pitch: QUARTER });
  }
  // The cradles and the outrigger beams back to the hull.
  for (const dz of [-8, 8]) {
    hull.box([18, 4, 3], H.dark, { at: offset(at, 0, 0, dz) });
    hull.box([16, 3, 3], H.panel, { at: offset(at, -s * 16, 1, dz) }, SHADE.edge);
  }
  hull.box([5, 3, 4], H.panel, { at: offset(axis, 0, 11, 14) });
  lamps(neon, [offset(axis, 0, 14.4, 14)], 1.3, TOXIC);
  vines(hull, [offset(at, s * 9, 18, -6), offset(at, s * 10, 16, 5), offset(at, s * 8, 19, 12)]);
  moss(hull, [offset(axis, -s * 3, 11.6, -6)], 2.4);
}

/** The armour plate seen from above: a wide, chamfered slab over the bow (around its centre). */
const PLATE = [
  [-22, -6],
  [-18, 9],
  [18, 9],
  [22, -6],
  [14, -12],
  [-14, -12],
] as const;

/**
 * The armour plate around its centre `at` (P09-R09): a thick, sloped slab bolted over the bow,
 * no weapon, hazard stripes along its front edge, green slits, moss in its seams.
 */
export function plate({ hull, neon }: EnemyParts, at: Vec3): void {
  const top = DECK_Y + 9;
  hull.bevelSlab(PLATE, [DECK_Y, top - 3, top], [0, 2.4], H.base, { at }, SHADE.edge);
  hazard(hull, offset(at, 0, top, -7.5), [24, 3], 8, 0);
  for (const s of SIDES) {
    neon.box([0.8, 0.4, 9], TOXIC, { at: offset(at, s * 12, top + 0.05, 1.5), yaw: s * 0.25 });
    for (const dz of [-4, 4])
      hull.cylinder(0.9, 0.6, 5, SHADE.edge, { at: offset(at, s * 17, top - 1.4, dz) });
  }
  hull.box([10, 1, 6], H.panel, { at: offset(at, 0, top, 3) }, SHADE.edge);
  moss(hull, [offset(at, -15, top - 1.5, 6), offset(at, 9, top, -2)], 2);
}

/**
 * The drone hangar around its centre `at` (P09-R09): a bay at the bow, its open door framed in
 * green, where its Hornets leave from.
 */
export function hangar(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  // P16-R06: a brood pouch of flesh on the bow, its drone hatch a grafted metal door.
  p.flesh.bevelSlab(
    rect(26, 20),
    [DECK_Y - 4, DECK_Y, DECK_Y + 7],
    [1, 1.5],
    F.purple,
    { at },
    F.crimson,
  );
  veinTo(
    p,
    [offset(at, -11, DECK_Y + 7.2, -8), offset(at, 11, DECK_Y + 7.2, -8)],
    [0, 1, 4],
    TOXIC,
  );
  hull.box([18, 6, 0.8], H.dark, { at: offset(at, 0, DECK_Y - 1.5, 9.8) });
  neon.box([20, 0.8, 0.6], TOXIC, { at: offset(at, 0, DECK_Y + 4.8, 10.2) });
  for (const s of SIDES) {
    neon.box([0.8, 6, 0.6], TOXIC, { at: offset(at, s * 9.8, DECK_Y - 1.4, 10.2) });
    lamps(neon, [offset(at, s * 11, DECK_Y + 7, 7)], 1.2, TOXIC);
  }
  vent(hull, offset(at, 0, DECK_Y + 7, -3), [12, 8], 4);
  vines(hull, [offset(at, 12, DECK_Y + 6, 9), offset(at, -4, DECK_Y + 6, 10)], 6);
}
