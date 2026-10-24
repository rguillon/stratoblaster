import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { fanHeadings } from '../../../core/systems/enemy-motion';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DEG, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.strafer;

/**
 * P05-R04: crosses the top third of the screen sideways, from `side`, and fires a fan of 3
 * bullets straight down every second (preset directions -15°, 0°, +15°, GD-44).
 */
export class Strafer extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.fireInterval / 2);
  readonly #direction: number;

  constructor(x: number, y: number, side: 'left' | 'right') {
    super(x, y, CFG.stats);
    this.#direction = side === 'left' ? 1 : -1;
    this.heading = (this.#direction * Math.PI) / 2;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.x += this.#direction * CFG.speed * dt;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#gun.tick(dt); i > 0; i--) {
      for (const heading of fanHeadings(DOWN, CFG.fanCount, CFG.fanSpacing * DEG)) {
        ctx.fireBullet(this.x, this.y, heading, CFG.bullet);
      }
    }
    this.charge = this.#gun.progress;
  }
}
