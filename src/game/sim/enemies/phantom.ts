import { Enemy, type EnemyContext } from '../../../core/entities/enemy';
import type { ShotTarget } from '../../../core/entities/shot-target';
import { randomIn } from '../../../core/math/rng';
import { approach } from '../../../core/systems/enemy-motion';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { headingTo } from '../../../core/systems/projectile-motion';
import { VETERAN_CONFIG } from '../../config/enemies-veteran';
import { DOWN } from './enemy-helpers';

const CFG = VETERAN_CONFIG.phantom;

/** What a {@link Phantom} is doing. */
export type PhantomState = 'enter' | 'hold' | 'fadeOut' | 'hidden' | 'fadeIn' | 'exit';

/** Slowest speed while braking to its first place, px/s. */
const CREEP = 25;
/** Tries at finding a place far enough from the last one. */
const TRIES = 8;

/**
 * P05-R17: a cloaker. It comes in from the top to a place in the upper half, then three times:
 * fades out over 0.4 s, stays invisible for 0.8 s, reappears at another place in the upper half
 * (fading in over 0.4 s, its nose to the player) and fires a spread of 5 bullets 12° apart
 * centred on the player (GD-44). Then it leaves upward. While it is faded out (less than half
 * visible), shots pass through it and it cannot ram the player.
 */
export class Phantom extends Enemy {
  state: PhantomState = 'enter';
  /** How visible it is, 0 (gone) to 1, for the model. */
  opacity = 1;
  /** Reappearances so far. */
  jumps = 0;
  readonly #muzzles = new GunMuzzles(CFG.muzzles);
  #timer = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats);
    this.heading = DOWN;
  }

  /** Whether shots pass through it and it cannot ram the player. */
  get cloaked(): boolean {
    return this.opacity < CFG.solidOpacity;
  }

  /** Nothing to hit while it is cloaked. */
  override get hitTargets(): readonly ShotTarget[] {
    return this.cloaked ? [] : super.hitTargets;
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.#timer += dt;
    this.#steps[this.state](ctx, dt);
  }

  /** What it does in each state, for `dt` seconds. */
  readonly #steps: Record<PhantomState, (ctx: EnemyContext, dt: number) => void> = {
    enter: (_, dt) => {
      this.#enter(dt);
    },
    hold: (ctx) => {
      // Its attacks come faster with the level's fire rate (P06-R08).
      this.#after(CFG.hold / ctx.fireRate, this.jumps < CFG.jumps ? 'fadeOut' : 'exit');
    },
    fadeOut: () => {
      this.opacity = Math.max(0, 1 - this.#timer / CFG.fade);
      this.#after(CFG.fade, 'hidden');
    },
    hidden: (ctx) => {
      if (this.#timer >= CFG.hidden) this.#reappear(ctx);
    },
    fadeIn: (ctx) => {
      this.opacity = Math.min(1, this.#timer / CFG.fade);
      this.charge = this.opacity;
      if (this.#timer >= CFG.fade) this.#fire(ctx);
    },
    exit: (_, dt) => {
      this.y += CFG.exitSpeed * dt;
    },
  };

  #enter(dt: number): void {
    const left = this.y - this.stopY;
    const speed = Math.max(CREEP, CFG.entrySpeed * Math.min(1, left / CFG.brakeDistance));
    this.y = approach(this.y, this.stopY, speed * dt);
    if (this.y === this.stopY) this.#go('hold');
  }

  /** Goes on to `next` once `seconds` have passed in this state. */
  #after(seconds: number, next: PhantomState): void {
    if (this.#timer >= seconds) this.#go(next);
  }

  #go(state: PhantomState): void {
    this.state = state;
    this.#timer = 0;
  }

  /** Moves, unseen, to another place in the upper half, and starts fading in there. */
  #reappear(ctx: EnemyContext): void {
    const pick = () => ({
      x: randomIn(ctx.random, CFG.placeX) * ctx.width,
      y: randomIn(ctx.random, CFG.placeY) * ctx.height,
    });
    let place = pick();
    for (
      let i = 1;
      i < TRIES && Math.hypot(place.x - this.x, place.y - this.y) < CFG.jumpDistance;
      i++
    ) {
      place = pick();
    }
    this.x = place.x;
    this.y = place.y;
    this.heading = headingTo(this.x, this.y, ctx.playerX, ctx.playerY);
    this.#go('fadeIn');
  }

  #fire(ctx: EnemyContext): void {
    this.opacity = 1;
    this.charge = 0;
    this.jumps++;
    fireAimed(ctx, this.#muzzles, this, [CFG.spreadCount, CFG.spreadSpacing], (x, y, h) => {
      ctx.fireBullet(x, y, h, CFG.bullet);
    });
    this.#go('hold');
  }
}
