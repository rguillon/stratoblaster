import { Enemy, type EnemyContext, type EnemyStats } from '../../../core/entities/enemy';
import { headingTo, turnTowards, wrapAngle } from '../../../core/systems/projectile-motion';

/** How a {@link Hornet} moves. */
export interface HornetOptions {
  readonly stats: EnemyStats;
  /** Height where it stops before the dive; without one it starts with the pause. */
  readonly stopY?: number;
  readonly entrySpeed?: number;
  /** Deceleration into the stop, so it slows down instead of halting at once. */
  readonly entryBrake?: number;
  readonly pause: number;
  /** The dive starts from rest and gathers speed at this rate (phase 5 review: no jolt). */
  readonly diveAcceleration: number;
  readonly diveMaxSpeed: number;
}

type HornetState = 'enter' | 'aim' | 'dive';

/** How fast the nose eases in on the player: turn rate per radian left to turn, per second. */
const TURN_EASE = 14;

/**
 * P05-R02: a diver. It flies down to its stop height, braking into it, stops for `pause` seconds
 * while turning its nose to the player, then dives in a straight line towards where the player
 * was at the end of the pause, accelerating from rest, until it leaves the screen. It does not
 * shoot. Splitter pods (P05-R10) are small Hornets that start with the pause.
 */
export class Hornet extends Enemy {
  state: HornetState;
  /** Direction of the dive, fixed at the end of the pause. */
  diveHeading: number | undefined;
  #pauseLeft: number;
  #speed = 0;

  constructor(
    x: number,
    y: number,
    private readonly options: HornetOptions,
  ) {
    super(x, y, options.stats);
    this.state = options.stopY === undefined ? 'aim' : 'enter';
    this.#pauseLeft = options.pause;
  }

  override update(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') this.#enter(ctx, dt);
    else if (this.state === 'aim') this.#aim(ctx, dt);
    else this.#dive(dt);
  }

  #enter(ctx: EnemyContext, dt: number): void {
    const { stopY = this.y, entrySpeed = 0, entryBrake = Number.MAX_VALUE } = this.options;
    // Full speed until the braking distance, then a constant deceleration down to 0 at the stop.
    const speed = Math.min(entrySpeed, Math.sqrt(2 * entryBrake * (this.y - stopY)));
    this.y -= speed * dt;
    // The nose starts coming round as it slows down.
    if (speed < entrySpeed) this.#turnToPlayer(ctx, dt);
    if (this.y <= stopY) {
      this.y = stopY;
      this.state = 'aim';
    }
  }

  /** Turns the nose to the player, easing in as it gets there; returns the player's heading. */
  #turnToPlayer(ctx: EnemyContext, dt: number): number {
    const target = headingTo(this.x, this.y, ctx.playerX, ctx.playerY);
    const left = Math.abs(wrapAngle(target - this.heading));
    // Fast enough to turn all the way round during the pause, slowing down near the end.
    const rate = Math.min(Math.PI / this.options.pause, TURN_EASE * left);
    this.heading = turnTowards(this.heading, target, rate * dt);
    return target;
  }

  #aim(ctx: EnemyContext, dt: number): void {
    const target = this.#turnToPlayer(ctx, dt);
    this.#pauseLeft -= dt;
    this.charge = 1 - Math.max(0, this.#pauseLeft) / this.options.pause;
    if (this.#pauseLeft > 0) return;
    this.diveHeading = target;
    this.heading = target;
    this.#speed = 0;
    this.state = 'dive';
  }

  #dive(dt: number): void {
    const { diveAcceleration, diveMaxSpeed } = this.options;
    this.#speed = Math.min(diveMaxSpeed, this.#speed + diveAcceleration * dt);
    this.x += Math.sin(this.heading) * this.#speed * dt;
    this.y += Math.cos(this.heading) * this.#speed * dt;
  }
}
