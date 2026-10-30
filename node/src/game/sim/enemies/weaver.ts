import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ENEMY_CONFIG } from '../../config/enemies';
import { Cadence, onPlayfield } from './enemy-helpers';

const CFG = ENEMY_CONFIG.weaver;

/**
 * P05-R05: moves down along a sine wave: its X is a sine of the distance it has come down.
 * Every 2 s it fires a pair of bullets aimed at the player, one from each hull.
 */
export class Weaver extends Enemy {
  readonly #gun = new Cadence(CFG.fireInterval, CFG.fireInterval / 2);
  /** One gun per hull, each firing its own bullet. */
  readonly #hulls = CFG.muzzles.map((muzzle) => new GunMuzzles([muzzle]));
  readonly #startY: number;

  constructor(
    readonly centerX: number,
    y: number,
  ) {
    super(centerX, y, CFG.stats);
    this.#startY = y;
  }

  /** X at a distance `down` below the start. */
  static swayAt(centerX: number, down: number): number {
    return centerX + CFG.amplitude * Math.sin((2 * Math.PI * down) / CFG.wavelength);
  }

  override update(ctx: EnemyContext, dt: number): void {
    const before = this.x;
    this.y -= CFG.speed * dt;
    this.x = Weaver.swayAt(this.centerX, this.#startY - this.y);
    this.heading = Math.atan2(this.x - before, -CFG.speed * dt);
    if (!onPlayfield(this, ctx)) return;
    for (let i = this.#gun.tick(dt * ctx.fireRate); i > 0; i--) {
      for (const hull of this.#hulls) {
        fireAimed(ctx, hull, this, [1, 0], (x, y, aim) => {
          ctx.fireBullet(x, y, aim, CFG.bullet);
        });
      }
    }
    this.charge = this.#gun.progress;
  }
}
