import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, cells, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/*
 * P09-R09, 3-3: the Sky Temple, the final boss of the Lost temples level. Offsets in px from the
 * boss's centre, X right and Y up (its grand stair points down, at -Y). Stage patterns as for
 * the World 1 and 2 final bosses (P07-R04): its parts fire the same while they stand, its core
 * fires every bullet pattern, a new one at each stage (aimed shots, spreads, bursts, fans,
 * rings), and twin spirals used by no earlier stage once it stands alone. Its core always drops
 * a bonus (P07-R07). Health tuned for P09-R10 with the D-055 bot.
 */

const GOLD = bullet('orange', 200);
const RED = bullet('red', 210);
const BLUE = bullet('blue', 205);
const MAGENTA = bullet('magenta', 195);
const GREEN = bullet('green', 190);

/** Where its parts stand (P09-R09): an obelisk on each corner, the beacon on the summit. */
export const TEMPLE_PARTS = {
  obelisk: [60, 62],
  beacon: [0, -28],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The heights of the tips of the obelisks' pyramidions (their spirals), the beacon's cells. */
export const TEMPLE_HEIGHTS = { obelisk: 56, beacon: 54.1, guns: 41, crystal: 64 } as const;
/** The beacon's four missile cells, on its lantern's roof. */
export const TEMPLE_BEACON: Muzzle[] = cells([-3, 3], [-31, -25], TEMPLE_HEIGHTS.beacon);
/** The twin cannons either side of the sanctum's door (the core's shots, spreads, bursts, fans). */
export const TEMPLE_GUNS: Muzzle[] = twin(8, -11, TEMPLE_HEIGHTS.guns);
/** The crystal on the sanctum's roof (the core's rings and spirals). */
export const TEMPLE_CRYSTAL: Muzzle[] = [[0, 10, TEMPLE_HEIGHTS.crystal]];

const [ox, oy] = TEMPLE_PARTS.obelisk;
/** The obelisks, by part id, and where they stand (X right, Y up). */
export const OBELISKS = {
  'obelisk-front-left': [-ox, -oy],
  'obelisk-front-right': [ox, -oy],
  'obelisk-back-left': [-ox, oy],
  'obelisk-back-right': [ox, oy],
} as const;
/** The tip of an obelisk standing at `[x, y]`. */
const tip = ([x, y]: readonly [number, number]): Muzzle[] => [[x, y, TEMPLE_HEIGHTS.obelisk]];

/**
 * 3-3: a flying stepped pyramid, gold and cyan neon; its four corner obelisks fire spirals and
 * shield the core, its summit beacon homing missiles, its core every bullet pattern (P09-R09).
 */
export const SKY_TEMPLE: BossDesign = {
  id: 'sky-temple',
  /** Angry after each destroyed part (phase 7 review): a vortex inside a blooming flower. */
  rage: [...rage.vortex(7, 'orange', 'blue', 0.5), ...rage.flower(7, 'blue', 'orange', 0.5)],
  stats: stats({
    id: 'sky-temple',
    name: 'Sky Temple',
    size: 5.5,
    coreRadius: 22,
    coreHealth: 3550,
    points: 15_000,
    groundSpeed: 0.3,
    coreDrop: 1,
    parts: [
      fpart('obelisk-front-left', OBELISKS['obelisk-front-left'], 13, 1000),
      fpart('obelisk-front-right', OBELISKS['obelisk-front-right'], 13, 1000),
      fpart('obelisk-back-left', OBELISKS['obelisk-back-left'], 13, 1000),
      fpart('obelisk-back-right', OBELISKS['obelisk-back-right'], 13, 1000),
      fpart('beacon', TEMPLE_PARTS.beacon, 16, 2400, { shields: false }),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 30, period: 11 },
  bob: { amplitude: 6, period: 5 },
  guns: {
    core: { gun: TEMPLE_GUNS, ring: TEMPLE_CRYSTAL },
    'obelisk-front-left': { ring: tip(OBELISKS['obelisk-front-left']) },
    'obelisk-front-right': { ring: tip(OBELISKS['obelisk-front-right']) },
    'obelisk-back-left': { ring: tip(OBELISKS['obelisk-back-left']) },
    'obelisk-back-right': { ring: tip(OBELISKS['obelisk-back-right']) },
    beacon: { missile: TEMPLE_BEACON },
  },
  stages: stages(
    [
      // Each obelisk turns its own spiral, the front ones one way, the back ones the other.
      volley.ring('obelisk-front-left', 1.6, 4, 23, GOLD, 0.6),
      volley.ring('obelisk-front-right', 1.6, 4, -23, GOLD, 1.4),
      volley.ring('obelisk-back-left', 1.6, 4, -19, GOLD, 1),
      volley.ring('obelisk-back-right', 1.6, 4, 19, GOLD, 1.8),
      volley.missiles('beacon', 5.5, 2, 30, 3),
    ],
    [
      [volley.aimed('core', 2.8, 1, 0, RED, 1.6)],
      [volley.aimed('core', 2.6, 3, 12, RED, 0.8)],
      [volley.burst('core', 2.4, 4, 0.13, MAGENTA, 0.6)],
      [volley.fan('core', 2.4, 5, 14, BLUE, 0.6)],
      [volley.ring('core', 2, 12, 0, GREEN, 0.6), volley.fan('core', 2.6, 7, 12, BLUE, 1.2)],
      [
        volley.ring('core', 0.6, 6, 14, GOLD, 0.4),
        volley.ring('core', 0.6, 6, -19, BLUE, 0.7),
        volley.burst('core', 2.6, 3, 0.12, RED, 1.2),
      ],
    ],
  ),
};
