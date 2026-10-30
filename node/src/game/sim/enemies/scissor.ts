import type { EnemyContext, LaserOwner } from '../../../core/entities/enemy';
import { JointedEnemy, type EnemyPart } from '../../../core/entities/jointed-enemy';
import type { Muzzle, RaisedPoint } from '../../../core/entities/muzzle';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { DOWN } from './enemy-helpers';

const CFG = ELITE_CONFIG.scissor;

type ScissorState = 'enter' | 'warn' | 'fire' | 'exit';

/** Slowest speed while braking to the stop point, px/s. */
const CREEP = 20;

/** What an arm's laser leaves from and follows: the emitter at the arm's tip, along the arm. */
class ArmBeam implements LaserOwner {
  constructor(
    private readonly arm: EnemyPart,
    private readonly muzzle: Muzzle,
  ) {}

  get emitter(): RaisedPoint {
    return this.arm.place(this.muzzle);
  }

  get heading(): number {
    return this.arm.heading;
  }

  get gone(): boolean {
    return this.arm.gone;
  }

  get health(): number {
    return this.arm.health;
  }
}

/**
 * P05-R21: a long, narrow hull with two laser arms hinged at its shoulders (moving parts,
 * P05-R13), 25° out from straight down. It moves to the upper part of the screen and stops; each
 * living arm shows a warning line along it for 1 s (GD-43), then fires its laser along it for
 * 2 s while both arms swing 15° inward, the beams closing like scissors; then it backs away.
 *
 * The arms' joints only swing while the lasers fire, so the inward swing starts with the beams,
 * which sweep with their arms (`EnemyLaserSpec.sweeps`).
 */
export class Scissor extends JointedEnemy {
  state: ScissorState = 'enter';
  #attackFor = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats, CFG.design);
    this.heading = DOWN;
    this.swinging = false;
  }

  protected act(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') this.#enter(ctx, dt);
    else if (this.state === 'warn') this.#warn(dt);
    else if (this.state === 'fire') this.#fire(dt);
    else this.y += CFG.exitSpeed * dt;
  }

  #enter(ctx: EnemyContext, dt: number): void {
    const left = this.y - this.stopY;
    const speed = Math.max(CREEP, CFG.entrySpeed * Math.min(1, left / CFG.brakeDistance));
    this.y = Math.max(this.stopY, this.y - speed * dt);
    if (this.y > this.stopY) return;
    this.state = 'warn';
    this.#attackFor = 0;
    for (const arm of CFG.arms) {
      const part = this.part(arm.id);
      if (part) ctx.fireLaser(new ArmBeam(part, arm.muzzle), { ...CFG.laser, sweeps: true });
    }
  }

  #warn(dt: number): void {
    this.#attackFor += dt;
    this.charge = Math.min(1, this.#attackFor / CFG.laser.warningSeconds);
    if (this.#attackFor < CFG.laser.warningSeconds) return;
    this.state = 'fire';
    // The arms close while the beams fire.
    this.swinging = true;
  }

  #fire(dt: number): void {
    const { warningSeconds, firingSeconds } = CFG.laser;
    this.#attackFor += dt;
    if (this.#attackFor < warningSeconds + firingSeconds) return;
    this.state = 'exit';
    this.swinging = false;
    this.charge = 0;
  }
}
