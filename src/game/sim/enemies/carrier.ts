import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { Path, type PathPoint } from '../../../core/systems/enemy-motion';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';
import { Gnat } from './gnat';

const CFG = ENEMY_CONFIG.carrier;
const GROUP_DELAY = ENEMY_CONFIG.gnat.groupDelay;

/**
 * P05-R12: a fat flying carrier. It descends slowly and never shoots; every 3 s a Gnat comes out
 * of each of its side ports (two a side), flying out sideways and then down the screen. It stops
 * launching in the lower part of the screen. Its `charge` is how close the next launch is (the
 * ports glow).
 */
export class Carrier extends Enemy {
  readonly #launcher = new Cadence(CFG.launchInterval, CFG.firstLaunch);

  constructor(x: number, y: number) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.y -= CFG.speed * dt;
    if (!onPlayfield(this, ctx) || this.y < CFG.lastLaunchFraction * ctx.height) {
      this.charge = 0;
      return;
    }
    for (let i = this.#launcher.tick(dt); i > 0; i--) this.#launch(ctx);
    this.charge = this.#launcher.progress;
  }

  #launch(ctx: EnemyContext): void {
    for (const side of [-1, 1]) {
      CFG.ports.forEach(([px, py], i) => {
        const [x0, y0] = [this.x + side * px, this.y + py];
        const path = new Path(CFG.launchPath.map(([x, y]): PathPoint => [x0 + side * x, y0 + y]));
        ctx.spawn(new Gnat(path, i * GROUP_DELAY));
      });
    }
  }
}
