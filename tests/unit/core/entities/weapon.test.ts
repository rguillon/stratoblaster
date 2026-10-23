import { describe, expect, it } from 'vitest';
import {
  findWeapon,
  validateWeapons,
  weaponLevelCount,
} from '../../../../src/core/entities/weapon';
import { testBeam, testGun } from '../../../helpers/test-weapons';

describe('validateWeapons', () => {
  it('accepts valid projectile and beam weapons', () => {
    expect(() => {
      validateWeapons([testGun(), testBeam()]);
    }).not.toThrow();
  });

  it('rejects duplicate ids and weapons without levels', () => {
    expect(() => {
      validateWeapons([testGun(), testGun()]);
    }).toThrow(/Duplicate/);
    expect(() => {
      validateWeapons([testGun({ levels: [] })]);
    }).toThrow(/no level/);
  });

  it('rejects invalid projectile values', () => {
    expect(() => {
      validateWeapons([testGun({ damage: 0 })]);
    }).toThrow(/damage/);
    expect(() => {
      validateWeapons([testGun({ blastRadius: -1 })]);
    }).toThrow(/blastRadius/);
    expect(() => {
      validateWeapons([testGun({ acceleration: 10, maxSpeed: 50 })]);
    }).toThrow(/maxSpeed/);
    expect(() => {
      validateWeapons([testGun({ levels: [[]] })]);
    }).toThrow(/stream/);
  });

  it('rejects a beam level without damage or width', () => {
    const beam = { ...testBeam(), levels: [{ damagePerSecond: 0, width: 2 }] };
    expect(() => {
      validateWeapons([beam]);
    }).toThrow(/positive/);
  });
});

describe('findWeapon / weaponLevelCount', () => {
  it('finds a weapon by id and counts its levels', () => {
    const weapons = [testGun(), testBeam()];
    expect(findWeapon(weapons, 'beam').name).toBe('Beam');
    expect(weaponLevelCount(findWeapon(weapons, 'gun'))).toBe(2);
    expect(() => findWeapon(weapons, 'nope')).toThrow(/Unknown/);
  });
});
