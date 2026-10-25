import {
  Enemy,
  type DropSource,
  type EnemyContext,
  type EnemyStats,
  type LaserOwner,
} from './enemy';
import type { ShotTarget } from './shot-target';

/**
 * Bosses (P07): big enemies made of a core and destroyable parts (GD-46). Positions are
 * playfield logical pixels, X to the right, Y up. A boss faces down the screen and does not turn:
 * its parts keep their offsets from its centre.
 */

/** A destroyable part of a boss (P07-R01): a turret, a pod, an armour plate… */
export interface BossPartSpec {
  /** Stable key, used by the boss's model and by the volleys fired from it. */
  readonly id: string;
  /** Offset of its centre from the boss's centre (X right, Y up). */
  readonly x: number;
  readonly y: number;
  /** Hit radius. */
  readonly radius: number;
  readonly health: number;
  /** While this part is there, the core takes no damage. */
  readonly shieldsCore: boolean;
  /** Chance (0..1) that it drops a bonus when the player destroys it (P07-R07). */
  readonly dropChance: number;
  /** Whether it turns around the boss's centre with {@link Boss.spin} (e.g. on a turning ring). */
  readonly orbits?: boolean;
}

/** Fixed numbers of a boss. `health` is its core's, `radius` the size of the whole boss. */
export interface BossStats extends EnemyStats {
  readonly name: string;
  /** Hit radius of the core. */
  readonly coreRadius: number;
  readonly parts: readonly BossPartSpec[];
  /** Factor on the level's ground speed while it is fought (P07-R03). */
  readonly groundSpeed: number;
  /** Seconds it does not fire after one of its parts is destroyed (P07-R04). */
  readonly stagePause: number;
  /** Its death (P07-R06): a blast every `every` seconds over its hull for `seconds`. */
  readonly death: { readonly seconds: number; readonly every: number };
  /** Chance its core drops a bonus when it is destroyed; the game's rule when omitted. */
  readonly coreDropChance?: number;
}

/** Coming in (no damage taken), fighting, or blowing up. */
export type BossState = 'entering' | 'fighting' | 'dying';

/** Something of a boss that shots hit and its weapons fire from: a part or the core. */
export interface BossPiece extends ShotTarget, Omit<LaserOwner, 'health'> {
  /** Seconds since it last took damage (for the hit flash); Infinity before. */
  readonly sinceHit: number;
}

/** Laser owners fire along their heading from one radius ahead of their centre. */
function emitterOf(piece: { x: number; y: number; radius: number; heading: number }) {
  return {
    x: piece.x + Math.sin(piece.heading) * piece.radius,
    y: piece.y + Math.cos(piece.heading) * piece.radius,
  };
}

/** A destroyable part of a {@link Boss}, at its offset from the boss's centre. */
export class BossPart implements BossPiece, DropSource {
  x = 0;
  y = 0;
  /** Lasers fired from it go this way (straight down). */
  heading = Math.PI;
  sinceHit = Infinity;
  /** Set once the boss has taken its destruction into account (its stage went up). */
  broken = false;
  readonly radius: number;
  readonly maxHealth: number;
  readonly dropChance: number;
  readonly shieldsCore: boolean;
  #health: number;

  constructor(
    readonly spec: BossPartSpec,
    readonly index: number,
    private readonly boss: Boss,
  ) {
    this.radius = spec.radius;
    this.maxHealth = spec.health;
    this.#health = spec.health;
    this.dropChance = spec.dropChance;
    this.shieldsCore = spec.shieldsCore;
  }

  /** Unique among the boss's pieces (the core is the boss's id). */
  get id(): number {
    return -(this.boss.id * 64 + this.index + 1);
  }

  get health(): number {
    return this.#health;
  }

  /** Damage only counts once the boss is in place (P07-R05). */
  set health(value: number) {
    if (!this.boss.vulnerable) return;
    const next = Math.max(0, value);
    if (next < this.#health) this.sinceHit = 0;
    this.#health = next;
  }

  get destroyed(): boolean {
    return this.#health <= 0;
  }

  get gone(): boolean {
    return this.boss.gone || this.destroyed;
  }

  get emitter(): { readonly x: number; readonly y: number } {
    return emitterOf(this);
  }

  /** Destroys it at once, whatever the boss is doing (its death, a debug key). */
  destroy(): void {
    this.#health = 0;
  }
}

/** The core of a {@link Boss} as its shots see it: shielded while its shielding parts stand. */
export class BossCore implements BossPiece {
  heading = Math.PI;
  sinceHit = Infinity;
  readonly radius: number;
  readonly maxHealth: number;

  constructor(private readonly boss: Boss) {
    this.radius = boss.stats.coreRadius;
    this.maxHealth = boss.stats.health;
  }

  get id(): number {
    return this.boss.id;
  }

  get x(): number {
    return this.boss.x;
  }

  get y(): number {
    return this.boss.y;
  }

  get health(): number {
    return this.boss.coreHealth;
  }

  /** Shots that hit a shielded core (or one coming in) spark but do no damage (P07-R01). */
  set health(value: number) {
    if (!this.boss.vulnerable || this.boss.coreShielded) return;
    if (value < this.boss.coreHealth) this.sinceHit = 0;
    this.boss.hurtCore(value);
  }

  get gone(): boolean {
    return this.boss.gone || this.boss.state === 'dying';
  }

  get emitter(): { readonly x: number; readonly y: number } {
    return emitterOf(this);
  }
}

/**
 * Base of every boss (P07-R01, R04, GD-46): a core and destroyable parts that the player's shots
 * hit one by one. It goes through stages, one more each time a part is destroyed, pausing its
 * fire for `stagePause` at each; it blows up over `death.seconds` once its core has no health
 * left. Concrete bosses (in the game) say how they come in ({@link enter}), move ({@link move})
 * and fire ({@link updatePattern}); they may react to a new stage ({@link onStageChange}).
 *
 * Its `health` (as an {@link Enemy}) only says whether it is still there: it drops to 0 when
 * its death blasts are over, and the enemy world then removes it as destroyed.
 */
export abstract class Boss extends Enemy {
  override readonly expires = false;
  override readonly rammable = false;
  override readonly dropChance: number | undefined;
  readonly name: string;
  readonly groundSpeed: number;
  readonly parts: readonly BossPart[];
  readonly core: BossCore;
  state: BossState = 'entering';
  /** Number of parts destroyed so far (P07-R04). */
  stage = 0;
  /** Seconds left without firing, after a stage change. */
  pause = 0;
  /** How far its orbiting parts have turned, in radians, clockwise on screen. */
  spin = 0;
  #coreHealth: number;
  #dyingFor = 0;
  #blasts = 0;
  #targets: ShotTarget[] = [];

  constructor(
    x: number,
    y: number,
    readonly stats: BossStats,
  ) {
    super(x, y, stats);
    this.heading = Math.PI;
    this.name = stats.name;
    this.groundSpeed = stats.groundSpeed;
    this.dropChance = stats.coreDropChance;
    this.#coreHealth = stats.health;
    this.parts = stats.parts.map((spec, i) => new BossPart(spec, i, this));
    this.core = new BossCore(this);
    this.#place();
    this.#rebuildTargets();
  }

  /** Whether shots damage it: once it is in place, until it blows up. */
  get vulnerable(): boolean {
    return this.state === 'fighting';
  }

  /** Whether some part that shields the core is still there. */
  get coreShielded(): boolean {
    return this.parts.some((part) => part.shieldsCore && !part.destroyed);
  }

  get coreHealth(): number {
    return this.state === 'dying' ? 0 : this.#coreHealth;
  }

  /** Health of the core and every part when it arrives (its health bar's full length). */
  get fullHealth(): number {
    return this.parts.reduce((sum, part) => sum + part.maxHealth, this.stats.health);
  }

  /** Health of the core and the parts left. */
  get remainingHealth(): number {
    return this.parts.reduce((sum, part) => sum + part.health, this.coreHealth);
  }

  /** Its intact parts and its core, until it blows up. */
  override get hitTargets(): readonly ShotTarget[] {
    return this.#targets;
  }

  /** Sets the core's health; at 0 the boss starts blowing up. Used by its {@link core}. */
  hurtCore(value: number): void {
    if (value > 0) this.#coreHealth = value;
    else this.#startDying();
  }

  /** Destroys its next intact part, or its core once they are all gone (debug, P07-R09). */
  breakNext(): void {
    if (this.state === 'dying') return;
    const part = this.parts.find((p) => !p.destroyed);
    if (part) part.destroy();
    else this.#startDying();
  }

  override update(ctx: EnemyContext, dt: number): void {
    for (const piece of [this.core, ...this.parts]) piece.sinceHit += dt;
    if (this.state === 'dying') {
      this.#die(ctx, dt);
      return;
    }
    this.#breakParts(ctx);
    if (this.state === 'entering') {
      if (this.enter(ctx, dt)) this.state = 'fighting';
    } else {
      this.move(ctx, dt);
    }
    this.#place();
    if (this.state !== 'fighting' || this.pause > 0) {
      this.pause = Math.max(0, this.pause - dt);
      this.charge = 0;
      return;
    }
    this.updatePattern(ctx, dt);
  }

  /** Comes in for `dt` seconds; returns true once in place (it can then be damaged). */
  protected abstract enter(ctx: EnemyContext, dt: number): boolean;

  /** Moves for `dt` seconds once in place. */
  protected abstract move(ctx: EnemyContext, dt: number): void;

  /** Fires the pattern of the current stage for `dt` seconds (not during a pause). */
  protected abstract updatePattern(ctx: EnemyContext, dt: number): void;

  /** Called when a part is destroyed and `stage` has gone up (P07-R04), if defined. */
  protected onStageChange?(stage: number, ctx: EnemyContext): void;

  /** Takes the parts destroyed since the last step into account: a stage more for each. */
  #breakParts(ctx: EnemyContext): void {
    let changed = false;
    for (const part of this.parts) {
      if (!part.destroyed || part.broken) continue;
      part.broken = true;
      changed = true;
      this.stage++;
      this.pause = this.stats.stagePause;
      ctx.breakPart(part);
      this.onStageChange?.(this.stage, ctx);
    }
    if (changed) this.#rebuildTargets();
  }

  #startDying(): void {
    this.state = 'dying';
    this.#coreHealth = 0;
    this.charge = 0;
    for (const part of this.parts) {
      part.destroy();
      part.broken = true;
    }
    this.#targets = [];
  }

  /** Blasts over the hull, one by one, then it is destroyed (its last, big blast). */
  #die(ctx: EnemyContext, dt: number): void {
    const { seconds, every } = this.stats.death;
    this.#dyingFor += dt;
    while (this.#blasts * every <= Math.min(this.#dyingFor, seconds)) {
      const part = this.parts[this.#blasts % Math.max(1, this.parts.length)];
      const spread = (part?.radius ?? this.stats.coreRadius) * 0.6;
      const [x, y] = part ? [part.x, part.y] : [this.x, this.y];
      const jitter = (): number => (ctx.random() * 2 - 1) * spread;
      ctx.explode(x + jitter(), y + jitter(), part?.radius ?? this.stats.coreRadius);
      this.#blasts++;
    }
    if (this.#dyingFor >= seconds) this.health = 0;
  }

  #place(): void {
    const [c, s] = [Math.cos(this.spin), Math.sin(this.spin)];
    for (const part of this.parts) {
      const { x, y, orbits } = part.spec;
      // Clockwise on screen (X right, Y up) by `spin` for the orbiting ones.
      part.x = this.x + (orbits ? x * c + y * s : x);
      part.y = this.y + (orbits ? -x * s + y * c : y);
    }
  }

  #rebuildTargets(): void {
    this.#targets = [...this.parts.filter((part) => !part.destroyed), this.core];
  }
}
