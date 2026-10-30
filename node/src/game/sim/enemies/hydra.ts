import type { EnemyContext } from '../../../core/entities/enemy';
import { JointedEnemy } from '../../../core/entities/jointed-enemy';
import { approach } from '../../../core/systems/enemy-motion';
import { headingTo } from '../../../core/systems/projectile-motion';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ELITE_CONFIG.hydra;

type HydraState = 'enter' | 'stay' | 'exit';

/**
 * P05-R19: a broad hull with three long necks swaying out of step (moving parts, P05-R13). It
 * comes down to the upper third, stays 7 s, then leaves downward. Its heads fire in turn, one
 * every 0.5 s, each a bullet aimed at the player from its eye; with every head gone it no
 * longer fires, but its hull can still be destroyed.
 */
export class Hydra extends JointedEnemy {
  state: HydraState = 'enter';
  readonly #heads = new Cadence(CFG.headFireInterval, CFG.firstShot);
  /** Index of the head whose turn it is. */
  #next = 0;
  #stayed = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats, CFG.design);
    this.heading = DOWN;
  }

  protected act(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') {
      this.y = approach(this.y, this.stopY, CFG.entrySpeed * dt);
      if (this.y === this.stopY) this.state = 'stay';
    } else if (this.state === 'stay') {
      this.#stayed += dt;
      if (this.#stayed >= CFG.stay) this.state = 'exit';
    } else {
      this.y -= CFG.exitSpeed * dt;
    }
    if (onPlayfield(this, ctx)) this.#fire(ctx, dt);
  }

  #fire(ctx: EnemyContext, dt: number): void {
    for (let i = this.#heads.tick(dt * ctx.fireRate); i > 0; i--) this.#fireNextHead(ctx);
    this.charge = this.#heads.progress;
  }

  /** The next living head in turn fires a bullet at the player from its eye. */
  #fireNextHead(ctx: EnemyContext): void {
    const heads = CFG.heads;
    for (let k = 0; k < heads.length; k++) {
      const index = (this.#next + k) % heads.length;
      const spec = heads[index];
      const head = spec && this.part(spec.id);
      if (!spec || !head) continue;
      this.#next = index + 1;
      const { x, y } = ctx.seen(head.place(spec.muzzle));
      ctx.fireBullet(x, y, headingTo(x, y, ctx.playerX, ctx.playerY), CFG.bullet);
      return;
    }
  }
}
