import type { EnemyContext } from '../../../core/entities/enemy';
import { JointedEnemy } from '../../../core/entities/jointed-enemy';
import { approach } from '../../../core/systems/enemy-motion';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { Cadence, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ELITE_CONFIG.juggernaut;

type JuggernautState = 'enter' | 'drift' | 'exit';

/**
 * P05-R22: an armoured brute. It comes down slowly to the upper third, drifts left and right for
 * 10 s, then leaves downward. Its two shoulder cannons swing to and fro (moving parts, P05-R13),
 * each firing a burst of 3 bullets along its barrel every 1.6 s; its two front plates are parts
 * too, and while one stands the core cannot be hit (a shield, as a boss's, P07-R01). The core's
 * turret fires a spread of 7 bullets 9° apart centred on the player every 2.5 s.
 */
export class Juggernaut extends JointedEnemy {
  state: JuggernautState = 'enter';
  readonly #gun = new Cadence(CFG.fireInterval, CFG.firstShot);
  readonly #muzzles = new GunMuzzles(CFG.muzzles);
  readonly #cannons = new Cadence(CFG.cannonInterval, CFG.firstBurst);
  /** Bullets left in the cannons' burst, and seconds until the next one. */
  #burstLeft = 0;
  #burstClock = 0;
  #driftFor = 0;

  constructor(
    readonly centerX: number,
    y: number,
    readonly stopY: number,
  ) {
    super(centerX, y, CFG.stats, CFG.design);
    this.heading = DOWN;
  }

  protected act(ctx: EnemyContext, dt: number): void {
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
    if (onPlayfield(this, ctx)) this.#fire(ctx, dt * ctx.fireRate);
  }

  #fire(ctx: EnemyContext, dt: number): void {
    for (let i = this.#gun.tick(dt); i > 0; i--) {
      fireAimed(ctx, this.#muzzles, this, [CFG.spreadCount, CFG.spreadSpacing], (x, y, h) => {
        ctx.fireBullet(x, y, h, CFG.bullet);
      });
    }
    this.charge = this.#gun.progress;
    if (this.#cannons.tick(dt) > 0) {
      this.#burstLeft = CFG.burstCount;
      this.#burstClock = 0;
    }
    this.#burstClock -= dt;
    while (this.#burstLeft > 0 && this.#burstClock <= 0) {
      this.#fireCannons(ctx);
      this.#burstLeft--;
      this.#burstClock += CFG.burstGap;
    }
  }

  /** Each standing shoulder cannon fires a bullet along its barrel. */
  #fireCannons(ctx: EnemyContext): void {
    for (const spec of CFG.cannons) {
      const cannon = this.part(spec.id);
      if (!cannon) continue;
      const { x, y } = ctx.seen(cannon.place(spec.muzzle));
      // Along the barrel as its joint is turned now (the part's heading is set after `act`).
      ctx.fireBullet(x, y, this.heading + this.joints.angle(spec.joint), CFG.cannonBullet);
    }
  }
}
