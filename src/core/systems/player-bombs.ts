/** The player's bombs (GD-32, P11-R05). */
export interface BombRules {
  /** Bombs at the start of a level, after a Continue, and the least after a lost life. */
  readonly start: number;
  /** Most bombs the player can have with bomb bonuses (P11-R07). */
  readonly max: number;
  /** Damage each enemy and boss piece on screen takes, once, when a bomb goes off. */
  readonly damage: number;
  /**
   * Seconds a bomb lasts: no other bomb can go off meanwhile, the enemy shots keep being cleared
   * and the player cannot be hurt.
   */
  readonly seconds: number;
}

/** A bomb going off, for the visuals. */
export interface ActiveBomb {
  /** Where the ship was when it went off. */
  readonly x: number;
  readonly y: number;
  /** Seconds since it went off. */
  readonly age: number;
  readonly seconds: number;
}

/**
 * The bombs left and the bomb going off (P11-R05): one goes off per press while some are left
 * and none is active; lives lost top them back up to the starting count. Pure.
 */
export class PlayerBombs {
  count: number;
  #active: { x: number; y: number; age: number } | undefined;
  /** Bombs gone off since the level started. */
  fired = 0;

  constructor(readonly rules: BombRules) {
    this.count = rules.start;
  }

  /** The bomb going off, if any. */
  get active(): ActiveBomb | undefined {
    const bomb = this.#active;
    return bomb && { ...bomb, seconds: this.rules.seconds };
  }

  /** Sets a bomb off at (`x`, `y`) if one is left and none is active; returns whether it did. */
  fire(x: number, y: number): boolean {
    if (this.count <= 0 || this.#active) return false;
    this.count--;
    this.fired++;
    this.#active = { x, y, age: 0 };
    return true;
  }

  /** A bomb bonus (P11-R07): one more bomb, up to the most. Returns whether it was added. */
  add(): boolean {
    if (this.count >= this.rules.max) return false;
    this.count++;
    return true;
  }

  /** After a lost life: back up to the starting count if fewer are left. */
  refill(): void {
    this.count = Math.max(this.count, this.rules.start);
  }

  step(dt: number): void {
    const bomb = this.#active;
    if (!bomb) return;
    bomb.age += dt;
    if (bomb.age >= this.rules.seconds) this.#active = undefined;
  }
}
