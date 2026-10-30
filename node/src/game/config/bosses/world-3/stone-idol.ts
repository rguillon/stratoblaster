import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P09-R09, 3-3: the Stone Idol, the mini boss of the Lost temples level. Offsets in px from the
 * boss's centre, X right and Y up (its chin points down, at -Y). The stage patterns are the
 * agent's design (P07-R04): the eyes and the mouth fire the same while they stand, the core
 * fires something new at every stage, and its last stage (only the core left) a spiral used by
 * no earlier stage. Health tuned for P09-R10 with the D-055 bot.
 */

const MAGENTA = bullet('magenta', 205);
const ORANGE = bullet('orange', 210);
const PURPLE = bullet('purple', 200);
/** The mouth's boulders (P09-R09): slow and big. */
const BOULDER = bullet('purple', 115, 9);

/** Where its parts stand (P09-R09): the eyes either side of the nose, the mouth under it. */
export const IDOL_PARTS = {
  eye: [32, -4],
  mouth: [0, -34],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The right eye's lens, at the front of its eyeball as it rests (its laser, on a turret). */
export const IDOL_EYE: Muzzle[] = [[32, -11.5, 12]];
/** The two nostrils, under the nose's tip (the core's fans). */
export const IDOL_NOSTRILS: Muzzle[] = twin(4, -21, 14.5);
/** The throat, deep in the open mouth (the mouth's rings of boulders). */
export const IDOL_THROAT: Muzzle[] = [[0, -35, 12.8]];
/** The jewel set in the forehead (the core's last-stage spiral). */
export const IDOL_JEWEL: Muzzle[] = [[0, 27, 19]];

const [ex, ey] = IDOL_PARTS.eye;

/**
 * 3-3: a flying stone head with neon cracks, glowing eyes and mouth; its two eyes turn to aim
 * lasers and shield the core, its mouth spits rings of slow boulders (P09-R09). The ground
 * stops over the temple while it fights (×0).
 */
export const STONE_IDOL: BossDesign = {
  id: 'stone-idol',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.flower(6.5, 'magenta', 'orange'),
  stats: stats({
    id: 'stone-idol',
    name: 'Stone Idol',
    size: 3,
    coreRadius: 22,
    coreHealth: 1550,
    points: 7500,
    groundSpeed: 0,
    parts: [
      part('eye-left', [-ex, ey], 13, 950),
      part('eye-right', [ex, ey], 13, 950),
      part('mouth', IDOL_PARTS.mouth, 13, 750, { shields: false }),
    ],
  }),
  stopFraction: 0.72,
  sway: { amplitude: 60, period: 7.5 },
  bob: { amplitude: 8, period: 3.6 },
  guns: {
    core: { gun: IDOL_NOSTRILS, ring: IDOL_JEWEL },
    // The eyeballs turn to aim at the player during the warning line, and hold still while
    // their beam fires (D-073).
    'eye-left': { laser: mirror(IDOL_EYE), turret: [-ex, ey], turretLaser: true },
    'eye-right': { laser: IDOL_EYE, turret: [ex, ey], turretLaser: true },
    mouth: { ring: IDOL_THROAT },
  },
  stages: stages(
    [
      volley.laser('eye-left', 6.5, 1.5, 2),
      volley.laser('eye-right', 6.5, 1.5, 5.25),
      volley.ring('mouth', 3, 9, 20, BOULDER, 1.4),
    ],
    [
      [volley.fan('core', 2.6, 3, 16, MAGENTA, 1.2)],
      [volley.fan('core', 2.4, 5, 13, MAGENTA, 0.8)],
      [
        volley.fan('core', 2.6, 5, 12, ORANGE, 0.6, -18),
        volley.fan('core', 2.6, 5, 12, ORANGE, 1.9, 18),
      ],
      [volley.ring('core', 0.45, 5, 17, PURPLE, 0.3), volley.fan('core', 2.2, 7, 11, MAGENTA, 1)],
    ],
  ),
};
