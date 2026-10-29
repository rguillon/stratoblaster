import { mirror } from '../../../config/bosses/boss-kit';
import {
  DREAD_HEIGHTS,
  DREAD_RACK,
  DREAD_STACK,
  DREAD_TURRET_GUNS,
} from '../../../config/bosses/world-4/steam-dreadnought';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { bossPoint } from '../boss-limbs';
import { missileTips } from '../final-boss-shapes';
import { hazard } from '../mini-boss-greebles';
import { H, offset, SHADE, WHITE } from '../mini-boss-shapes';
import { barrelTo, blot, FORGE, moltenSeam, soot, steam } from './black-sands-kit';
import { organ } from '../../../../render/geometry/organic';
import { SKIN } from './living-forge';

// P10-R11, 4-1: the Steam Dreadnought's parts: its two smokestacks, its two broadside turrets
// (each turning on its barbette, D-058) and the missile rack on its stern. Logical pixels, nose
// +Z, Y up; the left ones (the screen's left, -X on the playfield) are drawn at +X.
type Vec3 = [number, number, number];

/** The Steam Dreadnought's red neon (P10-R11). */
export const DREAD_RED = BOSS_LOOK.neon['steam-dreadnought'] ?? [1, 0.08, 0.1];

// P16-R06: the stacks are steaming blowholes of flesh banded in metal, the rack a fleshy growth
// cased in a metal launcher, the turrets metal grafts on flesh mounts.

const DECK = DREAD_HEIGHTS.deck;
/** The side of a part drawn at `at`: +1 for a left one (at +X), -1 for a right one. */
const sideAt = (at: readonly number[]): number => Math.sign(at[0] ?? 1) || 1;

/** A smokestack's casing (a lathe profile up from the deck, radius and height). */
const STACK = [
  [9.5, DECK],
  [9.5, DECK + 2],
  [7.2, DECK + 3],
  [6.4, DECK + 8],
  [6.4, DREAD_HEIGHTS.stack - 4],
  [7.4, DREAD_HEIGHTS.stack - 3],
  [7.4, DREAD_HEIGHTS.stack],
] as const;

/**
 * A smokestack (P10-R11) around its centre `at`: a tall casing banded with worn metal and a red
 * neon ring, sooted at the top, its mouth glowing as the next ring loads, steam puffing back
 * from it.
 */
export function smokestack(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const s = sideAt(at);
  const [mouth] = s > 0 ? DREAD_STACK : mirror(DREAD_STACK);
  if (!mouth) return;
  const tip = bossPoint(...mouth);
  p.flesh.lathe(STACK, 8, SKIN.base, { at: [at[0], 0, at[2]], yaw: Math.PI / 8 });
  for (const y of [DECK + 9, DECK + 15]) {
    hull.ring(6.7, 1, 8, SHADE.edge, { at: [at[0], y, at[2]], yaw: Math.PI / 8 });
  }
  neon.ring(6.75, 0.9, 8, DREAD_RED, { at: [at[0], DREAD_HEIGHTS.stack - 6, at[2]] });
  hull.ring(7.6, 2.4, 8, FORGE.soot, { at: offset(tip, 0, -2.4, 0), yaw: Math.PI / 8 });
  hull.cylinder(5.8, 0.3, 8, H.dark, { at: offset(tip, 0, -0.25, 0) });
  charge.cylinder(4.6, 0.3, 8, WHITE, { at: offset(tip, 0, -0.1, 0) });
  muzzle(tip);
  steam(neon, offset(tip, s * 0.6, 3, -3), 3, 2.6);
  hull.box([2, 10, 2], H.dark, { at: [at[0] - s * 7.4, DECK, at[2] - 3] });
}

/** The broadside turret's barbette (a lathe profile up from the deck) and its dome. */
const BARBETTE = [
  [10.5, DECK - 0.5],
  [10.5, DECK + 2.5],
  [9.5, DECK + 3],
] as const;
const DOME = [
  [8.6, 0],
  [8.6, 1.4],
  [7.2, 3.4],
  [4, 4.6],
  [0, 4.8],
] as const;

/** A broadside turret's mount (P10-R11): its armoured barbette with a red ring, on the sponson. */
export function barbette({ hull, neon, flesh }: EnemyParts, at: Vec3): void {
  const s = sideAt(at);
  flesh.lathe(BARBETTE, 8, SKIN.panel, { at: [at[0], 0, at[2]], yaw: Math.PI / 8 });
  neon.ring(10.6, 0.7, 8, DREAD_RED, { at: [at[0], DECK + 0.6, at[2]], yaw: Math.PI / 8 });
  hazard(hull, [at[0] + s * 4, DECK + 0.05, at[2] - 13], [10, 3], 4);
}

/**
 * A broadside turret (P10-R11) around its pivot `at`: a faceted dome with a mantlet, a
 * rangefinder across its roof, twin barrels pointing down the screen at rest (they turn with
 * the turret, D-058), a molten seam on its roof.
 */
export function broadside(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  const s = sideAt(at);
  const foot: Vec3 = [at[0], DECK + 2.6, at[2]];
  hull.lathe(DOME, 8, H.base, { at: foot, yaw: Math.PI / 8 });
  hull.box([9, 4, 4], H.dark, { at: offset(foot, 0, 0.5, 6.6) }, H.panel);
  hull.box([16, 1.4, 2], H.panel, { at: offset(foot, 0, 4.2, -2) });
  hull.box([3, 1.6, 2.6], SHADE.edge, { at: offset(foot, s * 7.5, 3.8, -2) });
  moltenSeam(
    neon,
    [
      [at[0] - 4, at[2] + 1],
      [at[0], at[2] + 2.2],
      [at[0] + 4, at[2] + 1],
    ],
    foot[1] + 4.6,
  );
  const guns = s > 0 ? DREAD_TURRET_GUNS : mirror(DREAD_TURRET_GUNS);
  for (const tip of guns) barrelTo(p, tip, [1.3, 10]);
}

/** The missile tubes: their radius (their tips stand `2.6 radius` above their foot). */
const TUBE = 1.8;

/**
 * The missile rack (P10-R11) around its centre `at`, on the stern: an armoured launcher box,
 * red lights along its sides, four missile tips in their tubes, soot from the launches.
 */
export function missileRack(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  const [cell] = DREAD_RACK;
  const top = (cell?.[2] ?? DREAD_HEIGHTS.rack) - TUBE * 2.6;
  organ(p.flesh, 13, 6, SKIN.base, { at: [at[0], DECK - 3, at[2]] }, 0.3);
  hull.box([18, top - DECK, 18], H.base, { at: [at[0], DECK, at[2]] }, H.panel);
  for (const s of [-1, 1]) {
    neon.box([0.5, 0.8, 18], DREAD_RED, { at: [at[0] + s * 11.1, top - 2, at[2]] });
    hull.box([2.4, top - DECK + 1, 6], H.dark, { at: [at[0] + s * 12, DECK - 1, at[2] - 7] });
  }
  missileTips(p, [at[0], top, at[2]], [2, 2], [10, TUBE]);
  soot(hull, blot([at[0], at[2] + 6], 4, 0.5, 4), top);
}
