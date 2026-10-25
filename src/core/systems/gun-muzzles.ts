import type { EnemyContext, LaserOwner } from '../entities/enemy';
import type { Muzzle, RaisedPoint } from '../entities/muzzle';
import { fanHeadings } from './enemy-motion';
import { headingTo } from './projectile-motion';

const DEG = Math.PI / 180;

/** What a gun fires from: an enemy or a boss's piece, and where its muzzles are now. */
export interface MuzzleSource extends LaserOwner {
  readonly x: number;
  readonly y: number;
  /**
   * Where `muzzle` is now (`Enemy.place`, `BossPiece.place`), turned with its turret when
   * `onTurret`; guns with muzzles need it.
   */
  place?(muzzle: Muzzle, onTurret?: boolean): RaisedPoint;
}

/** Muzzles closer than this to the furthest one along a shot's heading take turns. */
const TIE = 0.5;

/**
 * Where a gun's shots leave from (phase 7 review: from the barrels the player sees): the muzzle
 * furthest along each shot's way (a ring's bullets leave from the barrels pointing their way),
 * the ones side by side in turn, as the camera sees them. From the source's centre when the gun
 * has no muzzles. Muzzles `onTurret` turn with the source's turret.
 */
export class GunMuzzles {
  #next = 0;

  constructor(
    private readonly muzzles: readonly Muzzle[] = [],
    private readonly onTurret = false,
  ) {}

  /** Where a shot going towards `heading` starts, on the playfield. */
  along(ctx: EnemyContext, source: MuzzleSource, heading: number): { x: number; y: number } {
    const point = this.#pick(source, heading);
    return point ? ctx.seen(point) : { x: source.x, y: source.y };
  }

  /** The laser owner a laser fired along `source`'s heading follows: its piece, from a muzzle. */
  laser(source: MuzzleSource): LaserOwner {
    const muzzle = this.#choose(source, source.heading);
    const place = source.place?.bind(source);
    if (!muzzle || !place) return source;
    const onTurret = this.onTurret;
    return {
      get emitter() {
        return place(muzzle, onTurret);
      },
      get heading() {
        return source.heading;
      },
      get gone() {
        return source.gone;
      },
      get health() {
        return source.health;
      },
    };
  }

  #pick(source: MuzzleSource, heading: number): RaisedPoint | undefined {
    const muzzle = this.#choose(source, heading);
    return muzzle && source.place?.(muzzle, this.onTurret);
  }

  #choose(source: MuzzleSource, heading: number): Muzzle | undefined {
    if (!source.place || this.muzzles.length < 2) return this.muzzles[0];
    const [dx, dy] = [Math.sin(heading), Math.cos(heading)];
    const reach = this.muzzles.map((m) => {
      const p = source.place?.(m, this.onTurret) ?? source;
      return (p.x - source.x) * dx + (p.y - source.y) * dy;
    });
    const best = Math.max(...reach);
    const ahead = this.muzzles.filter((_, i) => (reach[i] ?? -Infinity) >= best - TIE);
    return ahead[this.#next++ % ahead.length];
  }
}

/**
 * Fires a fan of `count` shots `spacingDeg` apart around the player's direction (GD-44), each
 * from the muzzle facing its way and aimed from where it leaves.
 */
export function fireAimed(
  ctx: EnemyContext,
  guns: GunMuzzles,
  source: MuzzleSource,
  [count, spacingDeg]: readonly [number, number],
  fire: (x: number, y: number, heading: number) => void,
): void {
  const aim = headingTo(source.x, source.y, ctx.playerX, ctx.playerY);
  fanHeadings(0, count, spacingDeg * DEG).forEach((turn) => {
    const { x, y } = guns.along(ctx, source, aim + turn);
    fire(x, y, headingTo(x, y, ctx.playerX, ctx.playerY) + turn);
  });
}
