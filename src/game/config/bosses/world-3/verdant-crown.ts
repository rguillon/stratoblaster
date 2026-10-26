import type { Muzzle } from '../../../../core/entities/muzzle';
import {
  bullet,
  bursting,
  cells,
  mirror,
  part,
  stages,
  stats,
  twin,
  volley,
  type BossDesign,
} from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P09-R09, 3-5's final boss: the Verdant Crown, World 3's last boss. Offsets in px from the
 * boss's centre, X right and Y up (its nose points down, at -Y). Stage patterns as for the World
 * 1 and 2 final bosses (P07-R04, D-055): its parts fire the same while they stand, its core fires
 * every kind of attack, a new one at each stage (seed pods bursting into rings among them), and
 * all of them at once with a spiral of its own, used by no earlier stage, once it stands alone.
 * Its core always drops a bonus (P07-R07).
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const GREEN = bullet('green', 205);
const MAGENTA = bullet('magenta', 210);
const PURPLE = bullet('purple', 200);
/** A slow, big seed pod that bursts into a ring of small bullets on its way down. */
const SEED_POD = bursting('green', 115, 7, [1.1, 8, bullet('magenta', 190)]);

/**
 * Where its parts stand (P09-R09): thorn cannons on the outriggers, seed batteries aft, root
 * generators ahead of the dome.
 */
export const VERDANT_PARTS = {
  thorn: [82, -6],
  seed: [52, 40],
  root: [32, -48],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.
 */

/** The right thorn cannon's lens, at the front of its thorned barrel. */
export const VERDANT_THORN: Muzzle[] = [[VERDANT_PARTS.thorn[0], -40, 9]];
/** The right seed battery's six cells, 2 columns by 3 rows. */
export const VERDANT_SEEDS: Muzzle[] = cells([47, 57], [32, 40, 48], 14.1);
/** The core's twin cannons on the bow. */
export const VERDANT_GUNS: Muzzle[] = twin(8, -82, 9);
/** The core's laser lens, on the bow between its twin cannons. */
export const VERDANT_LENS: Muzzle = [0, -86, 8];
/** The core's ring emitter, the bloom on top of the dome's tallest tree. */
export const VERDANT_BLOOM: Muzzle = [0, 0, 44];
/** The core's missile hatches, on the deck behind the dome. */
export const VERDANT_HATCHES: Muzzle[] = cells([-7, 7], [48, 56], 9.1);

const [tx, ty] = VERDANT_PARTS.thorn;
const [sx, sy] = VERDANT_PARTS.seed;
const [rx, ry] = VERDANT_PARTS.root;

/**
 * 3-5: the canopy city's flying crown, a city-ship carrying a glass garden dome under emerald and
 * magenta neon; two thorn cannons on turrets aim lasers, two seed batteries fire homing missiles,
 * two root generators shield the core, which fires every kind of attack.
 */
export const VERDANT_CROWN: BossDesign = {
  id: 'verdant-crown',
  /** Angry after each destroyed part (phase 7 review): the hottest bullet hell so far. */
  rage: [...rage.flower(9, 'green', 'magenta', 0.5), ...rage.spirals(9, 'magenta', 'purple', 0.5)],
  stats: stats({
    id: 'verdant-crown',
    name: 'Verdant Crown',
    size: 6,
    coreRadius: 26,
    coreHealth: 6900,
    points: 22_000,
    groundSpeed: 0.25,
    coreDrop: 1,
    parts: [
      fpart('thorn-left', [-tx, ty], 15, 2100, { shields: false }),
      fpart('thorn-right', [tx, ty], 15, 2100, { shields: false }),
      fpart('seed-left', [-sx, sy], 14, 1900, { shields: false }),
      fpart('seed-right', [sx, sy], 14, 1900, { shields: false }),
      fpart('root-left', [-rx, ry], 14, 2300),
      fpart('root-right', [rx, ry], 14, 2300),
    ],
  }),
  stopFraction: 0.75,
  sway: { amplitude: 25, period: 11 },
  bob: { amplitude: 6, period: 5 },
  guns: {
    core: {
      gun: VERDANT_GUNS,
      ring: [VERDANT_BLOOM],
      laser: [VERDANT_LENS],
      missile: VERDANT_HATCHES,
    },
    'thorn-left': { laser: mirror(VERDANT_THORN), turret: [-tx, ty], turretLaser: true },
    'thorn-right': { laser: VERDANT_THORN, turret: [tx, ty], turretLaser: true },
    'seed-left': { missile: mirror(VERDANT_SEEDS) },
    'seed-right': { missile: VERDANT_SEEDS },
  },
  stages: stages(
    [
      volley.laser('thorn-left', 6, 1.6, 2),
      volley.laser('thorn-right', 6, 1.6, 5),
      volley.missiles('seed-left', 5, 2, 24, 3.5),
      volley.missiles('seed-right', 5, 2, 24, 6),
    ],
    [
      [volley.burst('core', 2.4, 4, 0.12, MAGENTA, 1.4)],
      [volley.fan('core', 2.3, 5, 13, GREEN, 0.8)],
      [volley.aimed('core', 3, 1, 0, SEED_POD, 0.8), volley.aimed('core', 2.2, 3, 10, PURPLE, 1.9)],
      [volley.missiles('core', 4.5, 2, 30, 1.5), volley.burst('core', 2.2, 3, 0.12, GREEN, 1)],
      [volley.laser('core', 5, 1.4, 1.5), volley.fan('core', 2.3, 7, 11, MAGENTA, 0.6)],
      [volley.ring('core', 1.8, 12, 0, GREEN, 0.6), volley.aimed('core', 2.6, 1, 0, SEED_POD, 1.3)],
      [
        volley.ring('core', 1.1, 16, 10, MAGENTA, 0.4),
        volley.laser('core', 5, 1.4, 2),
        volley.missiles('core', 5.5, 2, 30, 3),
        volley.fan('core', 3, 3, 30, SEED_POD, 1.4),
        volley.burst('core', 2.6, 3, 0.12, PURPLE, 1.8),
      ],
    ],
  ),
};
