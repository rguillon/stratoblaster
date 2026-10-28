/** What hurts the player and how much, and its lives (GD-20, GD-21, GD-22; phase 6 review). */
export interface HullRules {
  /** Lives at the start of a level (GD-20). */
  readonly lives: number;
  /**
   * Most lives the player can have with life bonuses (P11-R07); no limit when omitted
   * (reviewer, 2026-10-28).
   */
  readonly maxLives?: number;
  /** Seconds the ship cannot be hurt after a hit (GD-22). */
  readonly invincibleSeconds: number;
  /** Radius of the ship's hitbox: small, much smaller than its model (GD-21). */
  readonly hitRadius: number;
  /** Damage of an enemy bullet, a missile, a laser beam (once per beam), and a collision. */
  readonly damage: {
    readonly bullet: number;
    readonly missile: number;
    readonly laser: number;
    readonly collision: number;
  };
  /** Damage an enemy takes when the ship rams it (small ones blow up). */
  readonly ramDamage: number;
}

/** What taking a hit did. */
export type HullEvent = 'ignored' | 'hit' | 'lifeLost' | 'gameOver';

/**
 * The player ship's health and lives (GD-20, GD-22): a hit takes health and makes the ship
 * invincible for a while; when the health runs out a life is lost and the ship comes back with
 * full health (still invincible); with no life left, the game is over. Pure.
 */
export class PlayerHull {
  health: number;
  lives: number;
  /** Seconds of invincibility left. */
  invincible = 0;

  /** Starts with `lives`: the rules' (GD-20), or those kept from the level before. */
  constructor(
    private readonly rules: HullRules,
    readonly maxHealth: number,
    lives = rules.lives,
  ) {
    this.health = maxHealth;
    this.lives = lives;
  }

  /** Whether the game is over (no life left). */
  get out(): boolean {
    return this.lives <= 0;
  }

  /** Takes `damage`, unless invincible or out. */
  hit(damage: number): HullEvent {
    if (this.invincible > 0 || this.out) return 'ignored';
    this.health = Math.max(0, this.health - damage);
    this.invincible = this.rules.invincibleSeconds;
    if (this.health > 0) return 'hit';
    this.lives--;
    if (this.lives <= 0) return 'gameOver';
    this.health = this.maxHealth;
    return 'lifeLost';
  }

  /** A life bonus (P11-R07): one more life, up to the most if any. Returns whether it was added. */
  addLife(): boolean {
    if (this.out || this.lives >= (this.rules.maxLives ?? Infinity)) return false;
    this.lives++;
    return true;
  }

  step(dt: number): void {
    this.invincible = Math.max(0, this.invincible - dt);
  }
}
