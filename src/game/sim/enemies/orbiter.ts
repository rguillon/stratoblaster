import type { EnemyContext } from '../../../core/entities/enemy';
import { JointedEnemy } from '../../../core/entities/jointed-enemy';
import { approach } from '../../../core/systems/enemy-motion';
import { GunMuzzles } from '../../../core/systems/gun-muzzles';
import { headingTo } from '../../../core/systems/projectile-motion';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { Cadence, DEG, DOWN, onPlayfield } from './enemy-helpers';

const CFG = ELITE_CONFIG.orbiter;

type OrbiterState = 'enter' | 'stay' | 'exit';

/**
 * P05-R20: a spherical core with three armoured drones orbiting it (moving parts, P05-R13),
 * close enough to catch the shots aimed at the core. It comes down to the upper half, stays 8 s,
 * then leaves upward. Every 3 s the core fires a ring of 12 bullets from its equator; each drone
 * fires a bullet aimed at the player every 2 s, in turn.
 */
export class Orbiter extends JointedEnemy {
  state: OrbiterState = 'enter';
  readonly #ring = new Cadence(CFG.ringInterval, CFG.firstRing);
  readonly #ringMuzzles = new GunMuzzles(CFG.ringMuzzles);
  readonly #drones = CFG.drones.map((d) => new Cadence(CFG.droneFireInterval, d.firstShot));
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
    this.spin += CFG.spin * DEG * dt;
    if (this.state === 'enter') {
      this.y = approach(this.y, this.stopY, CFG.entrySpeed * dt);
      if (this.y === this.stopY) this.state = 'stay';
    } else if (this.state === 'stay') {
      this.#stayed += dt;
      if (this.#stayed >= CFG.stay) this.state = 'exit';
    } else {
      this.y += CFG.exitSpeed * dt;
    }
    if (onPlayfield(this, ctx)) this.#fire(ctx, dt * ctx.fireRate);
  }

  #fire(ctx: EnemyContext, dt: number): void {
    for (let i = this.#ring.tick(dt); i > 0; i--) {
      for (let k = 0; k < CFG.ringCount; k++) {
        const heading = this.heading + (2 * Math.PI * k) / CFG.ringCount;
        const { x, y } = this.#ringMuzzles.along(ctx, this, heading);
        ctx.fireBullet(x, y, heading, CFG.ringBullet);
      }
    }
    this.charge = this.#ring.progress;
    CFG.drones.forEach((spec, i) => {
      const times = this.#drones[i]?.tick(dt) ?? 0;
      const drone = this.part(spec.id);
      if (!drone) return;
      for (let k = times; k > 0; k--) {
        const { x, y } = ctx.seen(drone.place(spec.muzzle));
        ctx.fireBullet(x, y, headingTo(x, y, ctx.playerX, ctx.playerY), CFG.droneBullet);
      }
    });
  }
}
