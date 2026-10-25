import type { BossPartSpec, BossStats } from '../../../core/entities/boss';
import type {
  EnemyBulletSpec,
  EnemyLaserSpec,
  EnemyMissileSpec,
} from '../../../core/entities/enemy';
import type { BossPatternSpec, BossVolley } from '../../../core/systems/boss-pattern';
import { ENEMY_UNIT } from '../enemies';

/*
 * Building blocks of the World 1 bosses (P07-R05). Logical pixels with X right and Y up, from
 * the boss's centre; the boss faces down the screen, so its nose is at -Y and its tail at +Y.
 * Times in seconds, angles in degrees, speeds in px/s.
 */

/** `L`, the length of the medium player ship (as for the enemies). */
export const L = ENEMY_UNIT;

/** A boss's design: its numbers, how it comes in and moves, and its stages (P07-R04). */
export interface BossDesign {
  /** Kind id and model key. */
  readonly id: string;
  readonly stats: BossStats;
  /** Height where it stops coming down, as a fraction of the playfield's height. */
  readonly stopFraction: number;
  /**
   * Once in place it sways left and right by up to `amplitude` (less when its parts would leave
   * the ship's reach, P07-R05) and bobs up and down by `bob`.
   */
  readonly sway: { readonly amplitude: number; readonly period: number };
  readonly bob: { readonly amplitude: number; readonly period: number };
  /** Radians a second its orbiting parts turn (`BossPartSpec.orbits`). */
  readonly spinRate?: number;
  /** One pattern per stage: `stages[k]` once `k` parts are destroyed. */
  readonly stages: readonly BossPatternSpec[];
  /**
   * Enemies some parts launch in every stage while they stand (a hangar's Gnats, a bay's
   * Hornets): `count` of `kind` every `every` seconds.
   */
  readonly launches?: readonly Launch[];
  /** A ring of bullets some parts burst into when destroyed (the Refinery Titan's tanks). */
  readonly breakRings?: Readonly<Record<string, { count: number; bullet: EnemyBulletSpec }>>;
}

/** Phase 5 enemies a boss's part launches (see {@link BossDesign.launches}). */
export interface Launch {
  readonly from: string;
  readonly kind: 'gnats' | 'hornets';
  readonly count: number;
  readonly every: number;
  readonly first?: number;
}

/** Shared timings of every boss (tunable values of P07). */
export const BOSS_TIMING = {
  /** No fire for this long after a part is destroyed (P07-R04, `stage_change_pause`). */
  stagePause: 1,
  /** Blasts over the hull for about 2 s, then the big one (P07-R06). */
  death: { seconds: 2, every: 0.16 },
  /** How far above the top edge a boss appears, and how fast it comes in (about 3 s). */
  spawnMargin: 30,
  entrySpeed: 75,
  /** Speed it eases into its place at, and the distance over which it brakes. */
  brakeDistance: 60,
} as const;

/** Enemy bullets in a style of `enemy-look.ts`. */
export const bullet = (style: string, speed: number, radius = 4): EnemyBulletSpec => ({
  speed,
  radius,
  style,
});

/** Boss missiles: like the Rocketeer's, and shot down the same way (GD-43). */
export const MISSILE: EnemyMissileSpec = {
  speed: 140,
  turnRateDeg: 80,
  homingSeconds: 3,
  radius: 5,
  health: 10,
  style: 'rocketeer',
};

/** Boss lasers: the Lancer's, with its 1 s warning line (GD-43). */
export const laserOf = (firingSeconds: number, width = 12): EnemyLaserSpec => ({
  warningSeconds: 1,
  firingSeconds,
  width,
  style: 'lancer',
});

/** A part. */
export function part(
  id: string,
  [x, y]: readonly [number, number],
  radius: number,
  health: number,
  options: { shields?: boolean; drop?: number; orbits?: boolean } = {},
): BossPartSpec {
  return {
    id,
    x,
    y,
    radius,
    health,
    shieldsCore: options.shields ?? true,
    dropChance: options.drop ?? 0.5,
    ...(options.orbits ? { orbits: true } : {}),
  };
}

/** The numbers of a boss of `size` L across. */
export function stats(options: {
  readonly id: string;
  readonly name: string;
  readonly size: number;
  readonly coreRadius: number;
  readonly coreHealth: number;
  readonly points: number;
  readonly groundSpeed: number;
  readonly parts: readonly BossPartSpec[];
  readonly coreDrop?: number;
}): BossStats {
  return {
    model: options.id,
    name: options.name,
    radius: (options.size * L) / 2,
    coreRadius: options.coreRadius,
    health: options.coreHealth,
    points: options.points,
    groundSpeed: options.groundSpeed,
    parts: options.parts,
    stagePause: BOSS_TIMING.stagePause,
    death: BOSS_TIMING.death,
    ...(options.coreDrop === undefined ? {} : { coreDropChance: options.coreDrop }),
  };
}

/**
 * The stages of a boss: the parts' volleys in every stage (each stops with its part), and the
 * core's own volleys, one list per stage. The core's volleys differ from a stage to the next, so
 * every stage fires another pattern (P07-R04).
 */
export function stages(
  parts: readonly BossVolley[],
  core: readonly (readonly BossVolley[])[],
): BossPatternSpec[] {
  return core.map((own) => [...parts, ...own]);
}

/** Volleys, `from` a part id or `core`. `first` defaults to `every`. */
export const volley = {
  aimed: (
    from: string,
    every: number,
    count: number,
    spacingDeg: number,
    b: EnemyBulletSpec,
    first?: number,
  ): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'aimed', count, spacingDeg, bullet: b },
  }),
  fan: (
    from: string,
    every: number,
    count: number,
    spacingDeg: number,
    b: EnemyBulletSpec,
    first?: number,
    headingDeg = 0,
  ): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'fan', headingDeg, count, spacingDeg, bullet: b },
  }),
  ring: (
    from: string,
    every: number,
    count: number,
    turnDeg: number,
    b: EnemyBulletSpec,
    first?: number,
  ): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'ring', count, turnDeg, bullet: b },
  }),
  burst: (
    from: string,
    every: number,
    count: number,
    gap: number,
    b: EnemyBulletSpec,
    first?: number,
  ): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'burst', count, gap, bullet: b },
  }),
  missiles: (
    from: string,
    every: number,
    count: number,
    spacingDeg: number,
    first?: number,
  ): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'missiles', count, spacingDeg, missile: MISSILE },
  }),
  laser: (from: string, every: number, firingSeconds: number, first?: number): BossVolley => ({
    from,
    every,
    ...(first === undefined ? {} : { first }),
    shape: { kind: 'laser', laser: laserOf(firingSeconds) },
  }),
};
