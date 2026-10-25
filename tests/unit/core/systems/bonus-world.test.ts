import { describe, expect, it } from 'vitest';
import type { ShotTarget } from '../../../../src/core/entities/shot-target';
import { BonusWorld, dropChance, type BonusRules } from '../../../../src/core/systems/bonus-world';

const RULES: BonusRules = {
  chance: { perHealth: 0.01, min: 0.1, max: 0.5 },
  fallSpeed: 50,
  pickupRadius: 10,
};

const target = (x: number, y: number, maxHealth = 30): ShotTarget => ({
  id: 1,
  x,
  y,
  radius: 5,
  health: 0,
  maxHealth,
});

/** A world whose random draws come from `draws`, in turn. */
function world(draws: readonly number[], reach: readonly [number, number] = [0, 300]) {
  let i = 0;
  return new BonusWorld(RULES, () => draws[i++ % draws.length] ?? 0, reach, 20);
}

describe('BonusWorld (phase 6 review)', () => {
  it('drops more often from tougher enemies, within the min and max chance', () => {
    expect(dropChance(RULES, target(0, 0, 5))).toBe(0.1);
    expect(dropChance(RULES, target(0, 0, 30))).toBeCloseTo(0.3);
    expect(dropChance(RULES, target(0, 0, 200))).toBe(0.5);
  });

  it('a destroyed enemy drops a bonus where it was when the draw is under its chance', () => {
    const w = world([0.29, 0.31]);
    w.drop([target(100, 400), target(150, 300)]);
    expect(w.bonuses).toHaveLength(1);
    expect(w.bonuses[0]).toMatchObject({ x: 100, y: 400, age: 0 });
    expect(w.dropped).toBe(1);
  });

  it('drops within the X range the ship can reach', () => {
    const w = world([0], [100, 200]);
    w.drop([target(20, 400), target(260, 400)]);
    expect(w.bonuses.map((b) => b.x)).toEqual([100, 200]);
  });

  it('bonuses fall, the ship picks up those it touches, and those it misses go', () => {
    const w = world([0]);
    w.drop([target(100, 200), target(250, 200)]);
    const ship = { x: 100, y: 100 };
    for (let i = 0; i < 20 && w.picked.length === 0; i++) w.step(0.1, ship);
    expect(w.picked.map((b) => b.x)).toEqual([100]);
    expect(w.collected).toBe(1);
    expect(w.bonuses).toHaveLength(1);
    expect(w.bonuses[0]?.y).toBeCloseTo(110);
    expect(w.bonuses[0]?.age).toBeCloseTo(1.8);
    // Under the bottom edge (and the cull margin), the other one is gone.
    for (let i = 0; i < 30; i++) w.step(0.1, ship);
    expect(w.bonuses).toHaveLength(0);
    expect(w.collected).toBe(1);
    w.drop([target(100, 200)]);
    w.clear();
    expect(w.bonuses).toHaveLength(0);
  });
});
