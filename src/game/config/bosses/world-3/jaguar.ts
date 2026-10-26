import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P09-R09, 3-5's mini boss: the Jaguar. Offsets in px from the boss's centre, X right and Y up
 * (its nose points down, at -Y). Stage patterns as for the World 1 and 2 mini bosses (P07-R04,
 * D-055): its claw guns fire aimed spreads and its tail cannon a laser while they stand, the core
 * fires a spiral that changes at every stage, and twin spirals of its own, used by no earlier
 * stage, once it stands alone.
 */

const ORANGE = bullet('orange', 205);
const RED = bullet('red', 200);
const PURPLE = bullet('purple', 195);

/** Where its parts stand: the claw guns at the front of the wing roots, the tail cannon aft. */
export const JAGUAR_PARTS = {
  claw: [34, -22],
  tail: [-30, 42],
} as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.
 */

/** The right claw gun's twin barrels, reaching forward between its talons. */
export const JAGUAR_CLAW: Muzzle[] = twin(JAGUAR_PARTS.claw[0], -42, 6, 2.6);
/** The tail cannon's lens, at the front of its barrel held high over the spine. */
export const JAGUAR_TAIL: Muzzle[] = [[JAGUAR_PARTS.tail[0], 18, 17]];
/** The core's twin fang guns, under the nose. */
export const JAGUAR_FANGS: Muzzle[] = twin(4.5, -55, 3);
/** The core's spiral emitter, the lit eye on its back behind the cockpit. */
export const JAGUAR_EYE: Muzzle = [0, -6, 13];

const [kx, ky] = JAGUAR_PARTS.claw;
const [tx, ty] = JAGUAR_PARTS.tail;

/**
 * 3-5: a sleek stealth interceptor with spotted armour and amber neon (P09-R09); two claw guns on
 * turrets shield the core, a tail cannon aims a laser, and the core fires spirals.
 */
export const JAGUAR: BossDesign = {
  id: 'jaguar',
  /** Angry after each destroyed part (phase 7 review): the hottest mini boss so far. */
  rage: rage.curtain(8.5, 'orange', 'red'),
  stats: stats({
    id: 'jaguar',
    name: 'Jaguar',
    size: 3.5,
    coreRadius: 20,
    coreHealth: 2000,
    points: 8000,
    groundSpeed: 0.6,
    parts: [
      part('claw-left', [-kx, ky], 15, 1100),
      part('claw-right', [kx, ky], 15, 1100),
      part('tail-cannon', [tx, ty], 14, 900, { shields: false }),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 60, period: 6 },
  bob: { amplitude: 8, period: 3 },
  guns: {
    core: { gun: JAGUAR_FANGS, ring: [JAGUAR_EYE] },
    'claw-left': { gun: mirror(JAGUAR_CLAW), turret: [-kx, ky] },
    'claw-right': { gun: JAGUAR_CLAW, turret: [kx, ky] },
    'tail-cannon': { laser: JAGUAR_TAIL, turret: [tx, ty], turretLaser: true },
  },
  stages: stages(
    [
      volley.aimed('claw-left', 2.1, 3, 11, ORANGE, 1),
      volley.aimed('claw-right', 2.1, 3, 11, ORANGE, 2.05),
      volley.laser('tail-cannon', 6, 1.4, 3),
    ],
    [
      [volley.ring('core', 0.55, 3, 17, RED, 0.6)],
      [volley.ring('core', 0.5, 4, -21, RED, 0.5)],
      [volley.ring('core', 0.5, 5, 25, PURPLE, 0.5)],
      [volley.ring('core', 0.45, 5, 13, RED, 0.4), volley.ring('core', 0.45, 5, -15, PURPLE, 0.62)],
    ],
  ),
};
