import type { EnemyContext } from '../../../core/entities/enemy';
import { JointedEnemy } from '../../../core/entities/jointed-enemy';
import { muzzlePoint } from '../../../core/entities/muzzle';
import { GunMuzzles } from '../../../core/systems/gun-muzzles';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { Cadence, DEG, DOWN, onPlayfield } from './enemy-helpers';
import { Wasp } from './wasp';

const CFG = ELITE_CONFIG.hive;

/**
 * P05-R23: a huge rounded hive-ship with a launch ring turning on its back (its `spin`; it has no
 * destroyable parts). It flies slowly straight down the screen and leaves at the bottom. Every
 * 4 s a Wasp (P05-R14) comes out of the hatch on its ring and attacks; every 3 s it fires a ring
 * of 12 bullets from the vents around its rim. It stops launching and firing in the lower part
 * of the screen. Its `charge` is how close the next launch is.
 */
export class Hive extends JointedEnemy {
  readonly #launcher = new Cadence(CFG.launchInterval, CFG.firstLaunch);
  readonly #ring = new Cadence(CFG.ringInterval, CFG.firstRing);
  readonly #ringMuzzles = new GunMuzzles(CFG.ringMuzzles);

  constructor(x: number, y: number) {
    super(x, y, CFG.stats, CFG.design);
    this.heading = DOWN;
  }

  /** Where the ring's hatch is now, as the camera sees it on the playfield. */
  hatch(ctx: EnemyContext): { x: number; y: number } {
    return ctx.seen(muzzlePoint(this, CFG.port, this.spin));
  }

  protected act(ctx: EnemyContext, dt: number): void {
    this.spin += CFG.ringSpin * DEG * dt;
    this.y -= CFG.speed * dt;
    if (!onPlayfield(this, ctx) || this.y < CFG.lastFraction * ctx.height) {
      this.charge = 0;
      return;
    }
    for (let i = this.#launcher.tick(dt); i > 0; i--) {
      const { x, y } = this.hatch(ctx);
      ctx.spawn(new Wasp(x, y, y - CFG.launchDrop));
    }
    this.charge = this.#launcher.progress;
    for (let i = this.#ring.tick(dt * ctx.fireRate); i > 0; i--) {
      for (let k = 0; k < CFG.ringCount; k++) {
        const heading = this.heading + (2 * Math.PI * k) / CFG.ringCount;
        const { x, y } = this.#ringMuzzles.along(ctx, this, heading);
        ctx.fireBullet(x, y, heading, CFG.ringBullet);
      }
    }
  }
}
