import type { BossJointSpec } from '../../core/entities/boss-joint';
import type { EnemyPartSpec } from '../../core/entities/jointed-enemy';
import { ENEMY_UNIT } from './enemies';

/**
 * Tunables of the elite enemies (P05-R19 to P05-R23), in the style of `enemies.ts`: distances
 * in logical pixels, speeds in px/s, times in seconds, angles in degrees; `...Fraction` heights
 * are fractions of the playfield height from its bottom. Their moving parts (P05-R13) are given
 * as drawn facing down the screen at rest, from the enemy's centre (X right, Y up); `aim` is in
 * radians, clockwise on screen from the nose. Muzzles as in `enemies.ts` (x, y, height).
 */

type Point = readonly [x: number, y: number];
type Muzzle = readonly [x: number, y: number, height: number];

const DEG = Math.PI / 180;

/** Hit radius relative to half the model size (GD-21), as for the first kinds. */
const HITBOX = 0.85;

/** Hit radius of an enemy `size` L across. */
const radius = (size: number): number => (size * ENEMY_UNIT * HITBOX) / 2;

/** Enemy bullets: colourful glowing balls (GD-43), styles of `enemy-look.ts`. */
const bullet = (style: string, speed: number) => ({ speed, radius: 4, style });

/** The point `length` px from `from` along `aim` (radians clockwise from the nose, facing down). */
export function alongAim([x, y]: Point, aim: number, length: number): [number, number] {
  return [x - Math.sin(aim) * length, y - Math.cos(aim) * length];
}

/** The aim (radians clockwise from the nose) from `from` towards `to`. */
const aimFrom = ([fx, fy]: Point, [tx, ty]: Point): number => Math.atan2(fx - tx, fy - ty);

/** `count` points `r` from the centre, evenly all around, the first one ahead of the nose. */
const around = (count: number, r: number, height: number): Muzzle[] =>
  Array.from({ length: count }, (_, k): Muzzle => {
    const a = (2 * Math.PI * k) / count;
    return [r * Math.sin(a), -r * Math.cos(a), height];
  });

/** P05-R19: the Hydra's necks: each a joint at the hull's front, its head at the end. */
const HYDRA_NECKS = [
  { side: 'left', pivot: [-8, -5], head: [-19, -21] },
  { side: 'middle', pivot: [0, -7], head: [0, -25] },
  { side: 'right', pivot: [8, -5], head: [19, -21] },
] as const;
const HYDRA_HEAD = { radius: 6.5, health: 50, eyeAhead: 5, eyeHeight: 3 } as const;

const hydraHeads = HYDRA_NECKS.map(({ side, pivot, head }, i) => {
  const aim = aimFrom(pivot, head);
  const eye = alongAim(head, aim, HYDRA_HEAD.eyeAhead);
  return {
    id: `head-${side}`,
    joint: `neck-${side}`,
    pivot,
    head,
    aim,
    /** Its eye, where its bullets leave from. */
    muzzle: [eye[0], eye[1], HYDRA_HEAD.eyeHeight] as Muzzle,
    /** The necks sway out of step. */
    phase: i / HYDRA_NECKS.length,
  };
});

/** P05-R21: the Scissor's arms: hinged at the shoulders, 25° out from straight down at rest. */
const SCISSOR_ARM = { length: 30, spread: 25, partAt: 16, height: 2 } as const;
const scissorArms = ([-1, 1] as const).map((s) => {
  const pivot: Point = [s * 6, 2];
  // Right arm (s = 1): pointing down and to the right, anticlockwise from the nose.
  const aim = -s * SCISSOR_ARM.spread * DEG;
  const [cx, cy] = alongAim(pivot, aim, SCISSOR_ARM.partAt);
  const [tx, ty] = alongAim(pivot, aim, SCISSOR_ARM.length);
  return {
    id: s < 0 ? 'arm-left' : 'arm-right',
    joint: s < 0 ? 'shoulder-left' : 'shoulder-right',
    pivot,
    centre: [cx, cy] as Point,
    aim,
    /** Its emitter at the tip, where its laser leaves from. */
    muzzle: [tx, ty, SCISSOR_ARM.height] as Muzzle,
    /** Its swing turns it inward first (clockwise for the right arm). */
    phase: s < 0 ? 0.5 : 0,
  };
});

/** P05-R22: the Juggernaut's shoulder cannons and front plates. */
const juggernautCannons = ([-1, 1] as const).map((s) => ({
  id: s < 0 ? 'cannon-left' : 'cannon-right',
  joint: s < 0 ? 'shoulder-left' : 'shoulder-right',
  pivot: [s * 22, 3] as Point,
  centre: [s * 28, -3] as Point,
  /** The tip of its barrel: its bursts leave from there, along it. */
  muzzle: [s * 28, -16, 3] as Muzzle,
  phase: s < 0 ? 0.5 : 0,
}));
const JUGGERNAUT_PLATES = ([-1, 1] as const).map((s) => ({
  id: s < 0 ? 'plate-left' : 'plate-right',
  x: s * 10,
  y: -17,
}));

/** P05-R20: the Orbiter's drones, evenly around its core. */
const ORBITER_DRONE = { orbit: 15.5, radius: 5.5, health: 40, muzzleOut: 4.5, height: 2 } as const;
const orbiterDrones = [0, 1, 2].map((i) => {
  const a = (2 * Math.PI * i) / 3;
  const [sx, sy] = [Math.sin(a), Math.cos(a)];
  const out = ORBITER_DRONE.orbit + ORBITER_DRONE.muzzleOut;
  return {
    id: `drone-${String(i)}`,
    centre: [ORBITER_DRONE.orbit * sx, ORBITER_DRONE.orbit * sy] as Point,
    /** It faces out from the core. */
    aim: a - Math.PI,
    muzzle: [out * sx, out * sy, ORBITER_DRONE.height] as Muzzle,
    /** The drones fire in turn, not all at once. */
    firstShot: 1 + (2 * i) / 3,
  };
});

const swing = (amplitudeDeg: number, period: number, phase: number) => ({
  amplitudeDeg,
  period,
  phase,
});

export const ELITE_CONFIG = {
  hydra: {
    stats: { model: 'hydra', radius: 17, health: 220, points: 700 },
    size: 1.6,
    entrySpeed: 75,
    /** It stops in the upper third. */
    stopFraction: 0.74,
    stay: 7,
    exitSpeed: 95,
    /** One head fires every `headFireInterval`, in turn; the first after `firstShot`. */
    headFireInterval: 0.5,
    firstShot: 0.4,
    bullet: bullet('green', 200),
    heads: hydraHeads,
    design: {
      joints: Object.fromEntries(
        hydraHeads.map((h): [string, BossJointSpec] => [
          h.joint,
          { x: h.pivot[0], y: h.pivot[1], swing: swing(16, 2.6, h.phase) },
        ]),
      ),
      parts: hydraHeads.map((h): EnemyPartSpec => ({
        id: h.id,
        x: h.head[0],
        y: h.head[1],
        radius: HYDRA_HEAD.radius,
        health: HYDRA_HEAD.health,
        joint: h.joint,
        aim: h.aim,
      })),
    },
    xRange: [0.3, 0.7],
  },
  orbiter: {
    stats: { model: 'orbiter', radius: 12, health: 160, points: 650 },
    size: 1.1,
    /** Radius of its spherical core. */
    coreRadius: 12,
    entrySpeed: 120,
    /** It stops at a random height between these (the upper half). */
    stopRange: [0.6, 0.78],
    stay: 8,
    exitSpeed: 140,
    /** How fast the drones orbit, degrees per second, clockwise on screen. */
    spin: 100,
    ringInterval: 3,
    firstRing: 0.8,
    ringCount: 12,
    ringBullet: bullet('orange', 150),
    /** Its equator: each bullet of a ring leaves from the point facing its way. */
    ringMuzzles: around(12, 12.5, 0),
    droneFireInterval: 2,
    droneBullet: bullet('orange', 200),
    drones: orbiterDrones,
    design: {
      parts: orbiterDrones.map((d): EnemyPartSpec => ({
        id: d.id,
        x: d.centre[0],
        y: d.centre[1],
        radius: ORBITER_DRONE.radius,
        health: ORBITER_DRONE.health,
        orbits: true,
        aim: d.aim,
      })),
    },
    xRange: [0.25, 0.75],
  },
  scissor: {
    stats: { model: 'scissor', radius: 14, health: 240, points: 800 },
    size: 1.8,
    entrySpeed: 160,
    /** It slows down over this distance before its stop point. */
    brakeDistance: 60,
    stopFraction: 0.8,
    exitSpeed: 190,
    /** Each arm's laser: 1 s of warning line, then 2 s of beam while the arms close. */
    laser: { warningSeconds: 1, firingSeconds: 2, width: 9, style: 'lancer' },
    /** How far each arm swings inward while its laser fires. */
    sweep: 15,
    arms: scissorArms,
    design: {
      joints: Object.fromEntries(
        scissorArms.map((a): [string, BossJointSpec] => [
          a.joint,
          // A quarter of a period is the firing time: the arm closes by `sweep` (P05-R21).
          { x: a.pivot[0], y: a.pivot[1], swing: swing(15, 8, a.phase) },
        ]),
      ),
      parts: scissorArms.map((a): EnemyPartSpec => ({
        id: a.id,
        x: a.centre[0],
        y: a.centre[1],
        radius: 7,
        health: 70,
        joint: a.joint,
        aim: a.aim,
      })),
    },
    xRange: [0.25, 0.75],
  },
  juggernaut: {
    stats: { model: 'juggernaut', radius: 20, health: 320, points: 1000 },
    size: 2,
    entrySpeed: 55,
    stopFraction: 0.74,
    drift: 60,
    /** Seconds for one left-right drift. */
    driftPeriod: 5,
    stay: 10,
    exitSpeed: 80,
    fireInterval: 2.5,
    firstShot: 1.2,
    spreadCount: 7,
    spreadSpacing: 9,
    bullet: bullet('blue', 185),
    /** The twin cannon on its back turret. */
    muzzles: [
      [-3, -9, 7],
      [3, -9, 7],
    ] as readonly Muzzle[],
    /** Each shoulder cannon fires a burst of `burstCount` along its barrel every interval. */
    cannonInterval: 1.6,
    firstBurst: 0.8,
    burstCount: 3,
    burstGap: 0.12,
    cannonBullet: bullet('blue', 210),
    cannons: juggernautCannons,
    plates: JUGGERNAUT_PLATES,
    design: {
      joints: Object.fromEntries(
        juggernautCannons.map((c): [string, BossJointSpec] => [
          c.joint,
          { x: c.pivot[0], y: c.pivot[1], swing: swing(20, 2.4, c.phase) },
        ]),
      ),
      parts: [
        ...juggernautCannons.map((c): EnemyPartSpec => ({
          id: c.id,
          x: c.centre[0],
          y: c.centre[1],
          radius: 7,
          health: 60,
          joint: c.joint,
        })),
        // While a plate stands, the core cannot be hit (P05-R22).
        ...JUGGERNAUT_PLATES.map((p): EnemyPartSpec => ({
          ...p,
          radius: 9,
          health: 120,
          shields: true,
        })),
      ],
    },
    xRange: [0.3, 0.7],
  },
  hive: {
    stats: { model: 'hive', radius: radius(2) * 0.8, health: 420, points: 900 },
    size: 2,
    speed: 28,
    /** How fast its launch ring turns, degrees per second. */
    ringSpin: 45,
    /** A Wasp from the ring every `launchInterval`, the first after `firstLaunch`. */
    launchInterval: 4,
    firstLaunch: 1.5,
    /** The ring's launch hatch, on the turning ring: Wasps come out of it. */
    port: [0, 14, 9] as Muzzle,
    /** A launched Wasp flies this far down from the hatch before its pause. */
    launchDrop: 55,
    ringInterval: 3,
    firstRing: 1,
    ringCount: 12,
    ringBullet: bullet('orange', 150),
    /** Twelve vents around its rim: each bullet of a ring leaves from the one facing its way. */
    ringMuzzles: around(12, 32, 1),
    /** It stops launching and firing below this height, too close to the player. */
    lastFraction: 0.3,
    design: { parts: [] },
    xRange: [0.3, 0.7],
  },
} as const;
