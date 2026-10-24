import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import type { Path } from '../../../core/systems/enemy-motion';
import { headingTo } from '../../../core/systems/projectile-motion';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, onPlayfield } from './enemy-helpers';
import { Hornet } from './hornet';

const CFG = ENEMY_CONFIG.splitter;
const POD = ENEMY_CONFIG.splitterPod;

/**
 * P05-R10: flies down a predefined curved path and fires one aimed bullet every 2.5 s. When it
 * is destroyed its three pods break off, and each dives at the player like a small Hornet.
 */
export class Splitter extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.firstShot);
  #travelled = 0;

  constructor(readonly path: Path) {
    const start = path.at(0);
    super(start.x, start.y, CFG.stats);
    this.heading = start.heading;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.#travelled += CFG.speed * dt;
    const pose = this.path.at(this.#travelled);
    this.x = pose.x;
    this.y = pose.y;
    this.heading = pose.heading;
    if (this.#travelled >= this.path.length) this.gone = true;
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#gun.tick(dt * ctx.fireRate); i > 0; i--) {
      ctx.fireBullet(
        this.x,
        this.y,
        headingTo(this.x, this.y, ctx.playerX, ctx.playerY),
        CFG.bullet,
      );
    }
    this.charge = this.#gun.progress;
  }

  /** The three pods, 120° apart around the core, each facing outwards. */
  override onDestroyed(ctx: EnemyContext): void {
    for (let i = 0; i < 3; i++) {
      const heading = this.heading + (2 * Math.PI * i) / 3;
      const x = this.x + Math.sin(heading) * CFG.podOffset;
      const y = this.y + Math.cos(heading) * CFG.podOffset;
      const pod = new Hornet(x, y, POD);
      pod.heading = heading;
      ctx.spawn(pod);
    }
  }
}
