import type { EnemyContext } from '../../../core/entities/enemy';
import {
  JointedEnemy,
  type EnemyPart,
  type JointedDesign,
} from '../../../core/entities/jointed-enemy';
import type { Muzzle } from '../../../core/entities/muzzle';
import { fireAimed, GunMuzzles } from '../../../core/systems/gun-muzzles';
import { VETERAN_CONFIG } from '../../config/enemies-veteran';
import { Cadence, DEG, DOWN, onPlayfield } from './enemy-helpers';

const CFG = VETERAN_CONFIG.mantis;
const ARM = CFG.arm;

/** The arms' sides, by sign (-1 left, 1 right). */
const SIDE_NAMES = { [-1]: 'left', 1: 'right' } as const;

/** The arm on the side `s` (1 right, -1 left): its shoulder joint and the blade hanging on it. */
function armDesign(s: 1 | -1) {
  const side = SIDE_NAMES[s];
  const out = s * ARM.outDeg * DEG;
  const [sx, sy] = [s * CFG.shoulder[0], CFG.shoulder[1]];
  return {
    joint: [
      `${side}-shoulder`,
      // Out of step: the right arm a quarter swing behind the left one.
      { x: sx, y: sy, swing: { ...ARM.swing, phase: s === 1 ? 0.25 : 0 } },
    ] as const,
    part: {
      id: `${side}-arm`,
      x: sx + Math.sin(out) * ARM.centre,
      y: sy - Math.cos(out) * ARM.centre,
      radius: ARM.radius,
      health: ARM.health,
      joint: `${side}-shoulder`,
      // Clockwise on screen from its nose: turned out to its side.
      aim: -out,
    },
  };
}

const ARMS = [armDesign(-1), armDesign(1)];

/** P05-R16: the Mantis's two scythe arms, each on its shoulder (P05-R13). */
export const MANTIS_DESIGN: JointedDesign = {
  joints: Object.fromEntries(ARMS.map((a) => a.joint)),
  parts: ARMS.map((a) => a.part),
};

type MantisState = 'enter' | 'stay' | 'exit';

/** Slowest speed while braking to its stop, px/s. */
const CREEP = 20;

/**
 * P05-R16: an insect-like hull with two scythe arms (moving parts, P05-R13) swinging out and in,
 * out of step. It comes down to the upper half, stops for 6 s, then leaves downward. While it is
 * stopped, each standing arm fires a pair of bullets straight along its blade every 1.2 s, so
 * its shots sweep as the arm swings; its head fires a bullet aimed at the player every 2 s.
 */
export class Mantis extends JointedEnemy {
  state: MantisState = 'enter';
  readonly #arms = new Cadence(ARM.fireInterval, ARM.fireInterval / 2);
  readonly #head = new Cadence(CFG.head.fireInterval, CFG.head.firstShot);
  readonly #headMuzzles = new GunMuzzles(CFG.head.muzzles);
  #stayed = 0;

  constructor(
    x: number,
    y: number,
    readonly stopY: number,
  ) {
    super(x, y, CFG.stats, MANTIS_DESIGN);
    this.heading = DOWN;
  }

  protected act(ctx: EnemyContext, dt: number): void {
    if (this.state === 'enter') this.#enter(dt);
    else if (this.state === 'stay') this.#stay(ctx, dt);
    else this.y -= CFG.exitSpeed * dt;
    if (onPlayfield(this, ctx)) this.#fireHead(ctx, dt);
  }

  #enter(dt: number): void {
    const left = this.y - this.stopY;
    const speed = Math.max(CREEP, CFG.entrySpeed * Math.min(1, left / CFG.brakeDistance));
    this.y = Math.max(this.stopY, this.y - speed * dt);
    if (this.y === this.stopY) this.state = 'stay';
  }

  #stay(ctx: EnemyContext, dt: number): void {
    this.#stayed += dt;
    for (let i = this.#arms.tick(dt * ctx.fireRate); i > 0; i--) {
      for (const s of [-1, 1] as const) this.#fireArm(ctx, s);
    }
    this.charge = this.#arms.progress;
    if (this.#stayed < CFG.stay) return;
    this.state = 'exit';
    this.charge = 0;
  }

  /** The arm on side `s` fires its pair straight along its blade, if it still stands. */
  #fireArm(ctx: EnemyContext, s: 1 | -1): void {
    const side = SIDE_NAMES[s];
    const arm: EnemyPart | undefined = this.part(`${side}-arm`);
    if (!arm) return;
    const muzzles: readonly Muzzle[] = ARM.muzzles[side];
    for (const muzzle of muzzles) {
      const { x, y } = ctx.seen(arm.place(muzzle));
      ctx.fireBullet(x, y, arm.heading, ARM.bullet);
    }
  }

  #fireHead(ctx: EnemyContext, dt: number): void {
    for (let i = this.#head.tick(dt * ctx.fireRate); i > 0; i--) {
      fireAimed(ctx, this.#headMuzzles, this, [1, 0], (x, y, heading) => {
        ctx.fireBullet(x, y, heading, CFG.head.bullet);
      });
    }
  }
}
