import type { EnemyContext } from '../../../core/entities/enemy';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { VETERAN_CONFIG } from '../../config/enemies-veteran';
import { onPlayfield } from './enemy-helpers';
import { Hornet } from './hornet';

const CFG = VETERAN_CONFIG.wasp;

/**
 * P05-R14: an armed diver. It flies down to its stop height, pauses 0.4 s turning its nose to
 * the player, fires a fan of 3 bullets 12° apart aimed at the player (GD-44) once, then dives
 * at where the player was at that moment, like a Hornet (P05-R02). The Hive launches them too
 * (P05-R23).
 */
export class Wasp extends Hornet {
  readonly #muzzles = new GunMuzzles(CFG.muzzles);

  /**
   * Comes in from (x, y) flying down to `stopY`, pauses turning to the player, fires its aimed
   * fan of 3, then dives. Already at or below `stopY`, it starts with the pause.
   */
  constructor(x: number, y: number, stopY: number) {
    super(x, y, { ...CFG, stopY: Math.min(stopY, y) });
  }

  override update(ctx: EnemyContext, dt: number): void {
    const aiming = this.state === 'aim';
    super.update(ctx, dt);
    // The pause just ended: the dive heading is the player's direction now.
    if (aiming && this.state === 'dive') this.#fire(ctx);
  }

  #fire(ctx: EnemyContext): void {
    if (!onPlayfield(this, ctx)) return;
    fireAimed(ctx, this.#muzzles, this, [CFG.fanCount, CFG.fanSpacing], (x, y, heading) => {
      ctx.fireBullet(x, y, heading, CFG.bullet);
    });
  }
}
