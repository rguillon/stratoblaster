/**
 * Data-only description of player weapons. Positions and distances are in logical pixels,
 * with X to the right and Y up (forward); angles are in degrees from forward, positive to the
 * right.
 */

/** One stream of shots at a weapon level: where they leave the ship and which way they go. */
export interface ShotStream {
  /** Sideways offset from the ship's muzzle. */
  readonly offsetX: number;
  readonly angleDeg: number;
}

/** A weapon that fires projectiles (bullets, missiles...) in streams. */
export interface ProjectileWeaponDefinition {
  readonly kind: 'projectile';
  /** Stable identifier, also the key of the weapon's visuals in the game view. */
  readonly id: string;
  readonly name: string;
  /** Where the streams start: the ship's muzzle (its nose) or its centre. */
  readonly launchPoint: 'muzzle' | 'center';
  /** Shots per second in each stream. */
  readonly shotsPerSecond: number;
  readonly launchSpeed: number;
  /** Constant acceleration along the heading, px/s² (0: constant velocity). */
  readonly acceleration: number;
  /** Speed cap, px/s; ignored when `acceleration` is 0. */
  readonly maxSpeed: number;
  /** Turn rate towards the closest target, degrees per second (0: flies straight). */
  readonly homingTurnRateDeg: number;
  /** A homing shot only sees targets within this distance of it, px (phase 5 review). */
  readonly homingRange: number;
  /** Hit radius of a shot. */
  readonly radius: number;
  readonly damage: number;
  /** 0: damages the target hit only; above 0: every target within this distance of the impact. */
  readonly blastRadius: number;
  /** `levels[i]` lists the streams fired at level `i + 1`. */
  readonly levels: readonly (readonly ShotStream[])[];
}

/** One level of a beam weapon. */
export interface BeamLevel {
  readonly damagePerSecond: number;
  readonly width: number;
}

/**
 * A continuous beam fired straight ahead. At level 1 it stops at the first target it hits;
 * above, it goes through the target and continues one level lower.
 */
export interface BeamWeaponDefinition {
  readonly kind: 'beam';
  readonly id: string;
  readonly name: string;
  /** `levels[i]` is level `i + 1`. */
  readonly levels: readonly BeamLevel[];
}

export type WeaponDefinition = ProjectileWeaponDefinition | BeamWeaponDefinition;

function validateProjectile(weapon: ProjectileWeaponDefinition): void {
  const positive = ['shotsPerSecond', 'launchSpeed', 'radius', 'damage'] as const;
  for (const key of positive) {
    if (!(weapon[key] > 0)) throw new Error(`Weapon "${weapon.id}": ${key} must be positive`);
  }
  const nonNegative = ['acceleration', 'homingTurnRateDeg', 'homingRange', 'blastRadius'] as const;
  for (const key of nonNegative) {
    if (!(weapon[key] >= 0)) throw new Error(`Weapon "${weapon.id}": ${key} must be >= 0`);
  }
  if (weapon.acceleration > 0 && !(weapon.maxSpeed >= weapon.launchSpeed)) {
    throw new Error(`Weapon "${weapon.id}": maxSpeed must be >= launchSpeed`);
  }
  if (weapon.levels.some((streams) => streams.length === 0)) {
    throw new Error(`Weapon "${weapon.id}": every level needs at least one stream`);
  }
}

function validateBeam(weapon: BeamWeaponDefinition): void {
  for (const level of weapon.levels) {
    if (!(level.damagePerSecond > 0) || !(level.width > 0)) {
      throw new Error(`Weapon "${weapon.id}": damage and width must be positive`);
    }
  }
}

/** Throws a descriptive error if the weapons have duplicate ids, no levels or invalid values. */
export function validateWeapons(weapons: readonly WeaponDefinition[]): void {
  const ids = new Set<string>();
  for (const weapon of weapons) {
    if (ids.has(weapon.id)) throw new Error(`Duplicate weapon id "${weapon.id}"`);
    ids.add(weapon.id);
    if (weapon.levels.length === 0) throw new Error(`Weapon "${weapon.id}" has no level`);
    if (weapon.kind === 'projectile') validateProjectile(weapon);
    else validateBeam(weapon);
  }
}

/** Number of levels of a weapon. */
export function weaponLevelCount(weapon: WeaponDefinition): number {
  return weapon.levels.length;
}

/** Returns the weapon with the given id, or throws if there is none. */
export function findWeapon(weapons: readonly WeaponDefinition[], id: string): WeaponDefinition {
  const weapon = weapons.find((w) => w.id === id);
  if (!weapon) throw new Error(`Unknown weapon "${id}"`);
  return weapon;
}
