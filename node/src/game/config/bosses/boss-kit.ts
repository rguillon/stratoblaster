import type { BossPartSpec, BossStats } from '../../../core/entities/boss';
import type { BossJointSpec } from '../../../core/entities/boss-joint';
import type { BossTurretSpec } from '../../../core/entities/boss-turret';
import type {
  EnemyBulletSpec,
  EnemyLaserSpec,
  EnemyMissileSpec,
} from '../../../core/entities/enemy';
import type { Muzzle } from '../../../core/entities/muzzle';
import type { BossPatternSpec, BossVolley } from '../../../core/systems/boss-pattern';
import { ENEMY_UNIT } from '../enemies';
import { bossPartPoints } from '../scoring';

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
   * Its angry pattern (phase 7 review, `boss-rage.ts`): a bullet hell it fires for
   * `BOSS_TIMING.rageSeconds` after the pause that follows each destroyed part.
   */
  readonly rage?: BossPatternSpec;
  /**
   * Enemies some parts launch in every stage while they stand (a hangar's Gnats, a bay's
   * Hornets): `count` of `kind` every `every` seconds.
   */
  readonly launches?: readonly Launch[];
  /** A ring of bullets some parts burst into when destroyed (the Refinery Titan's tanks). */
  readonly breakRings?: Readonly<Record<string, { count: number; bullet: EnemyBulletSpec }>>;
  /**
   * The muzzles of the guns of its core and parts, by piece (a part id or `core`): where their
   * shots leave from (phase 7 review). Its model draws its barrels' tips there.
   */
  readonly guns: Readonly<Record<string, Guns>>;
}

/**
 * The muzzles of a piece's guns, from the boss's centre (X right, Y up, and height, px; its
 * orbiting parts as drawn, at a spin of 0), by the kind of shot they fire: bullets (`gun`), a
 * `ring` of bullets (the `gun` ones when omitted), `missile`s and `laser`s. Its `gun`s may be on
 * a `turret` turning around the pivot given (from the boss's centre, X right, Y up): it turns
 * the way they fire next (phase 7 review, D-060). Its model draws it on its own. Its `laser`s
 * are on that turret too when `turretLaser` (phase 8 review): it aims them at the player during
 * the warning line and holds still while the beam fires.
 */
export interface Guns {
  readonly turret?: readonly [x: number, y: number];
  readonly turretLaser?: boolean;
  readonly gun?: readonly Muzzle[];
  readonly ring?: readonly Muzzle[];
  readonly missile?: readonly Muzzle[];
  readonly laser?: readonly Muzzle[];
}

/** Which of a piece's {@link Guns} fire each kind of volley. */
const FIRED_BY: Readonly<
  Record<BossVolley['shape']['kind'], (guns: Guns) => readonly Muzzle[] | undefined>
> = {
  aimed: (guns) => guns.gun,
  fan: (guns) => guns.gun,
  burst: (guns) => guns.gun,
  ring: (guns) => guns.ring ?? guns.gun,
  missiles: (guns) => guns.missile,
  laser: (guns) => guns.laser,
  launch: () => [],
};

/** The muzzles `volley` fires from, among its piece's {@link Guns} (none for launches). */
export function volleyMuzzles(design: BossDesign, volley: BossVolley): readonly Muzzle[] {
  return FIRED_BY[volley.shape.kind](design.guns[volley.from] ?? {}) ?? [];
}

/** Whether `volley` fires from its piece's turret: its `gun`s (or `laser`s) when on one. */
export function volleyOnTurret(design: BossDesign, volley: BossVolley): boolean {
  const guns = design.guns[volley.from];
  if (guns?.turret === undefined) return false;
  const muzzles = volleyMuzzles(design, volley);
  return muzzles === guns.gun || (guns.turretLaser === true && muzzles === guns.laser);
}

/** The turrets of its pieces (`BossStats.turrets`), by piece. */
export function turretsOf(design: BossDesign): Record<string, BossTurretSpec> {
  const turrets: Record<string, BossTurretSpec> = {};
  for (const [piece, { turret, turretLaser }] of Object.entries(design.guns)) {
    if (!turret) continue;
    turrets[piece] = {
      x: turret[0],
      y: turret[1],
      turnRateDeg: BOSS_TIMING.turretTurnDeg,
      ...(turretLaser ? { laserTurnRateDeg: BOSS_TIMING.laserTurnDeg } : {}),
    };
  }
  return turrets;
}

/** `muzzles` mirrored left to right, for the gun on the other side. */
export const mirror = (muzzles: readonly Muzzle[]): Muzzle[] =>
  muzzles.map(([x, y, h]): Muzzle => [-x, y, h]);

/** Two muzzles side by side at `x ± gap` (or `±x`, a pair either side of the centre line). */
export const twin = (x: number, y: number, height: number, gap?: number): Muzzle[] =>
  gap === undefined
    ? [
        [x, y, height],
        [-x, y, height],
      ]
    : [
        [x - gap, y, height],
        [x + gap, y, height],
      ];

/** Missile cells in rows and columns, at the `xs` and `ys` given, all `height` high. */
export const cells = (xs: readonly number[], ys: readonly number[], height: number): Muzzle[] =>
  xs.flatMap((x) => ys.map((y): Muzzle => [x, y, height]));

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
  /**
   * It rolls into its sideways moves (phase 7 review): up to `maxDeg` at `fullSpeed` px/s
   * across (about its fastest sway), easing towards it `easePerSec` of the way a second.
   */
  roll: { maxDeg: 12, fullSpeed: 60, easePerSec: 4 },
  /** Degrees a second a turret turns at, following the player (phase 7 review). */
  turretTurnDeg: 150,
  /**
   * Degrees a second a laser turret follows the player at during the warning line (phase 8
   * review): about half as fast as the ship crosses its aim from 300 px away, so it can be
   * outrun.
   */
  laserTurnDeg: 20,
  /** Seconds a boss is angry after the pause that follows each destroyed part (phase 7 review). */
  rageSeconds: 3,
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

/**
 * A slow, big bullet of `style` that bursts into a ring of `count` small ones `after` seconds
 * from its firing (phase 8: the Aurora Station's cryo cannons).
 */
export const bursting = (
  style: string,
  speed: number,
  radius: number,
  [after, count, small]: readonly [after: number, count: number, small: EnemyBulletSpec],
): EnemyBulletSpec => ({ speed, radius, style, burst: { after, count, bullet: small } });

/** A part. */
export function part(
  id: string,
  [x, y]: readonly [number, number],
  radius: number,
  health: number,
  options: { shields?: boolean; drop?: number; orbits?: boolean; joint?: string } = {},
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
    ...(options.joint === undefined ? {} : { joint: options.joint }),
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
  /** Its moving limbs (phase 7 review): see `BossStats.joints`. */
  readonly joints?: Readonly<Record<string, BossJointSpec>>;
}): BossStats {
  return {
    model: options.id,
    name: options.name,
    radius: (options.size * L) / 2,
    coreRadius: options.coreRadius,
    health: options.coreHealth,
    points: options.points,
    partPoints: bossPartPoints(options.points),
    groundSpeed: options.groundSpeed,
    parts: options.parts,
    stagePause: BOSS_TIMING.stagePause,
    death: BOSS_TIMING.death,
    roll: BOSS_TIMING.roll,
    ...(options.coreDrop === undefined ? {} : { coreDropChance: options.coreDrop }),
    ...(options.joints === undefined ? {} : { joints: options.joints }),
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

/**
 * `volley` fired only while the part `part` stands (`needs`), or only once it is destroyed
 * (`after`): phase 8, the Fjord Lynx's radar mast.
 */
export const onlyWhile = (volley: BossVolley, part: string): BossVolley => ({
  ...volley,
  needs: part,
});
export const onlyAfter = (volley: BossVolley, part: string): BossVolley => ({
  ...volley,
  after: part,
});

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

/**
 * `design` with its lasers drawn in its own colour (phase 8 review): their style is its kind
 * id, which the laser renderer colours with the boss's neon.
 */
export function withOwnLasers(design: BossDesign): BossDesign {
  const own = (pattern: BossPatternSpec): BossPatternSpec =>
    pattern.map((v) =>
      v.shape.kind === 'laser'
        ? { ...v, shape: { ...v.shape, laser: { ...v.shape.laser, style: design.id } } }
        : v,
    );
  return {
    ...design,
    stages: design.stages.map(own),
    ...(design.rage ? { rage: own(design.rage) } : {}),
  };
}
