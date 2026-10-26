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

  it('P11-R07: a destroyed enemy drops at most one bonus: life first, then bomb, then weapon', () => {
    const special = { ...RULES, special: { life: 0.1, bomb: 0.2 } };
    /** A world whose weapon draws come from `weapon` and life / bomb draws from `others`. */
    const draws = (weapon: readonly number[], others: readonly number[]) => {
      let [i, j] = [0, 0];
      const next = () => weapon[i++] ?? 1;
      return new BonusWorld(special, next, [0, 300], 20, () => others[j++] ?? 1);
    };
    const all = () => true;
    // The weapon draw hits (0.2 < 0.3 for 30 HP), but life 0.05 < 0.1 wins: one life bonus.
    const life = draws([0.2], [0.05]);
    life.drop([target(100, 200)], all);
    expect(life.bonuses.map((b) => b.kind)).toEqual(['life']);
    // Life missed (0.5), bomb 0.1 < 0.2.
    const bomb = draws([0.9], [0.5, 0.1]);
    bomb.drop([target(100, 200)], all);
    expect(bomb.bonuses.map((b) => b.kind)).toEqual(['bomb']);
    // Both missed: the weapon draw decides.
    const weapon = draws([0.2], [0.5, 0.5]);
    weapon.drop([target(100, 200)], all);
    expect(weapon.bonuses.map((b) => b.kind)).toEqual(['weapon']);
    // Not special (a boss or its parts): no life or bomb draw.
    const plain = draws([0.2], [0]);
    plain.drop([target(100, 200)], () => false);
    plain.drop([target(100, 200)]);
    expect(plain.bonuses.map((b) => b.kind)).toEqual(['weapon']);
  });

  it('P11-R07: the weapon draws are the same with or without life and bomb bonuses', () => {
    const sequence = [0.05, 0.5, 0.25, 0.9, 0.1, 0.35];
    const dropped = (rules: typeof RULES) => {
      let i = 0;
      const w = new BonusWorld(
        rules,
        () => sequence[i++ % sequence.length] ?? 1,
        [0, 300],
        20,
        () => 0.5,
      );
      for (let k = 0; k < 6; k++) w.drop([target(10 * k, 200)], () => true);
      return w.bonuses.map((b) => b.x);
    };
    const special = { ...RULES, special: { life: 0, bomb: 0 } };
    expect(dropped(special)).toEqual(dropped(RULES));
    expect(dropped(RULES)).toEqual([0, 20, 40]);
  });

  it("P11-R07: a bonus of a given kind can be placed, within the ship's reach", () => {
    const w = world([0], [50, 250]);
    w.place('life', { x: 10, y: 300 });
    expect(w.bonuses).toEqual([{ id: 1, x: 50, y: 300, age: 0, kind: 'life' }]);
    expect(w.dropped).toBe(1);
  });
});
