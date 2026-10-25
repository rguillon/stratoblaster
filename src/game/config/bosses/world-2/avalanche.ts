import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P08-R10, 2-4: the Avalanche, the Glacier level's mini boss. Offsets in px from the boss's
 * centre, X right and Y up (its nose points down, at -Y). Its two drill arms swing on their
 * joints (D-061) and shield the core; a rock hopper on its back drops lines of slow big rocks.
 */

const ORANGE = bullet('orange', 180);
const RED = bullet('red', 190);
/** The hopper's rocks: slow and big, dropped in lines the player weaves through. */
const ROCK = bullet('purple', 110, 7);

/** Where each drill arm's left (-X) joints and drill sit, as drawn at rest (mirrored on the right). */
export const AVALANCHE_ARM = {
  shoulder: [-20, -12],
  elbow: [-34, -24],
  drill: [-42, -36],
} as const;

/*
 * The guns' muzzles: the tips of the barrels its model draws, from the boss's centre, X right,
 * Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The left drill's gun, along the drill's outer side (mirrored on the right). */
export const AVALANCHE_DRILL_GUN: Muzzle[] = [[-51, -50, 8]];
/** The core's twin guns under the cab's chin. */
export const AVALANCHE_CORE_GUNS: Muzzle[] = twin(6, -40, 5);
/** The hopper's chute, at the front of its bin: the rocks fall from its lip. */
export const AVALANCHE_CHUTE: Muzzle[] = [[0, 15, 12]];

/**
 * A drill arm's joints (D-061), the left one at -X: it swings at the shoulder and bends at the
 * elbow, the drill hanging on the elbow. The right arm is its mirror image, a little out of step.
 */
function drillArm(side: 'left' | 'right'): Record<string, BossJointSpec> {
  const [s, late] = side === 'left' ? [1, 0] : [-1, 0.37];
  const joint = (
    [x, y]: readonly [number, number],
    swing: readonly [amplitudeDeg: number, period: number, phase: number],
    parent?: string,
  ): BossJointSpec => ({
    x: s * x,
    y,
    ...(parent === undefined ? {} : { parent: `${parent}-${side}` }),
    swing: { amplitudeDeg: s * swing[0], period: swing[1], phase: swing[2] + late },
  });
  return {
    [`shoulder-${side}`]: joint(AVALANCHE_ARM.shoulder, [7, 4.2, 0]),
    [`elbow-${side}`]: joint(AVALANCHE_ARM.elbow, [12, 2.8, 0.25], 'shoulder'),
  };
}

const [DRILL_X, DRILL_Y] = AVALANCHE_ARM.drill;

/**
 * P08-R10, 2-4: a heavy drilling machine with two drill arms swinging in front of it (they fire
 * aimed bursts and shield the core) and a rock hopper on its back; the fight is a chase down
 * the glacier (ground ×1.4).
 */
export const AVALANCHE: BossDesign = {
  id: 'avalanche',
  /** Angry after each destroyed part (phase 7 review, D-063). */
  rage: rage.spirals(5.5, 'orange', 'red'),
  stats: stats({
    id: 'avalanche',
    name: 'Avalanche',
    size: 3.5,
    coreRadius: 18,
    coreHealth: 1400,
    points: 7000,
    groundSpeed: 1.4,
    parts: [
      part('drill-left', [DRILL_X, DRILL_Y], 14, 900, { joint: 'elbow-left' }),
      part('drill-right', [-DRILL_X, DRILL_Y], 14, 900, { joint: 'elbow-right' }),
      part('hopper', [0, 31], 14, 600, { shields: false }),
    ],
    joints: { ...drillArm('left'), ...drillArm('right') },
  }),
  stopFraction: 0.74,
  sway: { amplitude: 60, period: 7.5 },
  bob: { amplitude: 8, period: 3.2 },
  guns: {
    core: { gun: AVALANCHE_CORE_GUNS },
    'drill-left': { gun: AVALANCHE_DRILL_GUN },
    'drill-right': { gun: mirror(AVALANCHE_DRILL_GUN) },
    hopper: { gun: AVALANCHE_CHUTE },
  },
  stages: stages(
    [
      volley.burst('drill-left', 2.4, 3, 0.16, RED, 1),
      volley.burst('drill-right', 2.4, 3, 0.16, RED, 2.2),
      // Rows of rocks straight down, every other row offset: a lattice to weave through.
      volley.fan('hopper', 4, 3, 26, ROCK, 1.5),
      volley.fan('hopper', 4, 2, 26, ROCK, 2),
      volley.fan('hopper', 4, 3, 26, ROCK, 2.5),
    ],
    [
      [volley.fan('core', 3.2, 3, 16, ORANGE, 1.8)],
      [volley.fan('core', 2.6, 5, 14, ORANGE, 0.8)],
      [volley.fan('core', 2.2, 7, 12, ORANGE, 0.6)],
      [volley.ring('core', 1.6, 12, 9, ORANGE, 0.4), volley.fan('core', 2.6, 5, 14, RED, 1)],
    ],
  ),
};
