import { describe, expect, it } from 'vitest';
import { PlayerHull, type HullRules } from '../../../../src/core/systems/player-hull';

const RULES: HullRules = {
  lives: 2,
  invincibleSeconds: 2,
  hitRadius: 5,
  damage: { bullet: 10, missile: 20, laser: 25, collision: 30 },
  ramDamage: 40,
};

describe('PlayerHull (phase 6 review)', () => {
  it('GD-20, GD-22: a hit takes health, then the ship is invincible for a while', () => {
    const hull = new PlayerHull(RULES, 50);
    expect([hull.health, hull.lives, hull.invincible]).toEqual([50, 2, 0]);
    expect(hull.hit(10)).toBe('hit');
    expect([hull.health, hull.invincible]).toEqual([40, 2]);
    expect(hull.hit(10)).toBe('ignored');
    expect(hull.health).toBe(40);
    hull.step(1.5);
    expect(hull.invincible).toBeCloseTo(0.5);
    hull.step(1);
    expect(hull.invincible).toBe(0);
    expect(hull.hit(10)).toBe('hit');
    expect(hull.health).toBe(30);
  });

  it('GD-20: out of health, a life is lost and the ship comes back full; out of lives, game over', () => {
    const hull = new PlayerHull(RULES, 50);
    expect(hull.hit(60)).toBe('lifeLost');
    expect([hull.health, hull.lives, hull.out]).toEqual([50, 1, false]);
    expect(hull.invincible).toBe(2);
    hull.step(2);
    expect(hull.hit(50)).toBe('gameOver');
    expect([hull.health, hull.lives, hull.out]).toEqual([0, 0, true]);
    hull.step(5);
    expect(hull.hit(10)).toBe('ignored');
  });
});
