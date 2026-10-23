import type {
  BeamWeaponDefinition,
  ProjectileWeaponDefinition,
} from '../../src/core/entities/weapon';

/** A projectile weapon for engine tests: straight, constant speed, direct damage. */
export function testGun(
  overrides: Partial<ProjectileWeaponDefinition> = {},
): ProjectileWeaponDefinition {
  return {
    kind: 'projectile',
    id: 'gun',
    name: 'Gun',
    launchPoint: 'muzzle',
    shotsPerSecond: 10,
    launchSpeed: 100,
    acceleration: 0,
    maxSpeed: 100,
    homingTurnRateDeg: 0,
    radius: 2,
    damage: 5,
    blastRadius: 0,
    levels: [
      [{ offsetX: 0, angleDeg: 0 }],
      [
        { offsetX: -4, angleDeg: 0 },
        { offsetX: 4, angleDeg: 0 },
      ],
    ],
    ...overrides,
  };
}

/** A beam weapon for engine tests: three levels. */
export function testBeam(): BeamWeaponDefinition {
  return {
    kind: 'beam',
    id: 'beam',
    name: 'Beam',
    levels: [
      { damagePerSecond: 10, width: 2 },
      { damagePerSecond: 20, width: 4 },
      { damagePerSecond: 30, width: 6 },
    ],
  };
}
