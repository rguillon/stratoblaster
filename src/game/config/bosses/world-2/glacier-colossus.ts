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
 * P08-R10, 2-4: the Glacier Colossus, the Glacier level's final boss. Offsets in px from the
 * boss's centre, X right and Y up (its nose points down, at -Y). Six parts: two cutter lasers
 * out on its beam, two ore cannons and a heat sink at its bow (these three shield the core), and
 * a missile pod on its stern.
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const RED = bullet('red', 190);
const MAGENTA = bullet('magenta', 185);
/** The ore cannons' shells: big, a little slower than the stage bullets. */
const ORE = bullet('orange', 160, 6);

/** Where the left (-X) cutter and ore cannon sit (mirrored on the right). */
export const COLOSSUS_CUTTER = [-80, -10] as const;
export const COLOSSUS_ORE = [-44, -28] as const;
/** The heat sink at the bow and the missile pod on the stern. */
export const COLOSSUS_HEAT_SINK = [0, -48] as const;
export const COLOSSUS_POD = [0, 46] as const;

/*
 * The guns' muzzles: the tips of the barrels its model draws, from the boss's centre, X right,
 * Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The left cutter's laser emitter (mirrored on the right). */
export const COLOSSUS_CUTTER_LASER: Muzzle[] = [[-80, -42, 6]];
/** The left ore cannon's two fat barrels (mirrored on the right). */
export const COLOSSUS_ORE_GUNS: Muzzle[] = twin(-44, -50, 12, 3.5);
/** The core's twin guns on the bridge's front, over the heat sink. */
export const COLOSSUS_CORE_GUNS: Muzzle[] = twin(9, -30, 22);
/** The core's rings leave from the top of its heat stack. */
export const COLOSSUS_STACK: Muzzle[] = [[0, 6, 32]];
/** The missile pod's four cells. */
export const COLOSSUS_CELLS: Muzzle[] = cells([-5.5, 5.5], [41, 51], 24);

/**
 * P08-R10, 2-4: a giant mining ship with glowing heat vents; cutter lasers sweep from its beam,
 * ore cannons fire fans of big shells, a missile pod covers its stern, and a heat sink at its
 * bow (no weapon) shields the core with the ore cannons. The ground slows to ×0.3.
 */
export const GLACIER_COLOSSUS: BossDesign = {
  id: 'glacier-colossus',
  /** Angry after each destroyed part (phase 7 review, D-063). */
  rage: rage.flower(6, 'red', 'magenta'),
  stats: stats({
    id: 'glacier-colossus',
    name: 'Glacier Colossus',
    size: 5.5,
    coreRadius: 22,
    coreHealth: 4400,
    points: 14_000,
    groundSpeed: 0.3,
    coreDrop: 1,
    parts: [
      fpart('cutter-left', [...COLOSSUS_CUTTER], 15, 1200, { shields: false }),
      fpart('cutter-right', [-COLOSSUS_CUTTER[0], COLOSSUS_CUTTER[1]], 15, 1200, {
        shields: false,
      }),
      fpart('ore-left', [...COLOSSUS_ORE], 15, 1700),
      fpart('ore-right', [-COLOSSUS_ORE[0], COLOSSUS_ORE[1]], 15, 1700),
      fpart('heat-sink', [...COLOSSUS_HEAT_SINK], 16, 1900),
      fpart('missile-pod', [...COLOSSUS_POD], 14, 900, { shields: false }),
    ],
  }),
  stopFraction: 0.75,
  sway: { amplitude: 30, period: 10 },
  bob: { amplitude: 6, period: 5 },
  guns: {
    core: { gun: COLOSSUS_CORE_GUNS, ring: COLOSSUS_STACK },
    'cutter-left': { laser: COLOSSUS_CUTTER_LASER },
    'cutter-right': { laser: mirror(COLOSSUS_CUTTER_LASER) },
    'ore-left': { gun: COLOSSUS_ORE_GUNS },
    'ore-right': { gun: mirror(COLOSSUS_ORE_GUNS) },
    'missile-pod': { missile: COLOSSUS_CELLS },
  },
  stages: stages(
    [
      volley.laser('cutter-left', 6.5, 1.4, 2, 18),
      volley.laser('cutter-right', 6.5, 1.4, 5.25, -18),
      volley.fan('ore-left', 2.6, 3, 18, ORE, 0.9),
      volley.fan('ore-right', 2.6, 3, 18, ORE, 2.2),
      volley.missiles('missile-pod', 5.5, 2, 30, 3),
    ],
    [
      [volley.aimed('core', 2.8, 1, 0, RED, 1.4)],
      [volley.aimed('core', 2.4, 3, 12, RED, 0.8)],
      [volley.burst('core', 2.4, 4, 0.13, RED, 0.6)],
      [volley.ring('core', 2.2, 8, 0, MAGENTA, 0.6)],
      [volley.fan('core', 2.4, 7, 12, RED, 0.6), volley.burst('core', 2.8, 3, 0.13, RED, 1.2)],
      [volley.ring('core', 1.8, 10, 7, MAGENTA, 0.5), volley.aimed('core', 2.6, 1, 0, RED, 1.2)],
      [volley.ring('core', 1.3, 14, 9, MAGENTA, 0.4), volley.ring('core', 1.3, 14, -11, RED, 1.05)],
    ],
  ),
};
