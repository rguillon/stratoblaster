import type { DropSource } from '../entities/enemy';
import type { Random } from '../math/rng';

/**
 * What a bonus gives when picked up: a weapon level (phase 6 review, GD-31), a life (GD-20) or a
 * bomb (GD-32, P11-R07).
 */
export type BonusKind = 'weapon' | 'life' | 'bomb';

/**
 * Bonuses (phase 6 review, GD-31, P11-R07): some destroyed enemies drop one, it falls down the
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
  /**
   * Chances that a destroyed enemy (not a boss or one of its parts) drops a life or a bomb
   * bonus (P11-R07), drawn in that order before the weapon bonus's {@link chance}: an enemy
   * drops at most one bonus. Weapon bonuses only when omitted.
   */
  readonly special?: { readonly life: number; readonly bomb: number };
  /** Points scored for a life or bomb bonus picked up when the player has the most (P11-R07). */
  readonly overflowPoints?: { readonly life: number; readonly bomb: number };
}

/** A bonus falling down the playfield. */
export interface Bonus {
  readonly id: number;
  x: number;
  y: number;
  /** Seconds since it dropped (for its animation). */
  age: number;
  readonly kind: BonusKind;
}

/**
 * The chance (0..1) that destroying `target` drops a bonus: its own chance if it has one (a
 * boss's part, P07-R07), the rules' otherwise.
 */
export function dropChance(rules: BonusRules, target: DropSource): number {
  if (target.dropChance !== undefined) return target.dropChance;
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
    /**
     * Where the life and bomb draws come from (P11-R07): a source of their own, so the weapon
     * bonuses drop as they did without them. `random` when omitted.
     */
    private readonly specialRandom: Random = random,
  ) {}

  /**
   * Each of the destroyed `targets` drops a weapon bonus with its {@link dropChance}; those
   * that are `special` (enemies, not bosses or their parts) may drop a life or a bomb bonus
   * instead (P11-R07).
   */
  drop(targets: readonly DropSource[], special?: (target: DropSource) => boolean): void {
    for (const target of targets) {
      const kind = this.#kindFor(target, special?.(target) ?? false);
      if (kind) this.place(kind, target);
    }
  }

  /** Drops a bonus of `kind` where `at` is, within the ship's reach. */
  place(kind: BonusKind, at: { readonly x: number; readonly y: number }): void {
    const [xMin, xMax] = this.reach;
    const x = Math.min(xMax, Math.max(xMin, at.x));
    this.bonuses.push({ id: this.#nextId++, x, y: at.y, age: 0, kind });
    this.dropped++;
  }

  /**
   * The kind of bonus `target` drops, if any: at most one, life first, then bomb, then weapon.
   * The weapon draw always happens, so the weapon bonuses' draws stay as without the others.
   */
  #kindFor(target: DropSource, special: boolean): BonusKind | undefined {
    const weapon = this.random() < dropChance(this.rules, target);
    const odds = special ? this.rules.special : undefined;
    if (odds && this.specialRandom() < odds.life) return 'life';
    if (odds && this.specialRandom() < odds.bomb) return 'bomb';
    return weapon ? 'weapon' : undefined;
  }

  /** Moves the bonuses by `dt` seconds; the ship at `ship` (if any) picks up those it touches. */
  step(dt: number, ship?: { readonly x: number; readonly y: number }): void {
    const { fallSpeed, pickupRadius } = this.rules;
    this.picked = [];
    for (let i = this.bonuses.length - 1; i >= 0; i--) {
      const bonus = this.bonuses[i];
      if (!bonus) continue;
      bonus.y -= fallSpeed * dt;
      bonus.age += dt;
      const touched =
        ship !== undefined && Math.hypot(bonus.x - ship.x, bonus.y - ship.y) <= pickupRadius;
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
