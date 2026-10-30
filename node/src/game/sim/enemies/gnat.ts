import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import type { Path } from '../../../core/systems/enemy-motion';
import { ENEMY_CONFIG } from '../../config/enemies';

const CFG = ENEMY_CONFIG.gnat;

/**
 * P05-R01: a small swarm drone. It waits `delay` seconds, then follows its group's predefined
 * S-shaped path at a constant speed, from the top of the screen to the bottom. It does not shoot.
 */
export class Gnat extends Enemy {
  #travelled = 0;

  constructor(
    readonly path: Path,
    readonly delay: number,
  ) {
    const start = path.at(0);
    super(start.x, start.y, CFG.stats);
    this.heading = start.heading;
  }

  override update(_ctx: EnemyContext, dt: number): void {
    if (this.age <= this.delay) return;
    this.#travelled += CFG.speed * dt;
    const pose = this.path.at(this.#travelled);
    this.x = pose.x;
    this.y = pose.y;
    this.heading = pose.heading;
    if (this.#travelled >= this.path.length) this.gone = true;
  }
}
