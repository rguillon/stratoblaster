import type { BossJointSpec } from '../../../../core/entities/boss-joint';
import type { Muzzle } from '../../../../core/entities/muzzle';
import { bullet, part, stages, stats, twin, volley, type BossDesign } from '../boss-kit';
import { rage } from '../boss-rage';

/*
 * P08-R10, 2-2: the Harbour Kraken, the final boss of the Fjords. Offsets in px from the boss's
 * centre, X right and Y up (its nose points down, at -Y). Its four crane arms swing at the
 * shoulder and the elbow (D-061), each out of step with the others.
 */

const RED = bullet('red', 190);
const MAGENTA = bullet('magenta', 185);
const ORANGE = bullet('orange', 175);

/** A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`). */
const fpart = (...[id, at, radius, health, options = {}]: Parameters<typeof part>) =>
  part(id, at, radius, health, { drop: 0.6, ...options });

/** The cranes, by id: `fore` at the bow, `aft` at the stern, either side. */
type Crane = `${'fore' | 'aft'}-${'left' | 'right'}`;

/**
 * Where a left crane (at -X) turns and holds its grab cannon, as drawn at rest: its shoulder
 * (on its pedestal), its elbow and its grab's centre. The right ones mirror them.
 */
export const CRANE_REST: Readonly<
  Record<'fore' | 'aft', readonly (readonly [x: number, y: number])[]>
> = {
  fore: [
    [-28, -26],
    [-50, -34],
    [-70, -44],
  ],
  aft: [
    [-28, 22],
    [-52, 27],
    [-72, 34],
  ],
};

/**
 * How each crane swings (phase 7 review, D-061): degrees and seconds at the shoulder and the
 * elbow, and its phase, so that the four arms never move together.
 */
const SWING: Readonly<Record<Crane, readonly [shoulder: number, elbow: number, phase: number]>> = {
  'fore-left': [10, 18, 0],
  'fore-right': [10, 18, 0.31],
  'aft-left': [9, 16, 0.58],
  'aft-right': [9, 16, 0.83],
};

/** The shoulder and elbow joints of `crane`. */
function craneJoints(crane: Crane): Record<string, BossJointSpec> {
  const [end, side] = crane.split('-') as ['fore' | 'aft', 'left' | 'right'];
  const s = side === 'left' ? 1 : -1;
  const [shoulder, elbow] = CRANE_REST[end];
  const [a, b, phase] = SWING[crane];
  return {
    [`shoulder-${crane}`]: {
      x: s * (shoulder?.[0] ?? 0),
      y: shoulder?.[1] ?? 0,
      swing: { amplitudeDeg: s * a, period: 5.2, phase },
    },
    [`elbow-${crane}`]: {
      x: s * (elbow?.[0] ?? 0),
      y: elbow?.[1] ?? 0,
      parent: `shoulder-${crane}`,
      swing: { amplitudeDeg: -s * b, period: 3.7, phase: phase + 0.2 },
    },
  };
}

/** The cranes in the order of their parts. */
export const CRANES: readonly Crane[] = ['fore-left', 'fore-right', 'aft-left', 'aft-right'];

/** A crane's grab cannon, on its elbow (the part's centre is its grab's). */
function grab(crane: Crane, health: number) {
  const [end, side] = crane.split('-') as ['fore' | 'aft', 'left' | 'right'];
  const [x, y] = CRANE_REST[end][2] ?? [0, 0];
  return fpart(`crane-${crane}`, [side === 'left' ? x : -x, y], 13, health, {
    joint: `elbow-${crane}`,
  });
}

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.
 */

/** The grab cannons' barrels: the left fore one and the left aft one (mirrored on the right). */
const GRAB_FORE: Muzzle = [-70, -59.82, 4];
const GRAB_AFT: Muzzle = [-72, 18.18, 4];
/** The bow's laser emitter, and the twin guns either side of it. */
const BOW_LASER: Muzzle = [0, -78.4, 6];
const BOW_GUNS = twin(9, -67.68, 9.5);

/** The left crane's muzzle `m`, on `side`. */
const sided = (m: Muzzle, side: number): Muzzle[] => [[side * m[0], m[1], m[2]]];

/**
 * 2-2: a cargo crane-ship with four crane arms swinging at the shoulder and the elbow, orange
 * neon (P08-R10). The four grab cannons shield the core; the container bay at the stern
 * launches Gnats. The ground stops: the fight is over the harbour.
 */
export const HARBOUR_KRAKEN: BossDesign = {
  id: 'harbour-kraken',
  /** Angry after each destroyed part (phase 7 review). */
  rage: rage.vortex(4, 'orange', 'magenta'),
  stats: stats({
    id: 'harbour-kraken',
    name: 'Harbour Kraken',
    size: 5,
    coreRadius: 22,
    coreHealth: 2700,
    points: 10_500,
    groundSpeed: 0,
    coreDrop: 1,
    parts: [
      ...CRANES.map((crane) => grab(crane, 900)),
      fpart('container-bay', [0, 46], 16, 700, { shields: false }),
    ],
    joints: Object.assign({}, ...CRANES.map(craneJoints)) as Record<string, BossJointSpec>,
  }),
  stopFraction: 0.75,
  sway: { amplitude: 35, period: 10 },
  bob: { amplitude: 6, period: 5 },
  launches: [{ from: 'container-bay', kind: 'gnats', count: 3, every: 7, first: 3 }],
  guns: {
    core: { gun: BOW_GUNS, laser: [BOW_LASER] },
    'crane-fore-left': { gun: sided(GRAB_FORE, 1) },
    'crane-fore-right': { gun: sided(GRAB_FORE, -1) },
    'crane-aft-left': { gun: sided(GRAB_AFT, 1) },
    'crane-aft-right': { gun: sided(GRAB_AFT, -1) },
  },
  stages: stages(
    [
      volley.burst('crane-fore-left', 3, 3, 0.16, RED, 1),
      volley.burst('crane-fore-right', 3, 3, 0.16, RED, 1.75),
      volley.burst('crane-aft-left', 3, 3, 0.16, RED, 2.5),
      volley.burst('crane-aft-right', 3, 3, 0.16, RED, 3.25),
    ],
    [
      [volley.laser('core', 7, 1.5, 4)],
      [volley.laser('core', 6, 1.5, 2), volley.aimed('core', 2.6, 1, 0, MAGENTA, 1)],
      [volley.laser('core', 5.5, 1.5, 2), volley.fan('core', 2.6, 5, 14, MAGENTA, 1)],
      [volley.laser('core', 5.5, 1.6, 2), volley.aimed('core', 2.4, 3, 12, MAGENTA, 0.8)],
      [volley.laser('core', 5, 1.6, 2), volley.fan('core', 2.2, 7, 12, MAGENTA, 0.6)],
      [volley.laser('core', 4.5, 1.6, 1.5), volley.ring('core', 1.4, 14, 9, ORANGE, 0.4)],
    ],
  ),
};
