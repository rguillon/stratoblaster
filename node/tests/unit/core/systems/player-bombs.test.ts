import { describe, expect, it } from 'vitest';
import { PlayerBombs, type BombRules } from '../../../../src/core/systems/player-bombs';

const RULES: BombRules = { start: 3, max: 5, damage: 100, seconds: 1 };

describe('PlayerBombs (P11-R05)', () => {
  it('P11-R05: starts with the starting count; each bomb goes off where the ship is, for its time', () => {
    const bombs = new PlayerBombs(RULES);
    expect([bombs.count, bombs.active]).toEqual([3, undefined]);
    expect(bombs.fire(10, 20)).toBe(true);
    expect(bombs.count).toBe(2);
    expect(bombs.active).toEqual({ x: 10, y: 20, age: 0, seconds: 1 });
    bombs.step(0.5);
    expect(bombs.active?.age).toBeCloseTo(0.5);
    bombs.step(0.5);
    expect(bombs.active).toBeUndefined();
  });

  it('P11-R05: no bomb goes off while one is active, nor with none left', () => {
    const bombs = new PlayerBombs({ ...RULES, start: 1 });
    expect(bombs.fire(0, 0)).toBe(true);
    expect(bombs.fire(0, 0)).toBe(false);
    bombs.step(1);
    expect(bombs.fire(0, 0)).toBe(false);
    expect([bombs.count, bombs.fired]).toEqual([0, 1]);
  });

  it('P11-R05: bombs go off at most once per bomb time, so the flash stays below 3 a second', () => {
    const bombs = new PlayerBombs({ ...RULES, start: 5 });
    let fired = 0;
    for (let i = 0; i < 180; i++) {
      if (bombs.fire(0, 0)) fired++;
      bombs.step(1 / 60);
    }
    // 3 s of the key pressed on every step.
    expect(fired).toBeLessThanOrEqual(3);
    expect(fired / 3).toBeLessThan(3);
  });

  it('P11-R05, R07: a bomb bonus adds one up to the most; a lost life tops them up to the start', () => {
    const bombs = new PlayerBombs(RULES);
    expect([bombs.add(), bombs.add(), bombs.add()]).toEqual([true, true, false]);
    expect(bombs.count).toBe(5);
    bombs.refill();
    expect(bombs.count).toBe(5);
    const low = new PlayerBombs({ ...RULES, start: 1 });
    low.fire(0, 0);
    low.refill();
    expect(low.count).toBe(1);
  });

  it('reviewer, 2026-10-28: starts with the bombs kept from the level before; no limit without a most', () => {
    const bombs = new PlayerBombs({ start: 3, damage: 100, seconds: 1 }, 7);
    expect(bombs.count).toBe(7);
    for (let i = 0; i < 5; i++) expect(bombs.add()).toBe(true);
    expect(bombs.count).toBe(12);
  });
});
