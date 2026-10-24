import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { headingTo } from '../../../core/systems/projectile-motion';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.scout;

/**
 * P05-R03: flies straight down slowly and fires one bullet aimed at the player every 1.5 s
 * (GD-44) while it is over the playfield.
 */
export class Scout extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.firstShot);

  constructor(x: number, y: number) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.y -= CFG.speed * dt;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#gun.tick(dt); i > 0; i--) {
      const aim = headingTo(this.x, this.y, ctx.playerX, ctx.playerY);
      ctx.fireBullet(this.x, this.y, aim, CFG.bullet);
    }
    this.charge = this.#gun.progress;
  }
}
