import type { Muzzle } from '../../../../core/entities/muzzle';
import {
  bullet,
  mirror,
  onlyAfter,
  onlyWhile,
  part,
  stages,
  stats,
  volley,
  type BossDesign,
} from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P08-R10, 2-2: the Fjord Lynx, the mini boss of the Fjords. Offsets in px from the boss's
 * centre, X right and Y up (its nose points down, at -Y). Its radar mast aims its guns: while
 * the mast stands, the paws and the core fire at the player; once it is destroyed, they fire
 * fans at preset headings instead (`onlyWhile` / `onlyAfter`).
 */

const BLUE = bullet('blue', 185);
const MAGENTA = bullet('magenta', 190);
const PURPLE = bullet('purple', 175);

/** The part whose loss blinds the guns. */
const RADAR = 'radar-mast';

/** The left paw's centre (the right one mirrors it). */
const PAW: readonly [number, number] = [-30, -26];

/**
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.
 */

/** The right paw cannon's two barrels. */
const PAW_CANNON: Muzzle[] = [
  [31.8, -39.12, 5.74],
  [28.2, -39.12, 5.74],
];
/** The chin cannon's barrel, under the head. */
const CHIN: Muzzle[] = [[0, -41.64, 6.68]];

/**
 * 2-2: a fast, low gunship crouched like a lynx, two forward paws and tufted antennas, white and
 * cyan neon (P08-R10). Both paw cannons and the radar mast shield the core.
 */
export const FJORD_LYNX: BossDesign = {
  id: 'fjord-lynx',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.vortex(3.5, 'blue', 'magenta'),
  stats: stats({
    id: 'fjord-lynx',
    name: 'Fjord Lynx',
    size: 3,
    coreRadius: 18,
    coreHealth: 1080,
    points: 3500,
    groundSpeed: 0.6,
    parts: [
      part('paw-left', PAW, 13, 600),
      part('paw-right', [-PAW[0], PAW[1]], 13, 600),
      part(RADAR, [-25, 22], 11, 600),
    ],
  }),
  stopFraction: 0.72,
  sway: { amplitude: 75, period: 6 },
  bob: { amplitude: 8, period: 3 },
  guns: {
    core: { gun: CHIN, turret: [0, -30] },
    'paw-left': { gun: mirror(PAW_CANNON), turret: PAW },
    'paw-right': { gun: PAW_CANNON, turret: [-PAW[0], PAW[1]] },
  },
  stages: stages(
    [
      // Aimed spreads while the radar stands, then fans crossing in front of the nose.
      onlyWhile(volley.aimed('paw-left', 2.2, 3, 10, BLUE, 1), RADAR),
      onlyWhile(volley.aimed('paw-right', 2.2, 3, 10, BLUE, 2.1), RADAR),
      onlyAfter(volley.fan('paw-left', 2.2, 3, 12, BLUE, 1, 18), RADAR),
      onlyAfter(volley.fan('paw-right', 2.2, 3, 12, BLUE, 2.1, -18), RADAR),
    ],
    [
      [onlyWhile(volley.aimed('core', 3, 1, 0, MAGENTA, 1.5), RADAR)],
      [
        onlyWhile(volley.aimed('core', 2.6, 3, 12, MAGENTA, 0.8), RADAR),
        onlyAfter(volley.fan('core', 2.6, 3, 16, MAGENTA, 0.8), RADAR),
      ],
      [
        onlyWhile(volley.burst('core', 2.4, 4, 0.14, MAGENTA, 0.6), RADAR),
        onlyAfter(volley.fan('core', 2.2, 5, 14, MAGENTA, 0.6), RADAR),
      ],
      [volley.fan('core', 2.4, 7, 12, MAGENTA, 0.6), volley.ring('core', 1.6, 12, 9, PURPLE, 0.4)],
    ],
  ),
};
