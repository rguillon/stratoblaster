import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, DEG } from './enemy-helpers';

const CFG = ENEMY_CONFIG.spinner;

type SpinnerState = 'enter' | 'fire' | 'exit';

/**
 * P05-R06: descends to its stop height in the upper half, stops, then spins for 3 s firing a
 * spiral of bullets from its four pods (each bullet leaves outwards, so the directions turn
 * with the ring), then leaves upward. Its heading is the ring's rotation.
 */
export class Spinner extends Enemy {
  state: SpinnerState = 'enter';
  readonly #guns = new Cadence(CFG.fireInterval, 0);
  #firedFor = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats);
  }

  /** Where each pod is, and the direction it fires to. */
  pods(): { x: number; y: number; heading: number }[] {
    return Array.from({ length: CFG.pods }, (_, i) => {
      const heading = this.heading + (2 * Math.PI * i) / CFG.pods;
      return {
        x: this.x + Math.sin(heading) * CFG.podRadius,
        y: this.y + Math.cos(heading) * CFG.podRadius,
        heading,
      };
    });
  }

  override update(ctx: EnemyContext, dt: number): void {
    const spin = this.state === 'fire' ? CFG.firingSpin : CFG.idleSpin;
    this.heading += spin * DEG * dt;
    if (this.state === 'enter') {
      this.y = Math.max(this.stopY, this.y - CFG.entrySpeed * dt);
      if (this.y === this.stopY) this.state = 'fire';
    } else if (this.state === 'fire') {
      this.#fire(ctx, dt);
    } else {
      this.y += CFG.exitSpeed * dt;
    }
  }

  #fire(ctx: EnemyContext, dt: number): void {
    this.#firedFor += dt;
    this.charge = 1;
    for (let i = this.#guns.tick(dt * ctx.fireRate); i > 0; i--) {
      for (const pod of this.pods()) ctx.fireBullet(pod.x, pod.y, pod.heading, CFG.bullet);
    }
    if (this.#firedFor >= CFG.fireDuration) {
      this.state = 'exit';
      this.charge = 0;
    }
  }
}
