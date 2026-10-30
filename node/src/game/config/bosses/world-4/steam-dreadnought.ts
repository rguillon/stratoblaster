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
 * P10-R11, 4-1: the Steam Dreadnought, the Black sands' final boss. Offsets in px from the boss's
 * centre, X right and Y up (its bow points down the screen, at -Y). The stage patterns are the
 * agent's design (P07-R04): the parts fire the same while they stand, the core fires its bow
 * laser at every stage with something new beside it, and its last stage (only the core left)
 * adds spirals used by no earlier stage. Health tuned with the D-055 bot for P10-R12.
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const RED = bullet('red', 205);
const ORANGE = bullet('orange', 195);
const MAGENTA = bullet('magenta', 210);
const PURPLE = bullet('purple', 200);
const BLUE = bullet('blue', 200);

/** Where the parts sit (the left ones, at -X; the right ones mirror them). */
export const DREAD_PARTS = {
  stack: [-30, 16],
  turret: [-56, -20],
  rack: [0, 54],
} as const;

/** Heights of its decks and of the smokestacks' mouths (model units over the playfield). */
export const DREAD_HEIGHTS = { deck: 9, stack: 34, rack: 15 } as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The left smokestack's mouth: its rings pour out of it with the steam. */
export const DREAD_STACK: Muzzle[] = [
  [DREAD_PARTS.stack[0], DREAD_PARTS.stack[1], DREAD_HEIGHTS.stack],
];
/** The left broadside turret's twin barrels, at rest (pointing down the screen). */
export const DREAD_TURRET_GUNS: Muzzle[] = twin(DREAD_PARTS.turret[0], -37, 12.5, 2.4);
/** The missile rack's cells, two by two, on the stern. */
export const DREAD_RACK: Muzzle[] = cells([-5, 5], [49, 59], DREAD_HEIGHTS.rack);
/** The bow laser's lens, at the stem. */
export const DREAD_LENS: Muzzle[] = [[0, -87, 6]];
/** The twin guns either side of the bow (the core's aimed shots and fans). */
export const DREAD_BOW_GUNS: Muzzle[] = twin(9, -70, 11);
/** The beacon on top of the bridge tower (the core's rings and spirals). */
export const DREAD_BEACON: Muzzle[] = [[0, -7, 38]];

const [STACK_X, STACK_Y] = DREAD_PARTS.stack;
const [TURRET_X, TURRET_Y] = DREAD_PARTS.turret;

/**
 * 4-1: a flying battleship 5 L long, soot-black armour with red neon and glowing seams, two
 * smokestacks puffing steam (P10-R11). The smokestacks fire rings of bullets and the two
 * broadside turrets aimed bursts; the four shield the core. The missile rack on the stern fires
 * homing missiles; the bow fires its laser after a warning line. The ground slows (×0.6).
 */
export const STEAM_DREADNOUGHT: BossDesign = {
  id: 'steam-dreadnought',
  /** Angry after each destroyed part (D-063), heat 10: World 4 goes on from World 3's 9, up to 14. */
  rage: rage.flower(10, 'red', 'orange'),
  stats: stats({
    id: 'steam-dreadnought',
    name: 'Steam Dreadnought',
    size: 5,
    coreRadius: 18,
    coreHealth: 3600,
    points: 21_000,
    groundSpeed: 0.6,
    coreDrop: 1,
    parts: [
      fpart('stack-left', [STACK_X, STACK_Y], 10, 850),
      fpart('stack-right', [-STACK_X, STACK_Y], 10, 850),
      fpart('turret-left', [TURRET_X, TURRET_Y], 10, 950),
      fpart('turret-right', [-TURRET_X, TURRET_Y], 10, 950),
      fpart('rack', [...DREAD_PARTS.rack], 10, 600, { shields: false }),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 40, period: 10 },
  bob: { amplitude: 5, period: 5 },
  guns: {
    core: { gun: DREAD_BOW_GUNS, laser: DREAD_LENS, ring: DREAD_BEACON },
    'stack-left': { gun: DREAD_STACK },
    'stack-right': { gun: mirror(DREAD_STACK) },
    'turret-left': { gun: DREAD_TURRET_GUNS, turret: [TURRET_X, TURRET_Y] },
    'turret-right': { gun: mirror(DREAD_TURRET_GUNS), turret: [-TURRET_X, TURRET_Y] },
    rack: { missile: DREAD_RACK },
  },
  stages: stages(
    [
      volley.ring('stack-left', 3.6, 10, 9, ORANGE, 1.2),
      volley.ring('stack-right', 3.6, 10, -9, ORANGE, 3),
      volley.burst('turret-left', 3.2, 4, 0.12, RED, 0.8),
      volley.burst('turret-right', 3.2, 4, 0.12, RED, 2.4),
      volley.missiles('rack', 6.5, 2, 30, 3.5),
    ],
    [
      [volley.laser('core', 7, 1.5, 4)],
      [volley.laser('core', 6.5, 1.5, 2), volley.aimed('core', 2.8, 3, 12, MAGENTA, 1)],
      [volley.laser('core', 6.5, 1.5, 2), volley.fan('core', 2.6, 5, 14, MAGENTA, 0.8)],
      [volley.laser('core', 6, 1.6, 2), volley.ring('core', 2.4, 12, 11, PURPLE, 0.7)],
      [
        volley.laser('core', 5.5, 1.6, 2),
        volley.fan('core', 2.4, 7, 12, MAGENTA, 0.6),
        volley.aimed('core', 2.4, 1, 0, RED, 1.8),
      ],
      // Alone: two spirals turning opposite ways from the bridge, under the laser.
      [
        volley.laser('core', 5, 1.6, 1.5),
        volley.ring('core', 0.5, 4, 19, BLUE, 0.4),
        volley.ring('core', 0.5, 4, -23, PURPLE, 0.65),
      ],
    ],
  ),
};
