import { Enemy, type EnemyContext, type EnemyStats } from '../../../core/entities/enemy';
import { headingTo, turnTowards } from '../../../core/systems/projectile-motion';

/** How a {@link Hornet} moves. */
export interface HornetOptions {
  readonly stats: EnemyStats;
  /** Height where it stops before the dive; without one it starts with the pause. */
  readonly stopY?: number;
  readonly entrySpeed?: number;
  readonly pause: number;
  readonly diveSpeed: number;
  readonly diveAcceleration: number;
  readonly diveMaxSpeed: number;
}

type HornetState = 'enter' | 'aim' | 'dive';

/**
 * P05-R02: a diver. It flies down to its stop height, stops for `pause` seconds while turning
 * its nose to the player, then dives in a straight line towards where the player was at the end
 * of the pause, accelerating, until it leaves the screen. It does not shoot. Splitter pods
 * (P05-R10) are small Hornets that start with the pause.
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
    if (this.state === 'enter') this.#enter(dt);
    else if (this.state === 'aim') this.#aim(ctx, dt);
    else this.#dive(dt);
  }

  #enter(dt: number): void {
    const { stopY = this.y, entrySpeed = 0 } = this.options;
    this.y -= entrySpeed * dt;
    if (this.y <= stopY) {
      this.y = stopY;
      this.state = 'aim';
    }
  }

  #aim(ctx: EnemyContext, dt: number): void {
    const target = headingTo(this.x, this.y, ctx.playerX, ctx.playerY);
    // Fast enough to turn all the way round during the pause.
    this.heading = turnTowards(this.heading, target, (Math.PI / this.options.pause) * dt);
    this.#pauseLeft -= dt;
    this.charge = 1 - Math.max(0, this.#pauseLeft) / this.options.pause;
    if (this.#pauseLeft > 0) return;
    this.diveHeading = target;
    this.heading = target;
    this.#speed = this.options.diveSpeed;
    this.state = 'dive';
  }

  #dive(dt: number): void {
    const { diveAcceleration, diveMaxSpeed } = this.options;
    this.#speed = Math.min(diveMaxSpeed, this.#speed + diveAcceleration * dt);
    this.x += Math.sin(this.heading) * this.#speed * dt;
    this.y += Math.cos(this.heading) * this.#speed * dt;
  }
}
