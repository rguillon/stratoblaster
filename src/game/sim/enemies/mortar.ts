import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { VETERAN_CONFIG } from '../../config/enemies-veteran';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = VETERAN_CONFIG.mortar;

/**
 * P05-R15: a squat gunship descending slowly. Every 2.5 s it lobs a big, slow shell aimed at
 * the player (GD-44) from its barrel; 1.2 s later the shell bursts into a ring of 8 bullets
 * (a bursting bullet, `EnemyBulletSpec.burst`).
 */
export class Mortar extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.firstShot);
  readonly #muzzles = new GunMuzzles(CFG.muzzles);

  constructor(x: number, y: number) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.y -= CFG.speed * dt;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#gun.tick(dt * ctx.fireRate); i > 0; i--) {
      fireAimed(ctx, this.#muzzles, this, [1, 0], (x, y, heading) => {
        ctx.fireBullet(x, y, heading, CFG.shell);
      });
    }
    this.charge = this.#gun.progress;
  }
}
