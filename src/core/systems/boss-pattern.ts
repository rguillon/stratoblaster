import type {
  Enemy,
  EnemyBulletSpec,
  EnemyContext,
  EnemyLaserSpec,
  EnemyMissileSpec,
  LaserOwner,
} from '../entities/enemy';
import { fanHeadings } from './enemy-motion';
import { headingTo } from './projectile-motion';

const DEG = Math.PI / 180;
/** Straight down the screen. */
const DOWN = Math.PI;

/**
 * What one volley fires (GD-43, GD-44). Angles in degrees; a preset heading of 0 is straight down,
 * positive towards the right of the screen.
 */
export type BossVolleyShape =
  /** `count` bullets in a fan `spacingDeg` apart, the middle one at the player. */
  | {
      readonly kind: 'aimed';
      readonly count: number;
      readonly spacingDeg: number;
      readonly bullet: EnemyBulletSpec;
    }
  /** `count` bullets in a fan around a preset heading. */
  | {
      readonly kind: 'fan';
      readonly headingDeg: number;
      readonly count: number;
      readonly spacingDeg: number;
      readonly bullet: EnemyBulletSpec;
    }
  /** `count` bullets all around, the ring turned by `turnDeg` more at each volley (a spiral). */
  | {
      readonly kind: 'ring';
      readonly count: number;
      readonly turnDeg: number;
      readonly bullet: EnemyBulletSpec;
    }
  /** `count` single bullets at the player, `gap` seconds apart. */
  | {
      readonly kind: 'burst';
      readonly count: number;
      readonly gap: number;
      readonly bullet: EnemyBulletSpec;
    }
  /** `count` homing missiles in a fan `spacingDeg` apart around the player's direction. */
  | {
      readonly kind: 'missiles';
      readonly count: number;
      readonly spacingDeg: number;
      readonly missile: EnemyMissileSpec;
    }
  /** A laser straight down from the piece: warning line first (GD-43). */
  | { readonly kind: 'laser'; readonly laser: EnemyLaserSpec }
  /** Enemies launched from the muzzle (e.g. a hangar's drones). */
  | { readonly kind: 'launch'; readonly launch: (x: number, y: number) => readonly Enemy[] };

/** One weapon of a stage's pattern (P07-R04). */
export interface BossVolley {
  /** What fires it: the id of a part (it stops for good once that part is destroyed) or `core`. */
  readonly from: string;
  /** Offset of the muzzle from that piece's centre (X right, Y up). */
  readonly muzzle?: readonly [number, number];
  /** Seconds between two volleys. */
  readonly every: number;
  /** Seconds before the first one, from the start of the stage; `every` when omitted. */
  readonly first?: number;
  readonly shape: BossVolleyShape;
}

/** The volleys of one stage. */
export type BossPatternSpec = readonly BossVolley[];

/** What volleys fire from: the playfield position of a piece, and the laser owner it is. */
export type VolleySource = LaserOwner & { readonly x: number; readonly y: number };

/** The piece a volley fires from, or undefined once it is destroyed. */
export type VolleySources = (from: string) => VolleySource | undefined;

/** The core fires the volleys whose `from` is this. */
export const CORE = 'core';

/**
 * A short text naming the volleys of `pattern` that still fire when only the pieces for which
 * `intact` is true remain: two stages fire the same pattern when these are equal (P07-R04).
 */
export function patternSignature(
  pattern: BossPatternSpec,
  intact: (from: string) => boolean,
): string {
  return pattern
    .filter((volley) => intact(volley.from))
    .map((volley) => JSON.stringify({ ...volley, shape: { ...volley.shape, launch: undefined } }))
    .sort()
    .join('|');
}

interface VolleyState {
  /** Seconds until the next volley. */
  left: number;
  /** Turns of a ring so far. */
  turns: number;
  /** Bullets of a burst still to fire, and seconds until the next one. */
  burst: number;
  burstLeft: number;
}

/**
 * Fires one stage's pattern (P07-R04): each volley on its own timer, from its piece, as long as
 * that piece is there. Timers run `ctx.fireRate` times faster (a level's difficulty, P06-R08).
 * Pure and deterministic.
 */
export class BossPattern {
  readonly #states: VolleyState[];

  constructor(readonly volleys: BossPatternSpec) {
    this.#states = volleys.map((v) => ({
      left: v.first ?? v.every,
      turns: 0,
      burst: 0,
      burstLeft: 0,
    }));
  }

  /** How ready the next volley is, 0..1 (for charging lights). */
  get charge(): number {
    let best = 0;
    this.volleys.forEach((volley, i) => {
      const left = this.#states[i]?.left ?? volley.every;
      best = Math.max(best, 1 - Math.min(1, left / volley.every));
    });
    return best;
  }

  step(ctx: EnemyContext, dt: number, sources: VolleySources): void {
    const time = dt * ctx.fireRate;
    this.volleys.forEach((volley, i) => {
      const state = this.#states[i];
      const source = sources(volley.from);
      if (!state || !source) return;
      state.left -= time;
      while (state.left <= 0) {
        state.left += volley.every;
        this.#fire(ctx, volley, state, source);
      }
      this.#stepBurst(ctx, volley, state, source, time);
    });
  }

  #fire(ctx: EnemyContext, volley: BossVolley, state: VolleyState, source: VolleySource): void {
    const shape = volley.shape;
    const [x, y] = muzzleOf(volley, source);
    switch (shape.kind) {
      case 'burst':
        state.burst = shape.count;
        state.burstLeft = 0;
        break;
      case 'missiles':
        for (const h of fanHeadings(
          headingTo(x, y, ctx.playerX, ctx.playerY),
          shape.count,
          shape.spacingDeg * DEG,
        )) {
          ctx.fireMissile(x, y, h, shape.missile);
        }
        break;
      case 'laser':
        ctx.fireLaser(source, shape.laser);
        break;
      case 'launch':
        for (const enemy of shape.launch(x, y)) ctx.spawn(enemy);
        break;
      default:
        for (const h of bulletHeadings(shape, state, headingTo(x, y, ctx.playerX, ctx.playerY))) {
          ctx.fireBullet(x, y, h, shape.bullet);
        }
    }
  }

  /** The bullets of a burst, `gap` seconds apart, each aimed at the player when it leaves. */
  #stepBurst(
    ctx: EnemyContext,
    volley: BossVolley,
    state: VolleyState,
    source: VolleySource,
    time: number,
  ): void {
    const shape = volley.shape;
    if (shape.kind !== 'burst') return;
    state.burstLeft -= time;
    while (state.burst > 0 && state.burstLeft <= 0) {
      const [x, y] = muzzleOf(volley, source);
      ctx.fireBullet(x, y, headingTo(x, y, ctx.playerX, ctx.playerY), shape.bullet);
      state.burst--;
      state.burstLeft += shape.gap;
    }
  }
}

/** The headings of one volley of bullets aimed at `aim`, in a preset fan, or a ring that turns. */
function bulletHeadings(
  shape: Extract<BossVolleyShape, { kind: 'aimed' | 'fan' | 'ring' }>,
  state: VolleyState,
  aim: number,
): number[] {
  if (shape.kind === 'aimed') return fanHeadings(aim, shape.count, shape.spacingDeg * DEG);
  if (shape.kind === 'fan') {
    return fanHeadings(DOWN - shape.headingDeg * DEG, shape.count, shape.spacingDeg * DEG);
  }
  const turn = state.turns++ * shape.turnDeg * DEG;
  return Array.from(
    { length: shape.count },
    (_, k) => DOWN + turn + (2 * Math.PI * k) / shape.count,
  );
}

function muzzleOf(volley: BossVolley, source: VolleySource): [number, number] {
  const [dx, dy] = volley.muzzle ?? [0, 0];
  return [source.x + dx, source.y + dy];
}
