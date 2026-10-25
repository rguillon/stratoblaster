import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { fanHeadings } from '../../../core/systems/enemy-motion';
import { GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DEG, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.strafer;

/**
 * P05-R04: crosses the top third of the screen sideways, from `side`, and fires a fan of 3
 * bullets straight down every second (preset directions -15°, 0°, +15°, GD-44), from the gun on
 * its side facing down.
 */
export class Strafer extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.fireInterval / 2);
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
    for (let i = this.#gun.tick(dt * ctx.fireRate); i > 0; i--) {
      for (const heading of fanHeadings(DOWN, CFG.fanCount, CFG.fanSpacing * DEG)) {
        const { x, y } = this.#muzzles.along(ctx, this, heading);
        ctx.fireBullet(x, y, heading, CFG.bullet);
      }
    }
    this.charge = this.#gun.progress;
  }
}
