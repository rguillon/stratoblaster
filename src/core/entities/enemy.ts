import type { Random } from '../math/rng';
import { muzzlePoint, type Muzzle, type RaisedPoint } from './muzzle';
import type { ShotTarget } from './shot-target';

/**
 * Enemies (P05). Positions are playfield logical pixels, X to the right, Y up; headings are in
 * radians from +Y, positive to the right (π points straight down, towards the player's side).
 */

/** A bullet an enemy fires: it flies straight at constant speed. */
export interface EnemyBulletSpec {
  readonly speed: number;
  /** Hit radius. */
  readonly radius: number;
  /** Look of the bullet, a key the game's enemy shot renderer knows. */
  readonly style: string;
  /**
   * A bullet that bursts (phase 8): `after` seconds from its firing it is gone, and `count`
   * bullets of `bullet` leave from where it was, evenly all around, the first one on its way.
   */
  readonly burst?: {
    readonly after: number;
    readonly count: number;
    readonly bullet: EnemyBulletSpec;
  };
}

/** A missile an enemy launches: it turns towards the player for a while and can be shot down. */
export interface EnemyMissileSpec {
  readonly speed: number;
  /** Degrees per second. */
  readonly turnRateDeg: number;
  /** Seconds it homes on the player before it flies straight on. */
  readonly homingSeconds: number;
  readonly radius: number;
  readonly health: number;
  readonly style: string;
}

/** A laser an enemy fires straight along its heading: a warning line first, then the beam. */
export interface EnemyLaserSpec {
  readonly warningSeconds: number;
  readonly firingSeconds: number;
  /** Width of the beam. */
  readonly width: number;
  readonly style: string;
}

/**
 * What a laser leaves from and follows (an enemy, or a part of a boss): it fires along
 * `heading` from `emitter` (as the camera sees it when it is raised above the playfield,
 * {@link EnemyContext.seen}), and stops once its owner is gone or has no health left.
 */
export interface LaserOwner {
  readonly emitter: { readonly x: number; readonly y: number; readonly height?: number };
  readonly heading: number;
  readonly gone: boolean;
  readonly health: number;
}

/**
 * Something destroyed that may drop a bonus: a shot target with, optionally, its own chance
 * (0..1) of dropping one instead of the game's rule (P07-R07).
 */
export interface DropSource extends ShotTarget {
  readonly dropChance?: number | undefined;
}

/** What an enemy can see and do while it updates. */
export interface EnemyContext {
  /** The playfield spans X in [0, width] and Y in [0, height]. */
  readonly width: number;
  readonly height: number;
  /** Centre of the player ship. */
  readonly playerX: number;
  readonly playerY: number;
  readonly random: Random;
  /**
   * How fast attacks come, as a factor on each kind's own timing (1 = as tuned). Enemies run
   * their attack timers this much faster (a level's difficulty, P06-R08).
   */
  readonly fireRate: number;
  /**
   * Where shots must start to look as if they left from `point`, above the playfield (a gun's
   * muzzle, see `muzzle.ts`): the point of the playfield the camera sees behind it.
   */
  seen(point: RaisedPoint): { x: number; y: number };
  fireBullet(x: number, y: number, heading: number, spec: EnemyBulletSpec): void;
  fireMissile(x: number, y: number, heading: number, spec: EnemyMissileSpec): void;
  /** Fires a laser from `owner`'s emitter (e.g. {@link Enemy.emitter}), which it follows. */
  fireLaser(owner: LaserOwner, spec: EnemyLaserSpec): void;
  /** Adds another enemy (e.g. parts that break off), updated from the next step. */
  spawn(enemy: Enemy): void;
  /** An explosion of size `radius` at (x, y), e.g. one of a dying boss's blasts (GD-62). */
  explode(x: number, y: number, radius: number): void;
  /**
   * A piece of the enemy the player's shots destroyed (a boss's part, P07-R01): it blows up,
   * and may drop a bonus (P07-R07).
   */
  breakPart(part: DropSource): void;
}

/** Fixed numbers of an enemy kind. */
export interface EnemyStats {
  /** Key of the enemy's model in the game view. */
  readonly model: string;
  /** Hit radius (GD-21: about the size of the model). */
  readonly radius: number;
  readonly health: number;
  /** Points scored when it is destroyed (GD-50). */
  readonly points: number;
}

/**
 * Base of every enemy (GD-45): a circle with health that the player's shots can hit, moved and
 * armed by {@link update}. Concrete enemies live in the game; the engine only steps them.
 */
export abstract class Enemy implements ShotTarget, LaserOwner {
  /** Set by the world when the enemy is added. */
  id = 0;
  readonly radius: number;
  health: number;
  readonly maxHealth: number;
  readonly model: string;
  readonly points: number;
  /** Direction the nose points to. */
  heading = Math.PI;
  /** Seconds since the enemy was added. */
  age = 0;
  /** How ready the next attack is, 0..1, for the visuals (e.g. a charging light). */
  charge = 0;
  /** Set when the enemy is done (left for good); the world then removes it. */
  gone = false;
  /**
   * Whether the world removes it once it has left the playfield or is too old (a boss stays
   * until it is destroyed).
   */
  readonly expires: boolean = true;
  /** Whether ramming the player hurts it (not a boss, P07-R06). */
  readonly rammable: boolean = true;
  /** Its own chance of dropping a bonus when destroyed; the game's rule when undefined. */
  readonly dropChance: number | undefined = undefined;
  readonly #self: readonly ShotTarget[] = [this];

  constructor(
    public x: number,
    public y: number,
    stats: EnemyStats,
  ) {
    this.radius = stats.radius;
    this.health = stats.health;
    this.maxHealth = stats.health;
    this.model = stats.model;
    this.points = stats.points;
  }

  /** Where `muzzle`, one of its guns' (see `muzzle.ts`), is now: it turns with its nose. */
  place(muzzle: Muzzle): RaisedPoint {
    return muzzlePoint(this, muzzle);
  }

  /** Where its laser leaves from. Defaults to the nose, one radius ahead of the centre. */
  get emitter(): { readonly x: number; readonly y: number } {
    return {
      x: this.x + Math.sin(this.heading) * this.radius,
      y: this.y + Math.cos(this.heading) * this.radius,
    };
  }

  /**
   * What the player's shots can hit and the player can bump into: the enemy itself, or e.g. a
   * boss's parts and core (P07-R01). Empty when nothing of it can be hit.
   */
  get hitTargets(): readonly ShotTarget[] {
    return this.#self;
  }

  /**
   * What the player's shots can hit: its {@link hitTargets}, unless some of them let shots
   * through (e.g. a boss's shielded core, phase 7 review).
   */
  get shotTargets(): readonly ShotTarget[] {
    return this.hitTargets;
  }

  /** Moves and attacks for `dt` seconds. `age` is already advanced. */
  abstract update(ctx: EnemyContext, dt: number): void;

  /** Called once when the player destroys it, if defined. */
  onDestroyed?(ctx: EnemyContext): void;
}

/** An edge of the playfield enemies come in from. */
export type EnemySide = 'top' | 'left' | 'right';

/**
 * Where a group comes in (P06-R07): an edge, and a position along it as a fraction (0..1) of
 * that edge, from the left for the top edge and from the bottom for the side edges.
 */
export interface EnemyEntry {
  readonly side: EnemySide;
  readonly position: number;
}

/** Where a group of enemies may appear. */
export interface EnemySpawnArea {
  readonly width: number;
  readonly height: number;
  readonly random: Random;
  /**
   * Where the group should come in (a wave script's choice). Kinds follow it as far as their
   * movement allows; without it they pick at random.
   */
  readonly entry?: EnemyEntry;
  /**
   * X range (logical pixels) that enemies coming in from the top keep to (phase 6 review): what
   * the player can reach at the bottom of a tilted view, so none comes too far in an upper
   * corner to be shot. Default: the whole width.
   */
  readonly topRange?: readonly [number, number];
}

/** A kind of enemy a game offers: a name, and how one group of it appears (P05). */
export interface EnemyKindDefinition {
  /** Stable identifier. */
  readonly id: string;
  readonly name: string;
  /** Creates one group of this kind (one enemy, or e.g. a swarm), just outside the playfield. */
  spawn(area: EnemySpawnArea): Enemy[];
}

/** Throws a descriptive error if the kinds are empty or have duplicate ids. */
export function validateEnemyKinds(kinds: readonly EnemyKindDefinition[]): void {
  if (kinds.length === 0) throw new Error('A game needs at least one enemy kind');
  const ids = new Set<string>();
  for (const kind of kinds) {
    if (ids.has(kind.id)) throw new Error(`Duplicate enemy kind id "${kind.id}"`);
    ids.add(kind.id);
  }
}
