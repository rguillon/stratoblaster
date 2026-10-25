import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { approach } from '../../../core/systems/enemy-motion';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.bulwark;

type BulwarkState = 'enter' | 'drift' | 'exit';

/**
 * P05-R09: a heavy gunship. It comes down slowly to the upper third, drifts left and right for
 * 8 s, then leaves downward. Every 2 s it fires a spread of 5 bullets 10° apart, the middle one
 * aimed at the player (GD-44), from the twin cannon on its tower.
 */
export class Bulwark extends Enemy {
  state: BulwarkState = 'enter';
  readonly #gun = new Cadence(CFG.fireInterval, CFG.fireInterval / 2);
  readonly #muzzles = new GunMuzzles(CFG.muzzles);
  #driftFor = 0;

  constructor(
    readonly centerX: number,
    y: number,
    readonly stopY: number,
  ) {
    super(centerX, y, CFG.stats);
    this.heading = DOWN;
  }

  override update(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') {
      this.y = approach(this.y, this.stopY, CFG.entrySpeed * dt);
      if (this.y === this.stopY) this.state = 'drift';
    } else if (this.state === 'drift') {
      this.#driftFor += dt;
      this.x =
        this.centerX + CFG.drift * Math.sin((2 * Math.PI * this.#driftFor) / CFG.driftPeriod);
      if (this.#driftFor >= CFG.stay) this.state = 'exit';
    } else {
      this.y -= CFG.exitSpeed * dt;
    }
    if (onPlayfield(this, ctx)) this.#fire(ctx, dt);
  }

  #fire(ctx: EnemyContext, dt: number): void {
    for (let i = this.#gun.tick(dt * ctx.fireRate); i > 0; i--) {
      fireAimed(ctx, this.#muzzles, this, [CFG.spreadCount, CFG.spreadSpacing], (x, y, h) => {
        ctx.fireBullet(x, y, h, CFG.bullet);
      });
    }
    this.charge = this.#gun.progress;
  }
}
