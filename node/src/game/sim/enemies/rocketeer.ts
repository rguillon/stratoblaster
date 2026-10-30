import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.rocketeer;

/**
 * P05-R08: descends slowly and every 3 s launches one missile from each side pod. The missiles
 * turn towards the player at a limited rate and can be shot down (GD-43). Its `charge` is how
 * far the pods are reloaded (the tips glow when loaded).
 */
export class Rocketeer extends Enemy {
  readonly #launcher = new Cadence(CFG.fireInterval, CFG.firstShot);
  readonly #pods = CFG.muzzles.map((muzzle) => new GunMuzzles([muzzle]));

  constructor(x: number, y: number) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
    this.charge = 1;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.y -= CFG.speed * dt;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#launcher.tick(dt * ctx.fireRate); i > 0; i--) {
      for (const pod of this.#pods) {
        const { x, y } = pod.along(ctx, this, DOWN);
        ctx.fireMissile(x, y, DOWN, CFG.missile);
      }
    }
    this.charge = this.#launcher.progress;
  }
}
