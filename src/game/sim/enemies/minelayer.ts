import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { GunMuzzles } from '../../../core/systems/gun-muzzles';
import { VETERAN_CONFIG } from '../../config/enemies-veteran';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = VETERAN_CONFIG.minelayer;

/**
 * P05-R18: crosses the top half of the screen sideways from `side`, like a Strafer (P05-R04).
 * Every 0.8 s it drops a mine from its belly rack: a slow bullet drifting down that bursts into
 * a ring of 6 bullets 1.5 s later (`EnemyBulletSpec.burst`).
 */
export class Minelayer extends Enemy {
  readonly #rack = new Cadence(CFG.dropInterval, CFG.firstDrop);
  readonly #muzzles = new GunMuzzles(CFG.muzzles);
  readonly #direction: number;

  constructor(x: number, y: number, side: 'left' | 'right') {
    super(x, y, CFG.stats);
    this.#direction = side === 'left' ? 1 : -1;
    this.heading = (this.#direction * Math.PI) / 2;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.x += this.#direction * CFG.speed * dt;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#rack.tick(dt * ctx.fireRate); i > 0; i--) {
      // The rack's hatches take turns.
      const { x, y } = this.#muzzles.along(ctx, this, DOWN);
      ctx.fireBullet(x, y, DOWN, CFG.mine);
    }
    this.charge = this.#rack.progress;
  }
}
