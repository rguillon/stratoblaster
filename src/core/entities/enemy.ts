import type { Random } from '../math/rng';
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
  fireBullet(x: number, y: number, heading: number, spec: EnemyBulletSpec): void;
  fireMissile(x: number, y: number, heading: number, spec: EnemyMissileSpec): void;
  /** Fires a laser from `owner`'s emitter ({@link Enemy.emitter}), which it follows. */
  fireLaser(owner: Enemy, spec: EnemyLaserSpec): void;
  /** Adds another enemy (e.g. parts that break off), updated from the next step. */
  spawn(enemy: Enemy): void;
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
export abstract class Enemy implements ShotTarget {
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

  /** Where its laser leaves from. Defaults to the nose, one radius ahead of the centre. */
  get emitter(): { readonly x: number; readonly y: number } {
    return {
      x: this.x + Math.sin(this.heading) * this.radius,
      y: this.y + Math.cos(this.heading) * this.radius,
    };
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
