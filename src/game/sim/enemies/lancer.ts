import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import type { RaisedPoint } from '../../../core/entities/muzzle';
import { ENEMY_CONFIG } from '../../config/enemies';
import { DOWN } from './enemy-helpers';

const CFG = ENEMY_CONFIG.lancer;

type LancerState = 'enter' | 'attack' | 'exit';

/** Slowest speed while braking to the stop point, px/s. */
const CREEP = 20;

/**
 * P05-R07: moves to a fixed point in the top part of the screen and stops. A warning line
 * shows straight down from its emitter for 1 s, then it fires a laser along that line for
 * 1.5 s (GD-43), without moving; then it backs away upward.
 */
export class Lancer extends Enemy {
  state: LancerState = 'enter';
  #attackFor = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
  }

  /** The front of the emitter at its nose. */
  override get emitter(): RaisedPoint {
    return this.place(CFG.muzzle);
  }

  override update(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') this.#enter(ctx, dt);
    else if (this.state === 'attack') this.#attack(dt);
    else this.y += CFG.exitSpeed * dt;
  }

  #enter(ctx: EnemyContext, dt: number): void {
    const left = this.y - this.stopY;
    const speed = Math.max(CREEP, CFG.entrySpeed * Math.min(1, left / CFG.brakeDistance));
    this.y = Math.max(this.stopY, this.y - speed * dt);
    if (this.y > this.stopY) return;
    this.state = 'attack';
    ctx.fireLaser(this, CFG.laser);
  }

  #attack(dt: number): void {
    const { warningSeconds, firingSeconds } = CFG.laser;
    this.#attackFor += dt;
    this.charge = Math.min(1, this.#attackFor / warningSeconds);
    if (this.#attackFor < warningSeconds + firingSeconds) return;
    this.state = 'exit';
    this.charge = 0;
  }
}
