import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, cells, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P09-R09, 3-1: the River Leviathan, the River delta's final boss. Offsets in px from the boss's
 * centre, X right and Y up (its nose points down, at -Y). Its head is the core, at the centre;
 * its body trails behind it (+Y) in four segments and a tail, each hinged on the one before
 * (D-061, chained joints). Every hinge swings the same way a little later than the one before,
 * so a wave runs down the body from the head to the tail, as a swimming snake's.
 */

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

const TEAL = bullet('green', 195);
const BLUE = bullet('blue', 205);
const MAGENTA = bullet('magenta', 200);
const PURPLE = bullet('purple', 210);

/** The body's segments, head to tail. */
export const SEGMENTS = [1, 2, 3, 4] as const;
export type Segment = (typeof SEGMENTS)[number];

/**
 * The body (rest pose, straight behind the head): the hinge of each segment (`neck` for the
 * first) and of the tail, along the spine; each segment's middle; the side of its turret's
 * sponson (they alternate, so that none hides right behind the head) and how far out it is.
 */
export const LEVIATHAN_BODY = {
  hinges: [20, 52, 84, 116, 148],
  middles: [36, 68, 100, 132],
  sides: [-1, 1, -1, 1],
  turretOut: 28,
  /** The missile rack's middle, on the tail. */
  rack: 166,
} as const;

/**
 * How each hinge swings (D-061): degrees either way, growing towards the tail, all over one
 * `period`, each `lag` of a period behind the one before (the wave running down the body).
 */
const SWAY = { degrees: [8, 9, 10, 12, 14], period: 4.8, lag: 0.11 } as const;

/** The joint ids, head to tail: the neck, three spine hinges, the tail's. */
export const LEVIATHAN_JOINTS = ['neck', 'spine-1', 'spine-2', 'spine-3', 'tail'] as const;

/** The chain of joints, each hanging on the one before it. */
function spine(): Record<string, BossJointSpec> {
  const joints: Record<string, BossJointSpec> = {};
  LEVIATHAN_JOINTS.forEach((id, i) => {
    const parent = LEVIATHAN_JOINTS[i - 1];
    joints[id] = {
      x: 0,
      y: LEVIATHAN_BODY.hinges[i] ?? 0,
      ...(parent === undefined ? {} : { parent }),
      swing: {
        amplitudeDeg: SWAY.degrees[i] ?? 0,
        period: SWAY.period,
        phase: 1 - SWAY.lag * i,
      },
    };
  });
  return joints;
}

/** Where segment `k`'s turret sits, at rest: on its sponson, out to one side. */
export function turretAt(k: Segment): [x: number, y: number] {
  const i = k - 1;
  return [
    (LEVIATHAN_BODY.sides[i] ?? 1) * LEVIATHAN_BODY.turretOut,
    LEVIATHAN_BODY.middles[i] ?? 0,
  ];
}

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/**
 * The ring emitter on top of each segment turret, on its axis: it stays put as the turret turns
 * with its rings (D-060), and its rings fire from it (its `gun`, as rings fall back on it).
 */
export const TURRET_EMITTER_HEIGHT = 15.5;
export const turretEmitter = (k: Segment): Muzzle[] => [[...turretAt(k), TURRET_EMITTER_HEIGHT]];
/** The head's laser lens, at the tip of its snout. */
export const LEVIATHAN_LENS: Muzzle[] = [[0, -31, 5]];
/** The head's twin fang guns either side of its jaw (the core's aimed shots and fans). */
export const LEVIATHAN_FANGS: Muzzle[] = twin(9, -24, 3.5);
/** The crest emitter on the top of its head (the core's last-stage spirals). */
export const LEVIATHAN_CREST: Muzzle[] = [[0, 2, 19]];
/** The missile rack's cells on the tail, two by two. */
export const LEVIATHAN_RACK: Muzzle[] = cells([-4.5, 4.5], [160, 170], 10);

/**
 * 3-1: a segmented serpent-ship 6 L long, its body swaying from side to side, teal neon along
 * its spine (P09-R09). Its four segments' turrets fire rings in turn and shield the core; the
 * tail's rack fires homing missiles; the head fires its laser at every stage, with something
 * new beside it. The ground slows (×0.5).
 */
export const RIVER_LEVIATHAN: BossDesign = {
  id: 'river-leviathan',
  /** Angry after each destroyed part (D-063), heat 5 (P09-R10). */
  rage: rage.spirals(5, 'blue', 'green'),
  stats: stats({
    id: 'river-leviathan',
    name: 'River Leviathan',
    size: 6,
    coreRadius: 22,
    coreHealth: 2500,
    points: 20_000,
    groundSpeed: 0.5,
    coreDrop: 1,
    parts: [
      ...SEGMENTS.map((k) =>
        fpart(`segment-${String(k)}`, turretAt(k), 14, 900, {
          joint: LEVIATHAN_JOINTS[k - 1] ?? 'neck',
        }),
      ),
      fpart('tail-rack', [0, LEVIATHAN_BODY.rack], 13, 700, { shields: false, joint: 'tail' }),
    ],
    joints: spine(),
  }),
  // Stops high enough to be in place within 6.5 s (P07-R05), its tail still on screen.
  stopFraction: 0.72,
  sway: { amplitude: 55, period: 9.6 },
  bob: { amplitude: 6, period: 4.8 },
  guns: {
    core: { gun: LEVIATHAN_FANGS, laser: LEVIATHAN_LENS, ring: LEVIATHAN_CREST },
    ...Object.fromEntries(
      SEGMENTS.map((k) => [`segment-${String(k)}`, { gun: turretEmitter(k), turret: turretAt(k) }]),
    ),
    'tail-rack': { missile: LEVIATHAN_RACK },
  },
  stages: stages(
    [
      // The segments' rings in turn, from the neck to the tail, one a second.
      ...SEGMENTS.map((k) => volley.ring(`segment-${String(k)}`, 4.4, 8, 11, TEAL, 1.1 * k)),
      volley.missiles('tail-rack', 6, 2, 30, 3),
    ],
    [
      [volley.laser('core', 7, 1.5, 4)],
      [volley.laser('core', 6.5, 1.5, 2), volley.aimed('core', 2.8, 3, 12, MAGENTA, 1)],
      [volley.laser('core', 6, 1.5, 2), volley.fan('core', 2.6, 5, 14, MAGENTA, 0.8)],
      [volley.laser('core', 6, 1.6, 2), volley.burst('core', 2.6, 4, 0.14, BLUE, 0.6)],
      [volley.laser('core', 5.5, 1.6, 2), volley.fan('core', 2.4, 7, 12, MAGENTA, 0.6)],
      // Alone: two spirals turning opposite ways from its crest, under the laser.
      [
        volley.laser('core', 5, 1.6, 1.5),
        volley.ring('core', 0.5, 4, 19, BLUE, 0.4),
        volley.ring('core', 0.5, 4, -23, PURPLE, 0.65),
      ],
    ],
  ),
};
