import { BossJoints, type BossJointSpec } from './boss-joint';
import {
  Enemy,
  type DropSource,
  type EnemyContext,
  type EnemyStats,
  type LaserOwner,
} from './enemy';
import { muzzlePoint, type Muzzle, type RaisedPoint } from './muzzle';
import type { ShotTarget } from './shot-target';

/**
 * Enemies with moving parts (P05-R13): parts that hang on swinging joints (as a boss's limbs,
 * D-061) or orbit the hull, each with its own hit circle, health and guns. A destroyed part blows
 * up and stops; the enemy goes with its hull, taking its parts with it.
 */

/** A part of a {@link JointedEnemy}. */
export interface EnemyPartSpec {
  readonly id: string;
  /** Its centre, from the enemy's centre, as drawn facing down at rest (X right, Y up). */
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  readonly health: number;
  /** The joint it hangs on, if any: it moves with it. */
  readonly joint?: string;
  /** Whether it turns around the centre with the enemy's `spin` (it cannot hang on a joint). */
  readonly orbits?: boolean;
  /** Radians, clockwise on screen, from the enemy's nose to the way the part points at rest. */
  readonly aim?: number;
  /** Whether the hull cannot be hit while it stands (a shield, as a boss's, P07-R01). */
  readonly shields?: boolean;
}

/** How a {@link JointedEnemy} is built: its parts and the joints they hang on. */
export interface JointedDesign {
  readonly parts: readonly EnemyPartSpec[];
  readonly joints?: Readonly<Record<string, BossJointSpec>>;
}

/** A destroyable part of a {@link JointedEnemy}, where it is now. */
export class EnemyPart implements DropSource, LaserOwner {
  x = 0;
  y = 0;
  /** The way it points now (radians from +Y, clockwise): its guns fire along it. */
  heading = Math.PI;
  /** Seconds since it last took damage (for the hit flash); Infinity before. */
  sinceHit = Infinity;
  /** Set once its destruction was handled (it blew up). */
  broken = false;
  /** Parts never drop a bonus (P05-R13). */
  readonly dropChance = 0;
  readonly radius: number;
  readonly maxHealth: number;
  #health: number;

  constructor(
    readonly spec: EnemyPartSpec,
    readonly index: number,
    private readonly owner: JointedEnemy,
  ) {
    this.radius = spec.radius;
    this.maxHealth = spec.health;
    this.#health = spec.health;
  }

  /** Unique among the world's targets: below 0, apart from every enemy's id. */
  get id(): number {
    return -(this.owner.id * 64 + this.index + 1);
  }

  get health(): number {
    return this.#health;
  }

  set health(value: number) {
    const next = Math.max(0, value);
    if (next < this.#health) this.sinceHit = 0;
    this.#health = next;
  }

  get destroyed(): boolean {
    return this.#health <= 0;
  }

  get gone(): boolean {
    return this.owner.gone || this.destroyed;
  }

  /** Lasers leave one radius ahead of its centre, along its heading. */
  get emitter(): { readonly x: number; readonly y: number } {
    return {
      x: this.x + Math.sin(this.heading) * this.radius,
      y: this.y + Math.cos(this.heading) * this.radius,
    };
  }

  /**
   * Where `muzzle` (from the enemy's centre, as drawn facing down at rest) is now: moved by the
   * joint the part hangs on, or turned by the spin if it orbits, then with the enemy's nose.
   */
  place(muzzle: Muzzle): RaisedPoint {
    const [x, y] = this.owner.joints.move(this.spec.joint, muzzle[0], muzzle[1]);
    return muzzlePoint(this.owner, [x, y, muzzle[2]], this.spec.orbits ? this.owner.spin : 0);
  }

  /** Destroys it at once (its enemy's death). */
  destroy(): void {
    this.#health = 0;
  }
}

/**
 * Base of the enemies with moving parts (P05-R13). Each step swings the joints, runs the kind's
 * {@link act}, then puts the parts where they are now; parts the player destroyed blow up.
 */
export abstract class JointedEnemy extends Enemy {
  readonly parts: readonly EnemyPart[];
  readonly joints: BossJoints;
  /** Radians, clockwise on screen, the orbiting parts are turned by. */
  spin = 0;
  /** Whether the joints swing on; a kind holds them still while this is false. */
  protected swinging = true;
  readonly #specs: Readonly<Record<string, BossJointSpec>>;

  constructor(x: number, y: number, stats: EnemyStats, design: JointedDesign) {
    super(x, y, stats);
    this.#specs = design.joints ?? {};
    this.joints = new BossJoints(this.#specs, design.parts);
    this.parts = design.parts.map((spec, i) => new EnemyPart(spec, i, this));
    this.#placeParts();
  }

  /** Its part `id`, if it is still there. */
  part(id: string): EnemyPart | undefined {
    return this.parts.find((p) => p.spec.id === id && !p.destroyed);
  }

  /** Whether a standing part shields the hull. */
  get shielded(): boolean {
    return this.parts.some((p) => p.spec.shields === true && !p.destroyed);
  }

  /** The hull and its standing parts: what shots hit and the player can bump into. */
  override get hitTargets(): readonly ShotTarget[] {
    return [this, ...this.parts.filter((p) => !p.destroyed)];
  }

  /** Shots pass through a shielded hull (as a boss's core, P07-R01). */
  override get shotTargets(): readonly ShotTarget[] {
    const targets = this.hitTargets;
    return this.shielded ? targets.filter((t) => t !== this) : targets;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.#breakDestroyed(ctx);
    if (this.swinging) this.joints.step(dt);
    this.act(ctx, dt);
    this.#placeParts();
  }

  /** Moves and attacks for `dt` seconds, as {@link Enemy.update}; the parts are placed after. */
  protected abstract act(ctx: EnemyContext, dt: number): void;

  /** Its death blows up every part still on it. */
  override onDestroyed(ctx: EnemyContext): void {
    for (const part of this.parts) {
      if (part.broken) continue;
      part.destroy();
      part.broken = true;
      ctx.breakPart(part);
    }
  }

  /** How far joint `id` and those it hangs on are turned now, in all. */
  #turn(id: string | undefined): number {
    let angle = 0;
    for (let j = id; j !== undefined; j = this.#specs[j]?.parent) angle += this.joints.angle(j);
    return angle;
  }

  #placeParts(): void {
    for (const part of this.parts) {
      const { spec } = part;
      const at = part.place([spec.x, spec.y, 0]);
      part.x = at.x;
      part.y = at.y;
      const turn = spec.orbits ? this.spin : this.#turn(spec.joint);
      part.heading = this.heading + (spec.aim ?? 0) + turn;
    }
  }

  #breakDestroyed(ctx: EnemyContext): void {
    for (const part of this.parts) {
      if (!part.destroyed || part.broken) continue;
      part.broken = true;
      ctx.breakPart(part);
    }
  }
}
