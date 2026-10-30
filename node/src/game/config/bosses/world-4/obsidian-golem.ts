import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import {
  bullet,
  bursting,
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
 * P10-R11, 4-3: the Obsidian Golem, the final boss of the Lava fields level. Offsets in px from
 * the boss's centre, X right and Y up (its chest faces down the screen, at -Y). Its two huge
 * fists hang on arms bending at the shoulder and the elbow (D-061), pumping in turn. The stage
 * patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core
 * fires something new at every stage, and its last stage (only the core left) magma bombs and
 * spirals used by no earlier stage. Health tuned for P10-R12 with the D-055 bot.
 */

const RED = bullet('red', 215);
const ORANGE = bullet('orange', 205);
const MAGENTA = bullet('magenta', 210);
const PURPLE = bullet('purple', 200);
/** The fists' magma: slow, big globs thrown out in rings (P10-R11). */
const MAGMA = bullet('orange', 110, 9);
/** The last stage's magma bomb: a slow glob bursting into a ring of small drops. */
const BOMB = bursting('red', 120, 8, [1.1, 10, bullet('orange', 170)]);

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/** The arms, by side. */
export type Arm = 'left' | 'right';
export const ARMS: readonly Arm[] = ['left', 'right'];

/**
 * Where the left arm (at -X) bends and holds its fist, as drawn at rest: its shoulder, its
 * elbow and its fist's centre. The right arm mirrors it.
 */
export const GOLEM_ARM = {
  shoulder: [-40, -2],
  elbow: [-60, -16],
  fist: [-72, -42],
} as const;

/** Where its other parts stand: the left shoulder cannon (mirrored), the plate, the emitter. */
export const GOLEM_PARTS = {
  cannon: [-46, 20],
  plate: [0, -34],
  emitter: [0, -58],
} as const;

/** How the arms pump (D-061): degrees at the shoulder and the elbow, seconds of one swing. */
const PUMP = { shoulderDeg: 9, elbowDeg: 14, period: 4.2, lag: 0.25 } as const;

/** The side of `arm`: +1 for the left one (drawn at -X, as in {@link GOLEM_ARM}), -1 for the right. */
export const sideOf = (arm: Arm): number => (arm === 'left' ? 1 : -1);

/** The shoulder and elbow joints of `arm`, the right one half a swing out of step. */
function armJoints(arm: Arm): Record<string, BossJointSpec> {
  const s = sideOf(arm);
  const phase = arm === 'left' ? 0 : 0.5;
  const [sx, sy] = GOLEM_ARM.shoulder;
  const [ex, ey] = GOLEM_ARM.elbow;
  return {
    [`shoulder-${arm}`]: {
      x: s * sx,
      y: sy,
      swing: { amplitudeDeg: s * PUMP.shoulderDeg, period: PUMP.period, phase },
    },
    [`elbow-${arm}`]: {
      x: s * ex,
      y: ey,
      parent: `shoulder-${arm}`,
      swing: { amplitudeDeg: s * PUMP.elbowDeg, period: PUMP.period, phase: phase + PUMP.lag },
    },
  };
}

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.
 */

/** The left fist's magma vent, in the middle of its knuckles (mirrored on the right). */
export const GOLEM_KNUCKLES: Muzzle[] = [[-72, -57, 7]];
/** The left shoulder cannon's twin barrels, as its turret rests (mirrored on the right). */
export const GOLEM_CANNON_GUNS: Muzzle[] = twin(-46, 5, 15, 2.6);
/** The chest emitter's lens, at the front of its prow (its laser fires straight down). */
export const GOLEM_LENS: Muzzle[] = [[0, -68, 6]];
/** The twin guns under its brow (the core's aimed shots, bursts, fans and bombs). */
export const GOLEM_BROW: Muzzle[] = twin(6, -24, 22);
/** The furnace stack on its back (the core's rings and spirals). */
export const GOLEM_STACK: Muzzle[] = [[0, 30, 30]];

const [FIST_X, FIST_Y] = GOLEM_ARM.fist;
const [CANNON_X, CANNON_Y] = GOLEM_PARTS.cannon;

/** `arm`'s fist, on its elbow (P10-R11): it shields the core. */
const fist = (arm: Arm, health: number) =>
  fpart(`fist-${arm}`, [sideOf(arm) * FIST_X, FIST_Y], 17, health, { joint: `elbow-${arm}` });

/**
 * 4-3: a massive armoured flying fortress of black obsidian plates with glowing magma seams and
 * two huge fists (P10-R11). The fists throw rings of slow magma and, with the armour plate on
 * its chest, shield the core; the shoulder cannons turn to fire aimed spreads; the chest emitter
 * on its prow fires a laser straight down. The emitter hangs in front of the plate, so it can
 * always be shot.
 */
export const OBSIDIAN_GOLEM: BossDesign = {
  id: 'obsidian-golem',
  /** Angry after each destroyed part (phase 7 review, D-063). */
  rage: [...rage.flower(12, 'orange', 'red', 0.5), ...rage.vortex(12, 'red', 'magenta', 0.5)],
  stats: stats({
    id: 'obsidian-golem',
    name: 'Obsidian Golem',
    size: 5.5,
    coreRadius: 24,
    coreHealth: 5200,
    points: 16_000,
    groundSpeed: 0.3,
    coreDrop: 1,
    parts: [
      fist('left', 1600),
      fist('right', 1600),
      fpart('cannon-left', [CANNON_X, CANNON_Y], 13, 1100, { shields: false }),
      fpart('cannon-right', [-CANNON_X, CANNON_Y], 13, 1100, { shields: false }),
      fpart('emitter', [...GOLEM_PARTS.emitter], 12, 800, { shields: false }),
      fpart('plate', [...GOLEM_PARTS.plate], 16, 1000),
    ],
    joints: { ...armJoints('left'), ...armJoints('right') },
  }),
  stopFraction: 0.74,
  sway: { amplitude: 24, period: 12 },
  bob: { amplitude: 5, period: 6 },
  guns: {
    core: { gun: GOLEM_BROW, ring: GOLEM_STACK },
    'fist-left': { gun: GOLEM_KNUCKLES },
    'fist-right': { gun: mirror(GOLEM_KNUCKLES) },
    'cannon-left': { gun: GOLEM_CANNON_GUNS, turret: [CANNON_X, CANNON_Y] },
    'cannon-right': { gun: mirror(GOLEM_CANNON_GUNS), turret: [-CANNON_X, CANNON_Y] },
    emitter: { laser: GOLEM_LENS },
  },
  stages: stages(
    [
      volley.ring('fist-left', 4.4, 8, 11, MAGMA, 1.6),
      volley.ring('fist-right', 4.4, 8, -11, MAGMA, 3.8),
      volley.aimed('cannon-left', 3, 3, 12, MAGENTA, 1),
      volley.aimed('cannon-right', 3, 3, 12, MAGENTA, 2.5),
      volley.laser('emitter', 7, 1.6, 4),
    ],
    [
      [volley.aimed('core', 2.6, 1, 0, RED, 1.4)],
      [volley.burst('core', 2.5, 4, 0.13, RED, 0.8)],
      [volley.fan('core', 2.5, 5, 14, ORANGE, 0.6)],
      [volley.ring('core', 1.6, 10, 8, PURPLE, 0.5)],
      [volley.fan('core', 2.3, 7, 12, ORANGE, 0.6), volley.burst('core', 2.9, 3, 0.13, RED, 1.3)],
      [volley.ring('core', 1.5, 12, -9, PURPLE, 0.5), volley.aimed('core', 2.4, 3, 12, RED, 1.1)],
      [
        volley.aimed('core', 2.4, 1, 0, BOMB, 0.6),
        volley.ring('core', 1.3, 12, 11, ORANGE, 0.4),
        volley.ring('core', 1.3, 12, -13, PURPLE, 1.05),
      ],
    ],
  ),
};
