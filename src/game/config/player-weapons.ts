import type {
  BeamWeaponDefinition,
  ProjectileWeaponDefinition,
  ShotStream,
} from '../../core/entities/weapon';

/*
 * Player weapons (GD-30, GD-31: three weapons, five levels each). Logical pixels, Y up,
 * angles in degrees from forward. Values marked "default" were not given by the phase 3
 * spec; they are the agent's proposal (D-015), to be tuned in review.
 */

/** Distance between the two streams of a "dual forward stream" (default). */
const DUAL_SPACING = 12;

const forward: ShotStream = { offsetX: 0, angleDeg: 0 };
const dual: ShotStream[] = [
  { offsetX: -DUAL_SPACING / 2, angleDeg: 0 },
  { offsetX: DUAL_SPACING / 2, angleDeg: 0 },
];
/** Two diagonal streams, symmetric left / right (default reading of "two diagonal streams"). */
const diagonals = (angleDeg: number): ShotStream[] => [
  { offsetX: 0, angleDeg: -angleDeg },
  { offsetX: 0, angleDeg },
];

/**
 * Launch angles of the missile diagonal streams, inner and outer pair. Wider than the spec's
 * 10° / 20° at the reviewer's request (phase 3 review), so the missiles fan out before homing.
 */
const MISSILE_ANGLES = { inner: 25, outer: 45 } as const;

/** P03-R01: neon green bullets, 10 damage each, constant velocity. */
export const BULLET = {
  kind: 'projectile',
  id: 'bullet',
  name: 'Bullet',
  launchPoint: 'muzzle',
  /** Default. */
  shotsPerSecond: 8,
  /** Default. */
  launchSpeed: 600,
  acceleration: 0,
  maxSpeed: 600,
  homingTurnRateDeg: 0,
  /** Default. */
  radius: 4,
  damage: 10,
  blastRadius: 0,
  levels: [
    [forward],
    dual,
    [forward, ...diagonals(10)],
    [...dual, ...diagonals(10)],
    [forward, ...diagonals(10), ...diagonals(20)],
  ],
} as const satisfies ProjectileWeaponDefinition;

/**
 * P03-R02: bright blue laser, more damage per second at each level; above level 1 it goes
 * through a ship and continues one level lower. Damage and widths are defaults.
 */
export const LASER = {
  kind: 'beam',
  id: 'laser',
  name: 'Laser',
  levels: [
    { damagePerSecond: 40, width: 4 },
    { damagePerSecond: 60, width: 6 },
    { damagePerSecond: 85, width: 8 },
    { damagePerSecond: 115, width: 10 },
    { damagePerSecond: 150, width: 12 },
  ],
} as const satisfies BeamWeaponDefinition;

/**
 * P03-R03: missiles with constant acceleration that home on the closest enemy; 8 damage to
 * everything within 10 px of the impact; 4 missiles per second per stream.
 */
export const MISSILE = {
  kind: 'projectile',
  id: 'missile',
  name: 'Missile',
  /** From the centre of the ship, drawn under it (phase 3 review). */
  launchPoint: 'center',
  shotsPerSecond: 4,
  /** Default. */
  launchSpeed: 150,
  /** Default. */
  acceleration: 600,
  /** Default. */
  maxSpeed: 700,
  /** Default. */
  homingTurnRateDeg: 180,
  /** Default. */
  radius: 3,
  damage: 8,
  blastRadius: 10,
  levels: [
    [forward],
    diagonals(MISSILE_ANGLES.inner),
    [forward, ...diagonals(MISSILE_ANGLES.inner)],
    [...diagonals(MISSILE_ANGLES.inner), ...diagonals(MISSILE_ANGLES.outer)],
    [forward, ...diagonals(MISSILE_ANGLES.inner), ...diagonals(MISSILE_ANGLES.outer)],
  ],
} as const satisfies ProjectileWeaponDefinition;

/** Every player ship can fire every weapon (GD-30). */
export const PLAYER_WEAPONS = [BULLET, LASER, MISSILE] as const;
