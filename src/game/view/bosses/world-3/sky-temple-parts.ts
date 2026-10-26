import { BOSS_LOOK } from '../../../config/boss-look';
import { TEMPLE_BEACON, TEMPLE_HEIGHTS } from '../../../config/bosses/world-3/sky-temple';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { SIDES } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { missileTips } from '../final-boss-shapes';
import { offset, WHITE } from '../mini-boss-shapes';
import { moss, STONE, vine } from './stone-idol-stone';

// P09-R09, 3-3: the Sky Temple's parts (its corner obelisks, its summit beacon). Logical pixels,
// nose +Z (its grand stair, down the screen), Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The Sky Temple's gold neon, and the cyan it shares its lights with (P09-R09). */
export const TEMPLE_GOLD: Rgb = BOSS_LOOK.neon['sky-temple'] ?? [1, 0.8, 0.2];
export const TEMPLE_CYAN: Rgb = [0.2, 0.95, 1];
/** An eighth of a turn: four-sided solids turned square to the axes. */
export const SQUARE = Math.PI / 4;
/** The pyramid's tiers: half widths (the base first) and their common height. */
export const TIERS = { halves: [74, 54, 44, 34], height: 9 } as const;
/** The height of the summit platform. */
export const SUMMIT = TIERS.halves.length * TIERS.height;

/** Heights of an obelisk: its plinth's top, its shaft's top (its pyramidion ends at its tip). */
const OBELISK = { plinth: TIERS.height + 4, shaft: TEMPLE_HEIGHTS.obelisk - 7 } as const;
/** A four-sided solid's corner radius for a half width `half`. */
const corner = (half: number): number => half * Math.SQRT2;

/**
 * A corner obelisk around its centre `at` (P09-R09): a plinth on the lowest tier, a tapering
 * stone shaft carved with gold glyphs, a gilt pyramidion whose tip fires its spirals, a vine
 * climbing it.
 */
export function obelisk(p: EnemyParts, at: Vec3): void {
  const { hull, neon, charge, muzzle } = p;
  const square = { yaw: SQUARE };
  hull.box([12, 4, 12], STONE.dark, { at: offset(at, 0, TIERS.height, 0) }, STONE.light);
  neon.ring(corner(6.1), 0.6, 4, TEMPLE_CYAN, {
    at: offset(at, 0, OBELISK.plinth - 0.8, 0),
    ...square,
  });
  const [base, top] = [4, 2.9];
  const height = OBELISK.shaft - OBELISK.plinth;
  hull.cylinder(
    corner(base),
    height,
    4,
    STONE.base,
    { at: offset(at, 0, OBELISK.plinth, 0), ...square },
    corner(top),
  );
  const tipHeight = TEMPLE_HEIGHTS.obelisk - OBELISK.shaft;
  hull.cylinder(
    corner(top + 0.3),
    tipHeight,
    4,
    STONE.gilt,
    { at: offset(at, 0, OBELISK.shaft, 0), ...square },
    0,
  );
  charge.ring(corner(top + 0.35), 1.2, 4, WHITE, {
    at: offset(at, 0, OBELISK.shaft + 0.2, 0),
    ...square,
  });
  muzzle(offset(at, 0, TEMPLE_HEIGHTS.obelisk, 0), 'ring');
  // Gold glyphs on its four faces, at three heights (each just proud of the tapering face).
  for (const k of [0.15, 0.45, 0.75]) {
    const y = OBELISK.plinth + height * k;
    const half = base + (top - base) * k + 0.15;
    for (const s of SIDES) {
      neon.box([1.8, 1.4, 0.3], TEMPLE_GOLD, { at: offset(at, 0, y, s * half) });
      neon.box([0.3, 1.4, 1.8], TEMPLE_GOLD, { at: offset(at, s * half, y, 0) });
    }
  }
  const s = Math.sign(at[0]);
  vine(hull, [
    offset(at, s * 6, TIERS.height + 4, 4),
    offset(at, s * 4.4, 16, 3),
    offset(at, s * 3.6, 22, -2),
    offset(at, s * 3.2, 27, 1),
  ]);
  moss(hull, offset(at, -s * 3, OBELISK.plinth, -4), 2.6, s);
}

/** The beacon's lantern: its tower's top, and its roof (under the missile tubes). */
const LANTERN = { base: SUMMIT + 10, roof: SUMMIT + 13 } as const;

/**
 * The summit beacon around its centre `at` (P09-R09): a square tower at the front of the summit,
 * a lantern burning cyan under a gilt roof, four missile tubes on the roof.
 */
export function beacon(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  hull.box(
    [12, LANTERN.base - SUMMIT, 12],
    STONE.base,
    { at: offset(at, 0, SUMMIT, 0) },
    STONE.light,
  );
  neon.ring(corner(6.1), 0.6, 4, TEMPLE_GOLD, {
    at: offset(at, 0, LANTERN.base - 1.6, 0),
    yaw: SQUARE,
  });
  const lantern = LANTERN.roof - LANTERN.base;
  neon.box([7, lantern, 7], TEMPLE_CYAN, { at: offset(at, 0, LANTERN.base, 0) });
  for (const x of SIDES) {
    for (const z of SIDES) {
      hull.box([1.6, lantern, 1.6], STONE.dark, { at: offset(at, x * 5, LANTERN.base, z * 5) });
    }
  }
  const tubes = TEMPLE_BEACON.map((m) => bossPoint(...m));
  const radius = 1.5;
  // The tubes' tips stand `2.6 radius` above their foot (see `missileTips`).
  const foot = (tubes[0]?.[1] ?? TEMPLE_HEIGHTS.beacon) - radius * 2.6;
  hull.box([13, foot - LANTERN.roof, 13], STONE.gilt, { at: offset(at, 0, LANTERN.roof, 0) });
  missileTips(p, [at[0], foot, at[2]], [2, 2], [6, radius]);
  moss(hull, offset(at, 4, SUMMIT, -7), 2.4, 2);
}
