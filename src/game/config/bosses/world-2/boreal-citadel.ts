import type { Muzzle } from '../../../../core/entities/muzzle';
import {
  bullet,
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
 * P08-R10, 2-5's final boss: the Boreal Citadel. Offsets in px from the boss's centre, X right and
 * Y up (its nose points down, at -Y). Stage patterns as for the World 1 final bosses
 * (`final-bosses.ts`, P07-R04): its parts fire the same while they stand, its core fires every
 * kind of attack, a new one at each stage, and all of them at once with a spiral of its own,
 * used by no earlier stage, once it stands alone. Its core always drops a bonus (P07-R07).
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const GREEN = bullet('green', 185);
const PURPLE = bullet('purple', 195);
const MAGENTA = bullet('magenta', 190);

/** Where its parts stand (P08-R10): aurora cannons on the outriggers, batteries aft, domes ahead. */
export const BOREAL_PARTS = {
  cannon: [80, -8],
  battery: [48, 34],
  dome: [36, -40],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The right aurora cannon's lens, at the front of its long barrel. */
export const BOREAL_CANNON: Muzzle[] = [[80, -40, 7]];
/** The right missile battery's six cells, 2 columns by 3 rows. */
export const BOREAL_BATTERY: Muzzle[] = cells([43, 53], [26, 34, 42], 15.1);
/** The core's twin cannons on the keep's gun deck. */
export const BOREAL_GUNS: Muzzle[] = twin(7, -46.4, 17);
/** The core's ring emitter, on the keep's spire. */
export const BOREAL_SPIRE: Muzzle = [0, 0, 45];
/** The core's laser lens, between its twin cannons. */
export const BOREAL_LENS: Muzzle = [0, -48, 15];
/** The core's missile hatches, behind the keep. */
export const BOREAL_HATCHES: Muzzle[] = cells([-6, 6], [32, 40], 12.1);

const [cx, cy] = BOREAL_PARTS.cannon;
const [bx, by] = BOREAL_PARTS.battery;
const [dx, dy] = BOREAL_PARTS.dome;

/**
 * 2-5: the polar city's flying fortress; two aurora cannons sweep lasers, two missile batteries,
 * and two heated dome generators shield the core, which fires every kind of attack.
 */
export const BOREAL_CITADEL: BossDesign = {
  id: 'boreal-citadel',
  /** Angry after each destroyed part (phase 7 review): the hottest bullet hell so far. */
  rage: [...rage.curtain(7, 'green', 'purple', 0.5), ...rage.spirals(7, 'purple', 'magenta', 0.5)],
  stats: stats({
    id: 'boreal-citadel',
    name: 'Boreal Citadel',
    size: 6,
    coreRadius: 24,
    coreHealth: 6000,
    points: 18_000,
    groundSpeed: 0.25,
    coreDrop: 1,
    parts: [
      fpart('cannon-left', [-cx, cy], 15, 1900, { shields: false }),
      fpart('cannon-right', [cx, cy], 15, 1900, { shields: false }),
      fpart('battery-left', [-bx, by], 14, 1700, { shields: false }),
      fpart('battery-right', [bx, by], 14, 1700, { shields: false }),
      fpart('dome-left', [-dx, dy], 13, 2150),
      fpart('dome-right', [dx, dy], 13, 2150),
    ],
  }),
  stopFraction: 0.75,
  sway: { amplitude: 25, period: 11 },
  bob: { amplitude: 6, period: 5 },
  guns: {
    core: {
      gun: BOREAL_GUNS,
      ring: [BOREAL_SPIRE],
      laser: [BOREAL_LENS],
      missile: BOREAL_HATCHES,
    },
    'cannon-left': { laser: mirror(BOREAL_CANNON) },
    'cannon-right': { laser: BOREAL_CANNON },
    'battery-left': { missile: mirror(BOREAL_BATTERY) },
    'battery-right': { missile: BOREAL_BATTERY },
  },
  stages: stages(
    [
      volley.laser('cannon-left', 6.5, 1.6, 2, 15),
      volley.laser('cannon-right', 6.5, 1.6, 5.25, -15),
      volley.missiles('battery-left', 5.5, 2, 24, 3.5),
      volley.missiles('battery-right', 5.5, 2, 24, 6.25),
    ],
    [
      [volley.aimed('core', 2.6, 3, 10, PURPLE, 1.4)],
      [volley.fan('core', 2.4, 5, 14, GREEN, 0.8)],
      [volley.burst('core', 2.3, 4, 0.12, PURPLE, 0.6)],
      [volley.missiles('core', 5, 2, 30, 1.5), volley.aimed('core', 2.2, 1, 0, MAGENTA, 1)],
      [volley.laser('core', 5.5, 1.4, 1.5), volley.fan('core', 2.4, 7, 12, GREEN, 0.6)],
      [volley.ring('core', 2, 10, 0, GREEN, 0.6), volley.burst('core', 2.6, 3, 0.12, MAGENTA, 1)],
      [
        volley.ring('core', 1.2, 16, 9, PURPLE, 0.4),
        volley.laser('core', 5, 1.4, 2, 20),
        volley.missiles('core', 6, 2, 30, 3),
        volley.fan('core', 2.8, 5, 14, GREEN, 1.4),
      ],
    ],
  ),
};
