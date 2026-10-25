import type { Muzzle } from '../../../core/entities/muzzle';
import { bullet, mirror, part, stages, stats, twin, volley, type BossDesign } from './boss-kit';

/*
 * The World 1 mini bosses (P07-R05): 2 or 3 destroyable parts each. Offsets in px from the
 * boss's centre, X right and Y up (its nose points down, at -Y). The stage patterns are the
 * agent's design (P07-R04): the parts fire the same while they stand, the core fires something
 * new at every stage, and the last stage (only the core left) a ring or spiral used before by
 * no stage of that boss. Health values are tuned so that a player with guns at level 3 always
 * on target needs the fight times of P07-R10.
 */

const ORANGE = bullet('orange', 170);
const RED = bullet('red', 190);
const BLUE = bullet('blue', 185);
const GREEN = bullet('green', 180);
const PURPLE = bullet('purple', 195);

/*
 * The guns' muzzles (phase 7 review): the tips of the barrels their models draw, from the boss's
 * centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).
 */

/** The Reef Warden's right side cannon's two barrels. */
const CANNON: Muzzle[] = [
  [38.5, -23.2, 7.9],
  [33.5, -23.2, 7.9],
];

/** 1-1: a wide hover-gunboat with a cyan ring under its rim; two side cannons shield the core. */
export const REEF_WARDEN: BossDesign = {
  id: 'reef-warden',
  stats: stats({
    id: 'reef-warden',
    name: 'Reef Warden',
    size: 3,
    coreRadius: 20,
    coreHealth: 960,
    points: 3000,
    groundSpeed: 0.5,
    parts: [part('cannon-left', [-36, -2], 14, 620), part('cannon-right', [36, -2], 14, 620)],
  }),
  stopFraction: 0.72,
  sway: { amplitude: 70, period: 7 },
  bob: { amplitude: 8, period: 3.5 },
  guns: {
    core: { gun: [[0, -40.5, 5]], turret: [0, -27] },
    'cannon-left': { gun: mirror(CANNON), turret: [-36, -2] },
    'cannon-right': { gun: CANNON, turret: [36, -2] },
  },
  stages: stages(
    [
      volley.burst('cannon-left', 2.6, 3, 0.18, RED, 1),
      volley.burst('cannon-right', 2.6, 3, 0.18, RED, 2.3),
    ],
    [
      [volley.fan('core', 3.2, 3, 18, ORANGE, 1.8)],
      [volley.fan('core', 2.2, 5, 14, ORANGE, 0.6)],
      [volley.ring('core', 1.8, 8, 11, ORANGE, 0.4)],
    ],
  ),
};

/** 1-2: an armoured flying barge; its front plate shields the core, two mortars lob big bullets. */
export const BREAKWATER: BossDesign = {
  id: 'breakwater',
  stats: stats({
    id: 'breakwater',
    name: 'Breakwater',
    size: 3,
    coreRadius: 18,
    coreHealth: 930,
    points: 3500,
    groundSpeed: 0.4,
    parts: [
      part('ram-plate', [0, -34], 18, 810),
      part('mortar-left', [-34, 12], 13, 430, { shields: false }),
      part('mortar-right', [34, 12], 13, 430, { shields: false }),
    ],
  }),
  stopFraction: 0.72,
  sway: { amplitude: 60, period: 8 },
  bob: { amplitude: 6, period: 4 },
  guns: {
    core: { gun: twin(1.5, -33.3, 6.4), turret: [0, -21] },
    'mortar-left': { gun: [[-34, -1.5, 17.2]], turret: [-34, 12] },
    'mortar-right': { gun: [[34, -1.5, 17.2]], turret: [34, 12] },
  },
  stages: stages(
    [
      volley.aimed('mortar-left', 2.4, 1, 0, bullet('orange', 110, 7), 1.2),
      volley.aimed('mortar-right', 2.4, 1, 0, bullet('orange', 110, 7), 2.4),
    ],
    [
      [volley.fan('core', 3, 3, 16, RED, 1.6)],
      [volley.aimed('core', 2.4, 3, 12, RED, 0.6)],
      [volley.burst('core', 2.2, 4, 0.15, RED, 0.6)],
      [volley.ring('core', 1.7, 10, 9, RED, 0.4)],
    ],
  ),
};

/** 1-3: a gyro gunship; three blade pods on its turning ring fire spirals and shield the core. */
export const DUST_DEVIL: BossDesign = {
  id: 'dust-devil',
  stats: stats({
    id: 'dust-devil',
    name: 'Dust Devil',
    size: 3,
    coreRadius: 18,
    coreHealth: 1230,
    points: 4000,
    groundSpeed: 0.5,
    parts: [
      part('blade-1', [0, -40], 14, 620, { orbits: true }),
      part('blade-2', [34.6, 20], 14, 620, { orbits: true }),
      part('blade-3', [-34.6, 20], 14, 620, { orbits: true }),
    ],
  }),
  stopFraction: 0.72,
  sway: { amplitude: 60, period: 9 },
  bob: { amplitude: 10, period: 3 },
  spinRate: 0.7,
  guns: {
    core: { gun: [[0, 0, 10]] },
    'blade-1': {
      gun: [
        [16.8, -38.6, 0.3],
        [-16.8, -40, 0.3],
      ],
    },
    'blade-2': {
      gun: [
        [25, 33.8, 0.3],
        [43, 5.5, 0.3],
      ],
    },
    'blade-3': {
      gun: [
        [-41.8, 4.8, 0.3],
        [-26.2, 34.5, 0.3],
      ],
    },
  },
  stages: stages(
    [
      volley.ring('blade-1', 1, 2, 23, GREEN, 0.4),
      volley.ring('blade-2', 1, 2, 23, GREEN, 0.73),
      volley.ring('blade-3', 1, 2, 23, GREEN, 1.06),
    ],
    [
      [volley.aimed('core', 3, 1, 0, ORANGE, 1.5)],
      [volley.aimed('core', 2.6, 3, 12, ORANGE, 0.8)],
      [volley.burst('core', 2.4, 4, 0.14, ORANGE, 0.6)],
      [volley.ring('core', 1.5, 12, 15, ORANGE, 0.4)],
    ],
  ),
};

/**
 * 1-4: a gunship with a tail arched over its back, its stinger hanging in front of the core (so
 * shots from below reach it); claws spread, the stinger fires a laser.
 */
export const SCORPION: BossDesign = {
  id: 'scorpion',
  stats: stats({
    id: 'scorpion',
    name: 'Scorpion',
    size: 3.5,
    coreRadius: 18,
    coreHealth: 1470,
    points: 4500,
    groundSpeed: 0.5,
    parts: [
      part('claw-left', [-42, -24], 14, 730),
      part('claw-right', [42, -24], 14, 730),
      part('stinger', [0, -34], 13, 730),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 60, period: 7.5 },
  bob: { amplitude: 8, period: 3.2 },
  guns: {
    core: { gun: [[0, -26, 2]] },
    'claw-left': { gun: [[-38.8, -41.3, 5.5]] },
    'claw-right': { gun: [[39.3, -38.8, 5.5]] },
    stinger: { laser: [[0, -49.3, 8.9]] },
  },
  stages: stages(
    [
      volley.aimed('claw-left', 2.2, 3, 10, BLUE, 1),
      volley.aimed('claw-right', 2.2, 3, 10, BLUE, 2.1),
      volley.laser('stinger', 5.5, 1.4, 2.5),
    ],
    [
      [volley.aimed('core', 3, 1, 0, PURPLE, 1.5)],
      [volley.ring('core', 2.4, 6, 0, PURPLE, 0.8)],
      [volley.ring('core', 2, 8, 10, PURPLE, 0.6)],
      [volley.ring('core', 1.4, 12, 8, PURPLE, 0.4), volley.aimed('core', 2.4, 1, 0, BLUE, 1)],
    ],
  ),
};

/** 1-5: a twin-hull police interceptor; two hull guns and a drone bay at its nose shield the core. */
export const SENTINEL: BossDesign = {
  id: 'sentinel',
  stats: stats({
    id: 'sentinel',
    name: 'Sentinel',
    size: 3.5,
    coreRadius: 18,
    coreHealth: 1570,
    points: 5000,
    groundSpeed: 0.6,
    parts: [
      part('gun-left', [-40, -8], 13, 780),
      part('gun-right', [40, -8], 13, 780),
      part('drone-bay', [0, -36], 15, 780),
    ],
  }),
  stopFraction: 0.74,
  sway: { amplitude: 70, period: 6.5 },
  bob: { amplitude: 8, period: 3 },
  launches: [{ from: 'drone-bay', kind: 'hornets', count: 2, every: 5.5, first: 3 }],
  guns: {
    core: { gun: twin(15, -12.5, 1) },
    'gun-left': { gun: twin(-40, -24.6, 7.1, 1.8), turret: [-40, -8] },
    'gun-right': { gun: twin(40, -24.6, 7.1, 1.8), turret: [40, -8] },
  },
  stages: stages(
    [
      volley.aimed('gun-left', 1.7, 2, 8, BLUE, 0.8),
      volley.aimed('gun-right', 1.7, 2, 8, RED, 1.65),
    ],
    [
      [volley.fan('core', 2.8, 3, 16, BLUE, 1.4)],
      [volley.fan('core', 2.4, 5, 14, RED, 0.8)],
      [volley.fan('core', 2.2, 7, 12, BLUE, 0.6)],
      [volley.ring('core', 1.3, 14, 7, RED, 0.4), volley.fan('core', 2.6, 5, 14, BLUE, 1)],
    ],
  ),
};
