import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/*
 * P10-R11, 4-2: the Geyser Rig, the final boss of the Ash plains level. Offsets in px from the
 * boss's centre, X right and Y up (its bow points down, at -Y). Its two drill heads hang on arms
 * swinging on their shoulder joints (D-061), out of step, as if boring. The stage patterns are
 * the agent's design (P07-R04): the parts fire the same while they stand, the core fires new fans
 * at every stage, and its last stage (only the core left) sweeping fans used by no earlier stage.
 * Health tuned with the D-055 bot for P10-R12 (fight 90–112.5 s, full health 9 200–10 200).
 */

const RED = bullet('red', 210);
const ORANGE = bullet('orange', 200);
const MAGENTA = bullet('magenta', 205);
const PURPLE = bullet('purple', 195);

/** Where the parts sit (the left ones at -X; the right ones mirror them), at rest. */
export const RIG_DRILL = [-50, -62] as const;
export const RIG_VENT = [-35, 30] as const;
export const RIG_HANGAR = [0, -50] as const;
/** The left drill arm's shoulder joint on the deck (the right one mirrors it). */
export const RIG_SHOULDER = [-30, -26] as const;

/** Heights of a drill arm (model units over the playfield): its shoulder, its drill head. */
export const DRILL_HEIGHT = { shoulder: 12, head: 6 } as const;
/** How far ahead of the drill head's centre its bit ends (screen px, towards -Y). */
export const DRILL_REACH = 28;

/** The boring swing of the arms: degrees either way and seconds of one swing. */
const BORE = { amplitudeDeg: 13, period: 3.6 } as const;

/** The sides, by part id suffix: `left` at -X (as the constants above), `right` mirrored. */
export const RIG_SIDES = ['left', 'right'] as const;
export type RigSide = (typeof RIG_SIDES)[number];
/** +1 for the left side (as drawn in the constants), -1 for the right one. */
export const sideSign = (side: RigSide): number => (side === 'left' ? 1 : -1);

/** The shoulder joint of the `side` drill arm, out of step with the other one. */
function shoulder(side: RigSide): Record<string, BossJointSpec> {
  const s = sideSign(side);
  return {
    [`arm-${side}`]: {
      x: s * RIG_SHOULDER[0],
      y: RIG_SHOULDER[1],
      swing: {
        amplitudeDeg: s * BORE.amplitudeDeg,
        period: BORE.period,
        phase: side === 'left' ? 0 : 0.5,
      },
    },
  };
}

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.
 */

/** The left drill head's gun, on top of its housing, beside the bit. */
export const RIG_DRILL_GUN: Muzzle[] = [[RIG_DRILL[0], RIG_DRILL[1] - 14, DRILL_HEIGHT.head + 8]];
/** The left steam vent's stack top: its spirals leave from there. */
export const RIG_VENT_TOP: Muzzle[] = [[RIG_VENT[0], RIG_VENT[1], 24]];
/** The twin fan guns at the foot of the derrick, on the core's front. */
export const RIG_CORE_GUNS: Muzzle[] = twin(10, -24, 10);

const [DX, DY] = RIG_DRILL;
const [VX, VY] = RIG_VENT;

/** Fans sweeping across the screen and back from the core (its last stage). */
const sweep = (every: number, first: number) =>
  [-30, -15, 0, 15, 30].map((heading, i) =>
    volley.fan('core', every, 5, 9, MAGENTA, first + (every * i) / 5, heading),
  );

/**
 * 4-2: a flying drilling rig, yellow neon (P10-R11): two drill heads on swinging arms fire aimed
 * bursts and, with the two steam vents firing spirals, shield the core; a drone hangar at the bow
 * launches Hornets (as the Dam Breaker's); the core fires fans. The hangar hangs in front of the
 * core, so it can always be shot.
 */
export const GEYSER_RIG: BossDesign = {
  id: 'geyser-rig',
  /** Angry after each destroyed part (phase 7 review, D-063): World 4 goes on from 3-5's heat 9. */
  rage: rage.curtain(11, 'orange', 'red'),
  stats: stats({
    id: 'geyser-rig',
    name: 'Geyser Rig',
    size: 5,
    coreRadius: 22,
    coreHealth: 3900,
    points: 16_000,
    groundSpeed: 0.4,
    coreDrop: 1,
    parts: [
      fpart('drill-left', [DX, DY], 14, 1300, { joint: 'arm-left' }),
      fpart('drill-right', [-DX, DY], 14, 1300, { joint: 'arm-right' }),
      fpart('vent-left', [VX, VY], 13, 1150),
      fpart('vent-right', [-VX, VY], 13, 1150),
      fpart('hangar', [...RIG_HANGAR], 14, 900, { shields: false }),
    ],
    joints: { ...shoulder('left'), ...shoulder('right') },
  }),
  stopFraction: 0.74,
  sway: { amplitude: 30, period: 11 },
  bob: { amplitude: 5, period: 5.5 },
  launches: [{ from: 'hangar', kind: 'hornets', count: 2, every: 7, first: 3.5 }],
  guns: {
    core: { gun: RIG_CORE_GUNS },
    'drill-left': { gun: RIG_DRILL_GUN },
    'drill-right': { gun: mirror(RIG_DRILL_GUN) },
    'vent-left': { ring: RIG_VENT_TOP },
    'vent-right': { ring: mirror(RIG_VENT_TOP) },
  },
  stages: stages(
    [
      volley.burst('drill-left', 3.2, 4, 0.12, RED, 1),
      volley.burst('drill-right', 3.2, 4, 0.12, RED, 2.6),
      // The vents' steam spirals turn opposite ways.
      volley.ring('vent-left', 0.8, 3, 17, ORANGE, 0.6),
      volley.ring('vent-right', 0.8, 3, -17, ORANGE, 1),
    ],
    [
      [volley.fan('core', 2.6, 3, 16, PURPLE, 1.4)],
      [volley.fan('core', 2.4, 5, 14, PURPLE, 0.8)],
      [
        volley.fan('core', 2.6, 4, 12, MAGENTA, 0.8, -18),
        volley.fan('core', 2.6, 4, 12, MAGENTA, 2.1, 18),
      ],
      [volley.fan('core', 2.3, 7, 12, PURPLE, 0.6)],
      [volley.fan('core', 2.4, 9, 10, MAGENTA, 0.6), volley.fan('core', 1.2, 3, 6, RED, 1.2)],
      sweep(3, 0.5),
    ],
  ),
};
