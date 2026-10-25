import type {
  Enemy,
  EnemyBulletSpec,
  EnemyContext,
  EnemyLaserSpec,
  EnemyMissileSpec,
} from '../entities/enemy';
import type { BossTurret } from '../entities/boss-turret';
import type { Muzzle } from '../entities/muzzle';
import { fanHeadings } from './enemy-motion';
import { fireAimed, GunMuzzles, type MuzzleSource } from './gun-muzzles';
import { headingTo, turnTowards, wrapAngle } from './projectile-motion';

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
  /** Enemies launched from the piece (e.g. a hangar's drones). */
  | { readonly kind: 'launch'; readonly launch: (x: number, y: number) => readonly Enemy[] };

/** One weapon of a stage's pattern (P07-R04). */
export interface BossVolley {
  /** What fires it: the id of a part (it stops for good once that part is destroyed) or `core`. */
  readonly from: string;
  /**
   * The muzzles of that piece's gun its shots leave from (see `MuzzleSource.place`), the one
   * furthest along each shot's way; the piece's centre when omitted.
   */
  readonly muzzles?: readonly Muzzle[];
  /**
   * Whether those muzzles are on the piece's turret (phase 7 review): they turn with it, and
   * it turns the way its next volley goes (see {@link BossPattern.turnTurrets}).
   */
  readonly turret?: boolean;
  /** Seconds between two volleys. */
  readonly every: number;
  /** Seconds before the first one, from the start of the stage; `every` when omitted. */
  readonly first?: number;
  readonly shape: BossVolleyShape;
}

/** The volleys of one stage. */
export type BossPatternSpec = readonly BossVolley[];

/**
 * What volleys fire from: the playfield position of a piece, its muzzles, the laser owner it is,
 * and the turret its guns are on, if any.
 */
export interface VolleySource extends MuzzleSource {
  readonly turret?: BossTurret | undefined;
}

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
  readonly guns: GunMuzzles;
}

/**
 * Fires one stage's pattern (P07-R04): each volley on its own timer, from its piece, as long as
 * that piece is there. Timers run `ctx.fireRate` times faster (a level's difficulty, P06-R08).
 * Pure and deterministic.
 */
export class BossPattern {
  readonly #states: VolleyState[];
  /** The pieces whose turrets its volleys fire from, and the indices of those volleys. */
  readonly #turrets = new Map<string, number[]>();

  constructor(readonly volleys: BossPatternSpec) {
    this.#states = volleys.map((v) => ({
      left: v.first ?? v.every,
      turns: 0,
      burst: 0,
      burstLeft: 0,
      guns: new GunMuzzles(v.muzzles, v.turret),
    }));
    volleys.forEach((v, i) => {
      if (v.turret) this.#turrets.set(v.from, [...(this.#turrets.get(v.from) ?? []), i]);
    });
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

  /**
   * Turns the turrets its volleys fire from for `dt` seconds (phase 7 review), the way their
   * next volley goes (a burst under way first): at the player for aimed shots and bursts, along
   * a fan's heading, and with a ring's turn, so a turret firing a spiral spins. Pauses included.
   */
  turnTurrets(ctx: EnemyContext, dt: number, sources: VolleySources): void {
    for (const [from, volleys] of this.#turrets) {
      const source = sources(from);
      const turret = source?.turret;
      if (!source || !turret) continue;
      const aim = this.#aimOf(ctx, volleys, source, turret);
      turret.aim = turnTowards(turret.aim, aim, turret.spec.turnRateDeg * DEG * dt);
    }
  }

  /** Where `turret` should point for the next of its `volleys` to fire (radians from rest). */
  #aimOf(
    ctx: EnemyContext,
    volleys: readonly number[],
    source: VolleySource,
    turret: BossTurret,
  ): number {
    const left = (i: number) => this.#states[i]?.left ?? Infinity;
    const next =
      volleys.find((i) => (this.#states[i]?.burst ?? 0) > 0) ??
      volleys.reduce((best, i) => (left(i) < left(best) ? i : best));
    const volley = this.volleys[next];
    const state = this.#states[next];
    return volley && state ? turretAim(ctx, volley, state, source, turret) : 0;
  }

  #fire(ctx: EnemyContext, volley: BossVolley, state: VolleyState, source: VolleySource): void {
    const shape = volley.shape;
    switch (shape.kind) {
      case 'burst':
        state.burst = shape.count;
        state.burstLeft = 0;
        break;
      case 'missiles':
        fireAimed(ctx, state.guns, source, [shape.count, shape.spacingDeg], (x, y, h) => {
          ctx.fireMissile(x, y, h, shape.missile);
        });
        break;
      case 'laser':
        ctx.fireLaser(state.guns.laser(source), shape.laser);
        break;
      case 'launch':
        for (const enemy of shape.launch(source.x, source.y)) ctx.spawn(enemy);
        break;
      case 'aimed':
        fireAimed(ctx, state.guns, source, [shape.count, shape.spacingDeg], (x, y, h) => {
          ctx.fireBullet(x, y, h, shape.bullet);
        });
        break;
      default:
        for (const h of presetHeadings(shape, state)) {
          const { x, y } = state.guns.along(ctx, source, h);
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
      fireAimed(ctx, state.guns, source, [1, 0], (x, y, h) => {
        ctx.fireBullet(x, y, h, shape.bullet);
      });
      state.burst--;
      state.burstLeft += shape.gap;
    }
  }
}

/** The headings of one volley of bullets in a preset fan, or a ring that turns. */
function presetHeadings(
  shape: Extract<BossVolleyShape, { kind: 'fan' | 'ring' }>,
  state: VolleyState,
): number[] {
  if (shape.kind === 'fan') {
    return fanHeadings(DOWN - shape.headingDeg * DEG, shape.count, shape.spacingDeg * DEG);
  }
  const turn = state.turns++ * shape.turnDeg * DEG;
  return Array.from(
    { length: shape.count },
    (_, k) => DOWN + turn + (2 * Math.PI * k) / shape.count,
  );
}

/** Where `turret` points for `volley` (radians from rest): see {@link BossPattern.turnTurrets}. */
function turretAim(
  ctx: EnemyContext,
  volley: BossVolley,
  state: VolleyState,
  source: VolleySource,
  turret: BossTurret,
): number {
  const shape = volley.shape;
  switch (shape.kind) {
    case 'aimed':
    case 'burst':
      return aimAtPlayer(ctx, source, turret);
    case 'fan':
      return wrapAngle(-shape.headingDeg * DEG);
    case 'ring': {
      // Spinning on from the last ring's turn to the next one's as the next one gets ready; its
      // bullets leave from the barrels pointing their way, so the closest of the ring's turns.
      const ready = 1 - Math.min(1, state.left / volley.every);
      const turn = (state.turns - 1 + ready) * shape.turnDeg * DEG;
      const spacing = (2 * Math.PI) / shape.count;
      return wrapAngle(turn + spacing * Math.round(wrapAngle(turret.aim - turn) / spacing));
    }
    default:
      return 0;
  }
}

/** How far `turret` must turn from its rest (straight down) to point at the player. */
function aimAtPlayer(ctx: EnemyContext, source: VolleySource, turret: BossTurret): number {
  const pivot = source.place?.([turret.spec.x, turret.spec.y, 0]) ?? source;
  return wrapAngle(headingTo(pivot.x, pivot.y, ctx.playerX, ctx.playerY) - DOWN);
}
