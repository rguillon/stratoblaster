import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P08-R10, 2-3: the Snow Owl, the mini boss of the Tundra level. Offsets in px from the boss's
 * centre, X right and Y up (its nose points down, at -Y). The stage patterns are the agent's
 * design (P07-R04): the parts fire the same while they stand, the core fires something new at
 * every stage, and its last stage (only the core left) a ring used by no earlier stage. Health
 * values are placeholders for the P08-R11 tuning.
 */

const MAGENTA = bullet('magenta', 180);
const RED = bullet('red', 190);
const BLUE = bullet('blue', 185);
const PURPLE = bullet('purple', 195);

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The right wing radar pod's two fan barrels, under the pod's front. */
export const OWL_POD_GUNS: Muzzle[] = twin(38, -17, 1.5, 2.5);
/** The sensor eye's lens: its laser leaves from the lens's centre. */
export const OWL_EYE_LENS: Muzzle[] = [[0, -38.5, 6]];
/** The two chin guns either side of the eye (the core's aimed shots and bursts). */
export const OWL_CHIN_GUNS: Muzzle[] = twin(13, -27, 1.5);
/** The crown emitter on its back, between the ear tufts (the core's last-stage rings). */
export const OWL_CROWN: Muzzle[] = [[0, 10, 12.5]];

/**
 * 2-3: a wide-winged recon drone with white neon and a big round sensor eye at its front; two
 * wing radar pods fire fans and shield the core, the eye fires a laser after its warning line
 * (P08-R10). The eye sits in front of the core, so it can always be shot.
 */
export const SNOW_OWL: BossDesign = {
  id: 'snow-owl',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.flower(4.5, 'blue', 'magenta'),
  stats: stats({
    id: 'snow-owl',
    name: 'Snow Owl',
    size: 3,
    coreRadius: 18,
    coreHealth: 1250,
    points: 5500,
    groundSpeed: 0.5,
    parts: [
      part('pod-left', [-38, -2], 13, 850),
      part('pod-right', [38, -2], 13, 850),
      part('eye', [0, -30], 11, 600, { shields: false }),
    ],
  }),
  stopFraction: 0.73,
  sway: { amplitude: 65, period: 7.5 },
  bob: { amplitude: 9, period: 3.4 },
  guns: {
    core: { gun: OWL_CHIN_GUNS, ring: OWL_CROWN },
    'pod-left': { gun: mirror(OWL_POD_GUNS) },
    'pod-right': { gun: OWL_POD_GUNS },
    eye: { laser: OWL_EYE_LENS },
  },
  stages: stages(
    [
      // The pods' fans cross under the drone, each leaning towards the other side.
      volley.fan('pod-left', 2.3, 3, 14, MAGENTA, 0.9, 10),
      volley.fan('pod-right', 2.3, 3, 14, MAGENTA, 2, -10),
      volley.laser('eye', 5.5, 1.4, 3),
    ],
    [
      [volley.aimed('core', 3, 1, 0, RED, 1.5)],
      [volley.aimed('core', 2.4, 3, 12, RED, 0.8)],
      [volley.burst('core', 2.2, 4, 0.14, RED, 0.6)],
      [volley.ring('core', 1.4, 12, 8, BLUE, 0.4), volley.aimed('core', 2.4, 1, 0, PURPLE, 1)],
    ],
  ),
};
