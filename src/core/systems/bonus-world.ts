import type { ShotTarget } from '../entities/shot-target';
import type { Random } from '../math/rng';

/**
 * Weapon bonuses (phase 6 review, GD-31): some destroyed enemies drop one, it falls down the
 * screen, and the ship picks it up by flying over it.
 */
export interface BonusRules {
  /**
   * Chance that a destroyed enemy drops a bonus: `perHealth × maxHealth`, kept within
   * [`min`, `max`], so tougher enemies drop one more often.
   */
  readonly chance: { readonly perHealth: number; readonly min: number; readonly max: number };
  /** Speed it falls down the screen at, in logical pixels per second. */
  readonly fallSpeed: number;
  /** The ship picks a bonus up when their centres are this close. */
  readonly pickupRadius: number;
}

/** A bonus falling down the playfield. */
export interface Bonus {
  readonly id: number;
  x: number;
  y: number;
  /** Seconds since it dropped (for its animation). */
  age: number;
}

/** The chance (0..1) that destroying `target` drops a bonus. */
export function dropChance(rules: BonusRules, target: ShotTarget): number {
  const { perHealth, min, max } = rules.chance;
  return Math.min(max, Math.max(min, perHealth * target.maxHealth));
}

/**
 * The bonuses of a level: dropped where enemies blew up (moved in sideways to where the ship
 * can reach), falling, picked up by the ship or gone past the bottom edge. Pure and
 * deterministic for a given random source.
 */
export class BonusWorld {
  readonly bonuses: Bonus[] = [];
  /** Bonuses picked up during the last step. */
  picked: Bonus[] = [];
  dropped = 0;
  collected = 0;
  #nextId = 1;

  constructor(
    private readonly rules: BonusRules,
    private readonly random: Random,
    /** X range the ship can reach: bonuses drop within it. */
    private readonly reach: readonly [number, number],
    /** Bonuses this far under the bottom edge are removed. */
    private readonly cullMargin: number,
  ) {}

  /** Each of the destroyed `targets` drops a bonus with its {@link dropChance}. */
  drop(targets: readonly ShotTarget[]): void {
    const [xMin, xMax] = this.reach;
    for (const target of targets) {
      if (this.random() >= dropChance(this.rules, target)) continue;
      const x = Math.min(xMax, Math.max(xMin, target.x));
      this.bonuses.push({ id: this.#nextId++, x, y: target.y, age: 0 });
      this.dropped++;
    }
  }

  /** Moves the bonuses by `dt` seconds; the ship at `ship` picks up those it touches. */
  step(dt: number, ship: { readonly x: number; readonly y: number }): void {
    const { fallSpeed, pickupRadius } = this.rules;
    this.picked = [];
    for (let i = this.bonuses.length - 1; i >= 0; i--) {
      const bonus = this.bonuses[i];
      if (!bonus) continue;
      bonus.y -= fallSpeed * dt;
      bonus.age += dt;
      const touched = Math.hypot(bonus.x - ship.x, bonus.y - ship.y) <= pickupRadius;
      if (touched) this.picked.push(bonus);
      if (touched || bonus.y < -this.cullMargin) this.bonuses.splice(i, 1);
    }
    this.collected += this.picked.length;
  }

  /** Removes every bonus. */
  clear(): void {
    this.bonuses.length = 0;
    this.picked = [];
  }
}
