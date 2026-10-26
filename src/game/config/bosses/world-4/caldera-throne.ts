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
 * P10-R11, 4-5's final boss: the Caldera Throne, World 4's last boss and the hardest of the game
 * so far. Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
 * Stage patterns as for the earlier final bosses (P07-R04, D-055): its parts fire the same while
 * they stand, its core fires every kind of attack, a new one at each stage (magma bombs bursting
 * into rings among them), and all of them at once with a spiral of its own, used by no earlier
 * stage, once it stands alone. Its core always drops a bonus (P07-R07).
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const MAGENTA = bullet('magenta', 215);
const BLUE = bullet('blue', 210);
const PURPLE = bullet('purple', 205);
/** A slow, big magma bomb that bursts into a ring of small bullets on its way down. */
const MAGMA_BOMB = bursting('magenta', 115, 7, [1.05, 9, bullet('blue', 195)]);

/**
 * Where its parts stand (P10-R11): magma cannons on the side bastions, missile batteries aft,
 * heat shield generators ahead of the keep.
 */
export const CALDERA_PARTS = {
  magma: [88, -8],
  battery: [56, 46],
  shield: [34, -52],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.
 */

/** The right magma cannon's lens, at the front of its long barrel. */
export const CALDERA_MAGMA: Muzzle[] = [[CALDERA_PARTS.magma[0], -46, 10]];
/** The right missile battery's six cells, 2 columns by 3 rows. */
export const CALDERA_CELLS: Muzzle[] = cells([50, 62], [36, 46, 56], 15.1);
/** The core's twin cannons on the prow. */
export const CALDERA_GUNS: Muzzle[] = twin(10, -104, 10);
/** The core's laser lens, on the prow between its twin cannons. */
export const CALDERA_LENS: Muzzle = [0, -108, 9];
/** The core's ring emitter, the crown on top of the throne's keep. */
export const CALDERA_CROWN: Muzzle = [0, 4, 50];
/** The core's missile hatches, on the deck behind the keep. */
export const CALDERA_HATCHES: Muzzle[] = cells([-8, 8], [58, 68], 10.1);

const [mx, my] = CALDERA_PARTS.magma;
const [bx, by] = CALDERA_PARTS.battery;
const [sx, sy] = CALDERA_PARTS.shield;

/**
 * 4-5: the enemy's war fortress rising from the magma lake, crimson and gold neon over its whole
 * hull; two magma cannons on turrets aim lasers, two missile batteries fire homing missiles, two
 * heat shield generators shield the core, which fires every kind of attack. The ground stops
 * over the magma lake (×0).
 */
export const CALDERA_THRONE: BossDesign = {
  id: 'caldera-throne',
  /** Angry after each destroyed part (phase 7 review): the hottest bullet hell of the game. */
  rage: [...rage.spirals(14, 'magenta', 'purple', 0.5), ...rage.vortex(14, 'blue', 'magenta', 0.5)],
  stats: stats({
    id: 'caldera-throne',
    name: 'Caldera Throne',
    size: 6.5,
    coreRadius: 28,
    coreHealth: 7400,
    points: 26_000,
    groundSpeed: 0,
    coreDrop: 1,
    parts: [
      fpart('magma-left', [-mx, my], 16, 2300, { shields: false }),
      fpart('magma-right', [mx, my], 16, 2300, { shields: false }),
      fpart('battery-left', [-bx, by], 15, 2000, { shields: false }),
      fpart('battery-right', [bx, by], 15, 2000, { shields: false }),
      fpart('shield-left', [-sx, sy], 15, 2600),
      fpart('shield-right', [sx, sy], 15, 2600),
    ],
  }),
  stopFraction: 0.75,
  sway: { amplitude: 22, period: 12 },
  bob: { amplitude: 5, period: 5.5 },
  guns: {
    core: {
      gun: CALDERA_GUNS,
      ring: [CALDERA_CROWN],
      laser: [CALDERA_LENS],
      missile: CALDERA_HATCHES,
    },
    'magma-left': { laser: mirror(CALDERA_MAGMA), turret: [-mx, my], turretLaser: true },
    'magma-right': { laser: CALDERA_MAGMA, turret: [mx, my], turretLaser: true },
    'battery-left': { missile: mirror(CALDERA_CELLS) },
    'battery-right': { missile: CALDERA_CELLS },
  },
  stages: stages(
    [
      volley.laser('magma-left', 5.5, 1.6, 2),
      volley.laser('magma-right', 5.5, 1.6, 4.75),
      volley.missiles('battery-left', 4.6, 2, 24, 3.2),
      volley.missiles('battery-right', 4.6, 2, 24, 5.5),
    ],
    [
      [volley.burst('core', 2.2, 4, 0.11, MAGENTA, 1.2)],
      [volley.fan('core', 2.1, 7, 12, BLUE, 0.8)],
      [
        volley.aimed('core', 2.8, 1, 0, MAGMA_BOMB, 0.8),
        volley.aimed('core', 2.1, 3, 10, PURPLE, 1.8),
      ],
      [
        volley.ring('core', 1.4, 12, 9, PURPLE, 0.6),
        volley.burst('core', 2.3, 3, 0.11, MAGENTA, 1.3),
      ],
      [
        volley.missiles('core', 4.2, 2, 30, 1.2),
        volley.fan('core', 2.2, 5, 14, BLUE, 0.7),
        volley.burst('core', 2.5, 3, 0.11, MAGENTA, 1.8),
      ],
      [
        volley.laser('core', 5, 1.5, 1.4),
        volley.ring('core', 1.7, 14, 0, PURPLE, 0.6),
        volley.aimed('core', 2.7, 1, 0, MAGMA_BOMB, 1.5),
      ],
      [
        volley.ring('core', 1, 18, 10, PURPLE, 0.4),
        volley.laser('core', 5, 1.5, 2),
        volley.missiles('core', 5, 2, 30, 3),
        volley.fan('core', 3.2, 3, 30, MAGMA_BOMB, 1.4),
        volley.burst('core', 2.4, 4, 0.11, MAGENTA, 1.8),
        volley.aimed('core', 3, 3, 12, BLUE, 2.6),
      ],
    ],
  ),
};
