import { describe, expect, it } from 'vitest';
import { weaponSummary } from '../../../src/ui/weapon-summary';
import { testBeam, testGun } from '../../helpers/test-weapons';

describe('weaponSummary', () => {
  it('P03-R10: describes the streams, rate and damage of a projectile level', () => {
    const gun = testGun({
      levels: [
        [
          { offsetX: 0, angleDeg: 0 },
          { offsetX: 0, angleDeg: -10 },
          { offsetX: 0, angleDeg: 20 },
        ],
      ],
    });
    expect(weaponSummary(gun, 1)).toBe(
      'Gun L1 · 3 streams (0°, −10°, +20°) · 10 shots/s per stream · 5 damage',
    );
    expect(weaponSummary(testGun({ blastRadius: 10 }), 1)).toBe(
      'Gun L1 · 1 stream (0°) · 10 shots/s per stream · 5 damage within 10 px',
    );
  });

  it('P03-R10: describes the damage, width and piercing of a beam level', () => {
    expect(weaponSummary(testBeam(), 1)).toBe(
      'Beam L1 · 10 damage/s · 2 px wide · stops at the first ship',
    );
    expect(weaponSummary(testBeam(), 3)).toBe(
      'Beam L3 · 30 damage/s · 6 px wide · goes through 2 ships',
    );
    expect(weaponSummary(testBeam(), 9)).toBe('Beam L9');
  });
});
