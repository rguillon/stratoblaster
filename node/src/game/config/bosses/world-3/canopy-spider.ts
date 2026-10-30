import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, part, stages, stats, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P09-R09, 3-2: the Canopy Spider, the final boss of the Rainforest level. Offsets in px from the
 * boss's centre, X right and Y up (its head points down, at -Y). Its four legs bend at the hip
 * and the knee (D-061), stepping in turn, each out of step with the others. Stage patterns as
 * for the World 1 and 2 bosses (P07-R04): the legs fire the same while they stand, the core
 * spirals in a new way at every stage, and its last stage (only the core left) is a double
 * spiral used by no earlier stage. Health tuned with the D-055 bot for P09-R10.
 */

const RED = bullet('red', 205);
const PURPLE = bullet('purple', 195);
const MAGENTA = bullet('magenta', 200);
const GREEN = bullet('green', 190);

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/** The legs, by id: `fore` towards the head, `aft` towards the abdomen, either side. */
export type Leg = `${'fore' | 'aft'}-${'left' | 'right'}`;

/** The legs in the order of their parts. */
export const LEGS: readonly Leg[] = ['fore-left', 'fore-right', 'aft-left', 'aft-right'];

/**
 * Where a left leg (at -X) bends and holds its gun, as drawn at rest: its hip (on the body), its
 * knee and its foot (the gun pod's centre). The right legs mirror them.
 */
export const LEG_REST: Readonly<
  Record<'fore' | 'aft', readonly (readonly [x: number, y: number])[]>
> = {
  fore: [
    [-11, -20],
    [-24, -40],
    [-28, -62],
  ],
  aft: [
    [-16, 6],
    [-48, 18],
    [-70, 36],
  ],
};

/** Heights of a leg (model units over the playfield): its hip, its raised knee, its foot. */
export const LEG_HEIGHT = { hip: 8, knee: 22, foot: 4 } as const;

/** The stepping cycle: degrees at the hip and the knee, and the seconds of one step. */
const STEP = { hipDeg: 11, kneeDeg: 15, period: 3.2 } as const;

/**
 * Each leg's phase in the stepping cycle (phase 7 review, D-061): a walking order (fore-left,
 * aft-right, fore-right, aft-left), so that the four legs step in turn and never together.
 */
const PHASE: Readonly<Record<Leg, number>> = {
  'fore-left': 0,
  'aft-right': 0.25,
  'fore-right': 0.5,
  'aft-left': 0.75,
};

/** The side of `leg`: +1 for a left one (drawn at -X, as in {@link LEG_REST}), -1 for a right one. */
export const sideOf = (leg: Leg): number => (leg.endsWith('left') ? 1 : -1);
/** The end of the body `leg` is on. */
export const endOf = (leg: Leg): 'fore' | 'aft' => (leg.startsWith('fore') ? 'fore' : 'aft');

/**
 * The hip and knee joints of `leg`: the knee lags a quarter step behind the hip, so the foot
 * swings forward with the knee bent and comes back with it straight (a step, seen from above).
 */
function legJoints(leg: Leg): Record<string, BossJointSpec> {
  const s = sideOf(leg);
  const [hip, knee] = LEG_REST[endOf(leg)];
  const phase = PHASE[leg];
  return {
    [`hip-${leg}`]: {
      x: s * (hip?.[0] ?? 0),
      y: hip?.[1] ?? 0,
      swing: { amplitudeDeg: s * STEP.hipDeg, period: STEP.period, phase },
    },
    [`knee-${leg}`]: {
      x: s * (knee?.[0] ?? 0),
      y: knee?.[1] ?? 0,
      parent: `hip-${leg}`,
      swing: { amplitudeDeg: -s * STEP.kneeDeg, period: STEP.period, phase: phase + 0.25 },
    },
  };
}

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.
 */

/** How far ahead of its foot a leg gun's barrel ends (screen px, towards -Y). */
export const LEG_GUN_REACH = 11.6;
/** The leg guns' barrels: the left fore one's and the left aft one's (mirrored on the right). */
const legGun = (end: 'fore' | 'aft'): Muzzle => {
  const [x, y] = LEG_REST[end][2] ?? [0, 0];
  return [x, y - LEG_GUN_REACH, LEG_HEIGHT.foot];
};
/** The crown emitter on its back: the core's spirals leave from there. */
export const SPIDER_CROWN: Muzzle[] = [[0, -2, 21]];

/** A leg's gun pod, on its knee (the part's centre is its foot). */
function legGunPod(leg: Leg, health: number) {
  const [x, y] = LEG_REST[endOf(leg)][2] ?? [0, 0];
  return fpart(`leg-${leg}`, [sideOf(leg) * x, y], 12, health, { joint: `knee-${leg}` });
}

/** The muzzle of `leg`'s gun. */
const legMuzzles = (leg: Leg): Muzzle[] => {
  const [x, y, h] = legGun(endOf(leg));
  return [[sideOf(leg) * x, y, h]];
};

/**
 * 3-2: a four-legged walker-ship hanging over the canopy, its legs stepping in turn, red neon
 * eyes (P09-R09). The four leg guns fire aimed spreads and shield the core; the egg sac under
 * its abdomen launches Gnat groups (as the Harbour Kraken's container bay); the core spirals.
 */
export const CANOPY_SPIDER: BossDesign = {
  id: 'canopy-spider',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.flower(6, 'red', 'purple'),
  stats: stats({
    id: 'canopy-spider',
    name: 'Canopy Spider',
    size: 5,
    coreRadius: 22,
    coreHealth: 3150,
    points: 14_000,
    groundSpeed: 0.4,
    coreDrop: 1,
    parts: [
      ...LEGS.map((leg) => legGunPod(leg, 1250)),
      fpart('egg-sac', [0, 50], 15, 900, { shields: false }),
    ],
    joints: Object.assign({}, ...LEGS.map(legJoints)) as Record<string, BossJointSpec>,
  }),
  stopFraction: 0.74,
  sway: { amplitude: 30, period: 11 },
  bob: { amplitude: 6, period: 5 },
  launches: [{ from: 'egg-sac', kind: 'gnats', count: 3, every: 7, first: 3 }],
  guns: {
    core: { ring: SPIDER_CROWN },
    ...Object.fromEntries(LEGS.map((leg) => [`leg-${leg}`, { gun: legMuzzles(leg) }])),
  },
  stages: stages(
    LEGS.map((leg, i) => volley.aimed(`leg-${leg}`, 3.4, 3, 12, RED, 1 + 0.85 * i)),
    [
      [volley.ring('core', 1.5, 8, 13, PURPLE, 0.6)],
      [volley.ring('core', 1.4, 9, -15, MAGENTA, 0.5)],
      [volley.ring('core', 1.3, 10, 17, PURPLE, 0.5)],
      [
        volley.ring('core', 1.5, 8, 12, PURPLE, 0.4),
        volley.ring('core', 1.5, 8, -12, MAGENTA, 1.15),
      ],
      [volley.ring('core', 1.2, 11, 19, MAGENTA, 0.4), volley.ring('core', 2.4, 7, -9, PURPLE, 1)],
      [volley.ring('core', 1.1, 12, 9, GREEN, 0.3), volley.ring('core', 1.1, 12, -13, GREEN, 0.85)],
    ],
  ),
};
