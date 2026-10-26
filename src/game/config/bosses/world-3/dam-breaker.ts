import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/*
 * P09-R09, 3-4: the Dam Breaker, the final boss of the swamp works, fought over the giant dam.
 * Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). The
 * stage patterns are the agent's design (P07-R04): the parts fire the same while they stand,
 * the core fires something new at every stage, and its last stage (only the core left) spirals
 * used by no earlier stage. Health tuned for P09-R10.
 */

const RED = bullet('red', 205);
const MAGENTA = bullet('magenta', 200);
const ORANGE = bullet('orange', 195);
const GREEN = bullet('green', 190);
/** A sluice's sludge: slow, big globs let out in waves the player weaves through (P09-R09). */
const SLUDGE = bullet('green', 125, 7);

/** Where the parts sit (the left ones, at -X; the right ones mirror them). */
export const DAM_SLUICE = [-46, -22] as const;
export const DAM_TANK = [-76, 14] as const;
export const DAM_PLATE = [0, -32] as const;
export const DAM_HANGAR = [0, -58] as const;

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The left sluice gate's spout: the sludge pours from the middle of its lip. */
export const DAM_SPOUT: Muzzle[] = [[-46, -38, 5]];
/** The twin guns on the pump house's front (the core's aimed shots, bursts and fans). */
export const DAM_CORE_GUNS: Muzzle[] = twin(11, -21, 12);
/** The top of the pump house's stack (the core's rings and spirals). */
export const DAM_STACK: Muzzle[] = [[0, 8, 30]];

const [SLUICE_X, SLUICE_Y] = DAM_SLUICE;
const [TANK_X, TANK_Y] = DAM_TANK;

/** A sluice's waves: a row of five globs, then a row of four between them. */
const waves = (from: string, first: number) => [
  volley.fan(from, 4, 5, 15, SLUDGE, first),
  volley.fan(from, 4, 4, 15, SLUDGE, first + 0.55),
];

/**
 * 3-4: a giant armoured barge with toxic green neon: two sluice cannons let out waves of slow
 * big sludge and, with the armour plate on its bow, shield the core; two glowing chemical tanks
 * burst into rings of bullets when destroyed (as the Refinery Titan's); a drone hangar at the
 * bow launches Hornets (as the Aurora Station's). The hangar hangs in front of the plate, so it
 * can always be shot.
 */
export const DAM_BREAKER: BossDesign = {
  id: 'dam-breaker',
  /** Angry after each destroyed part (phase 7 review, D-063). */
  rage: rage.curtain(8, 'green', 'orange'),
  stats: stats({
    id: 'dam-breaker',
    name: 'Dam Breaker',
    size: 5.5,
    coreRadius: 22,
    coreHealth: 5300,
    points: 15_000,
    groundSpeed: 0.3,
    coreDrop: 1,
    parts: [
      fpart('sluice-left', [SLUICE_X, SLUICE_Y], 15, 1650),
      fpart('sluice-right', [-SLUICE_X, SLUICE_Y], 15, 1650),
      fpart('plate', [...DAM_PLATE], 15, 1900),
      fpart('tank-left', [TANK_X, TANK_Y], 15, 1300, { shields: false }),
      fpart('tank-right', [-TANK_X, TANK_Y], 15, 1300, { shields: false }),
      fpart('hangar', [...DAM_HANGAR], 14, 900, { shields: false }),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 32, period: 11 },
  bob: { amplitude: 5, period: 5.5 },
  launches: [{ from: 'hangar', kind: 'hornets', count: 2, every: 7, first: 3.5 }],
  breakRings: {
    'tank-left': { count: 12, bullet: GREEN },
    'tank-right': { count: 12, bullet: GREEN },
  },
  guns: {
    core: { gun: DAM_CORE_GUNS, ring: DAM_STACK },
    'sluice-left': { gun: DAM_SPOUT },
    'sluice-right': { gun: mirror(DAM_SPOUT) },
  },
  stages: stages(
    [...waves('sluice-left', 1), ...waves('sluice-right', 3)],
    [
      [volley.aimed('core', 2.8, 1, 0, RED, 1.4)],
      [volley.aimed('core', 2.4, 3, 12, RED, 0.8)],
      [volley.burst('core', 2.4, 4, 0.13, ORANGE, 0.6)],
      [volley.fan('core', 2.4, 5, 14, MAGENTA, 0.6)],
      [volley.fan('core', 2.2, 7, 12, MAGENTA, 0.6), volley.burst('core', 2.8, 3, 0.13, RED, 1.2)],
      [volley.ring('core', 1.8, 10, 7, GREEN, 0.5), volley.aimed('core', 2.6, 1, 0, RED, 1.2)],
      [
        volley.ring('core', 1.3, 14, 9, GREEN, 0.4),
        volley.ring('core', 1.3, 14, -11, ORANGE, 1.05),
      ],
    ],
  ),
};
