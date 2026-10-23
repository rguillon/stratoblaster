import { describe, expect, it } from 'vitest';
import { validateWeapons, type ShotStream } from '../../../../src/core/entities/weapon';
import { BULLET, LASER, MISSILE, PLAYER_WEAPONS } from '../../../../src/game/config/player-weapons';

/** Stream directions of a level, sorted, as "angle@offset" strings. */
function streams(levels: readonly (readonly ShotStream[])[], level: number): string[] {
  return (levels[level - 1] ?? []).map((s) => `${String(s.angleDeg)}@${String(s.offsetX)}`).sort();
}

describe('player weapons', () => {
  it('GD-30, GD-31: three valid weapons with five levels each', () => {
    expect(() => {
      validateWeapons(PLAYER_WEAPONS);
    }).not.toThrow();
    expect(PLAYER_WEAPONS.map((w) => w.id)).toEqual(['bullet', 'laser', 'missile']);
    for (const weapon of PLAYER_WEAPONS) expect(weapon.levels).toHaveLength(5);
  });

  it('P03-R01: bullets move at constant velocity and deal 10 damage each', () => {
    expect(BULLET.acceleration).toBe(0);
    expect(BULLET.homingTurnRateDeg).toBe(0);
    expect(BULLET.damage).toBe(10);
    expect(BULLET.blastRadius).toBe(0);
  });

  it('P03-R01: bullet streams per level', () => {
    expect(streams(BULLET.levels, 1)).toEqual(['0@0']);
    expect(streams(BULLET.levels, 2)).toEqual(['0@-6', '0@6']);
    expect(streams(BULLET.levels, 3)).toEqual(['-10@0', '0@0', '10@0']);
    expect(streams(BULLET.levels, 4)).toEqual(['-10@0', '0@-6', '0@6', '10@0']);
    expect(streams(BULLET.levels, 5)).toEqual(['-10@0', '-20@0', '0@0', '10@0', '20@0']);
  });

  it('P03-R02: the laser does more damage per second at each level', () => {
    const dps = LASER.levels.map((l) => l.damagePerSecond);
    for (let i = 1; i < dps.length; i++) expect(dps[i]).toBeGreaterThan(dps[i - 1] ?? Infinity);
  });

  it('P03-R03: missiles accelerate, home, and deal 8 damage within 10 px, 4 per second', () => {
    expect(MISSILE.acceleration).toBeGreaterThan(0);
    expect(MISSILE.homingTurnRateDeg).toBeGreaterThan(0);
    expect(MISSILE.damage).toBe(8);
    expect(MISSILE.blastRadius).toBe(10);
    expect(MISSILE.shotsPerSecond).toBe(4);
    // Phase 3 review: missiles leave from the centre of the ship, bullets from its nose.
    expect(MISSILE.launchPoint).toBe('center');
    expect(BULLET.launchPoint).toBe('muzzle');
  });

  it('P03-R03: missile streams per level, diagonals widened to 25° / 45° (phase 3 review)', () => {
    expect(streams(MISSILE.levels, 1)).toEqual(['0@0']);
    expect(streams(MISSILE.levels, 2)).toEqual(['-25@0', '25@0']);
    expect(streams(MISSILE.levels, 3)).toEqual(['-25@0', '0@0', '25@0']);
    expect(streams(MISSILE.levels, 4)).toEqual(['-25@0', '-45@0', '25@0', '45@0']);
    expect(streams(MISSILE.levels, 5)).toEqual(['-25@0', '-45@0', '0@0', '25@0', '45@0']);
  });
});
