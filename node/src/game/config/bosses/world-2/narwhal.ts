import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/*
 * P08-R10, 2-1: the Narwhal, the final boss of the Ice floes level. Offsets in px from the
 * boss's centre, X right and Y up (its nose points down, at -Y). Stage patterns as for the
 * World 1 bosses (P07-R04): the parts fire the same while they stand, the core fires something
 * new at every stage, and its last stage (only the core left) spirals used by no earlier stage.
 * Its core always drops a bonus (P07-R07). Health values are placeholders for the P08-R11 tuning.
 */

const MAGENTA = bullet('magenta', 185);
const GREEN = bullet('green', 180);
const BLUE = bullet('blue', 190);
const PURPLE = bullet('purple', 195);

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The tip of the spiral horn, where the lance's laser leaves from. */
export const NARWHAL_HORN: Muzzle[] = [[0, -90, 4.5]];
/** The right torpedo tube's two mouths, on the hull's flank. */
export const NARWHAL_TUBE: Muzzle[] = twin(22, -47.02, 5, 2.5);
/** The right ballast pod's two fan guns, at its front. */
export const NARWHAL_POD: Muzzle[] = twin(40, -5.68, 6, 2.5);
/** The deck gun's two barrels, on the forward deck (the core's aimed shots, bursts and fans). */
export const NARWHAL_DECK_GUN: Muzzle[] = twin(1.33, -43.77, 18.42);
/** The spiral emitter on top of the sail (the core's last-stage spirals). */
export const NARWHAL_EMITTER: Muzzle[] = [[0, -10, 31]];

/**
 * 2-1: a long flying submarine with a spiral horn and teal neon along its back. Its horn lance
 * fires a laser, two torpedo tubes homing missiles, and two ballast pods fans; the ballast pods
 * shield the core (P08-R10). It chases the ground over the ice floes (×1.5).
 */
export const NARWHAL: BossDesign = {
  id: 'narwhal',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.vortex(3, 'magenta', 'blue'),
  stats: stats({
    id: 'narwhal',
    name: 'Narwhal',
    size: 5,
    coreRadius: 22,
    coreHealth: 2300,
    points: 16_000,
    groundSpeed: 1.5,
    coreDrop: 1,
    parts: [
      fpart('lance', [0, -70], 13, 1100, { shields: false }),
      fpart('tube-left', [-22, -32], 10, 650, { shields: false }),
      fpart('tube-right', [22, -32], 10, 650, { shields: false }),
      fpart('pod-left', [-40, 18], 14, 900),
      fpart('pod-right', [40, 18], 14, 900),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 45, period: 8 },
  bob: { amplitude: 10, period: 4 },
  guns: {
    core: { gun: NARWHAL_DECK_GUN, turret: [0, -32], ring: NARWHAL_EMITTER },
    lance: { laser: NARWHAL_HORN },
    'tube-left': { missile: mirror(NARWHAL_TUBE) },
    'tube-right': { missile: NARWHAL_TUBE },
    'pod-left': { gun: mirror(NARWHAL_POD) },
    'pod-right': { gun: NARWHAL_POD },
  },
  stages: stages(
    [
      volley.laser('lance', 6.5, 1.4, 2.5),
      volley.missiles('tube-left', 5.5, 2, 30, 3.5),
      volley.missiles('tube-right', 5.5, 2, 30, 6.25),
      volley.fan('pod-left', 2.2, 3, 15, GREEN, 0.8, -12),
      volley.fan('pod-right', 2.2, 3, 15, GREEN, 1.9, 12),
    ],
    [
      [volley.aimed('core', 3, 1, 0, MAGENTA, 1.6)],
      [volley.aimed('core', 2.6, 3, 12, MAGENTA, 0.8)],
      [volley.burst('core', 2.4, 4, 0.14, MAGENTA, 0.6)],
      [volley.fan('core', 2.4, 5, 14, MAGENTA, 0.6)],
      [volley.fan('core', 2.2, 7, 12, MAGENTA, 0.6), volley.aimed('core', 2.6, 1, 0, PURPLE, 1.2)],
      [volley.ring('core', 1.2, 10, 13, BLUE, 0.4), volley.ring('core', 1.2, 10, -17, PURPLE, 1)],
    ],
  ),
};
