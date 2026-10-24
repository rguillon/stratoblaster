import type { Enemy, EnemyContext } from '../entities/enemy';
import { isAlive, type ShotTarget } from '../entities/shot-target';
import type { Random } from '../math/rng';
import { EnemyShots } from './enemy-shots';

/** Something that blew up during the last step, for the explosions (GD-62). */
export interface EnemyBlast {
  readonly kind: 'enemy' | 'missile';
  readonly x: number;
  readonly y: number;
  /** Size of what blew up (its hit radius). */
  readonly radius: number;
}

export interface EnemyWorldOptions {
  readonly width: number;
  readonly height: number;
  /**
   * Enemies are removed once they have been on the playfield and are this far outside it, and
   * shots once they are this far outside.
   */
  readonly cullMargin: number;
  /** Enemies older than this are removed, whatever they do (a safety net). */
  readonly maxEnemyAge: number;
}

/**
 * How hard the enemies are, as factors on each kind's own values (1 = as tuned): their bullets'
 * speed and how fast their attacks come (P06-R08).
 */
export interface EnemyDifficulty {
  readonly bulletSpeed: number;
  readonly fireRate: number;
}

/**
 * The enemies and their shots (P05): updates every enemy, removes the destroyed ones (scoring
 * them, GD-50, and letting them spawn parts) and the ones that left, and moves their shots.
 * Its {@link targets} are what the player's shots can hit. Pure and deterministic.
 */
export class EnemyWorld {
  readonly enemies: Enemy[] = [];
  readonly shots: EnemyShots;
  /** Living enemies and missiles, rebuilt every step (the player's shots aim at these). */
  readonly targets: ShotTarget[] = [];
  /** Blasts of the last step. */
  blasts: EnemyBlast[] = [];
  /** Enemies destroyed and points scored since the world was created. */
  kills = 0;
  score = 0;
  /** Enemies added (their parts and launches included) and their total health, since then. */
  spawned = 0;
  spawnedHealth = 0;
  playerX = 0;
  playerY = 0;
  #nextId = 1;
  readonly #entered = new WeakSet<Enemy>();
  readonly #spawned: Enemy[] = [];
  readonly #context: { -readonly [K in keyof EnemyContext]: EnemyContext[K] };

  constructor(
    readonly options: EnemyWorldOptions,
    random: Random,
    difficulty: EnemyDifficulty = { bulletSpeed: 1, fireRate: 1 },
  ) {
    this.shots = new EnemyShots(options);
    const shots = this.shots;
    const { bulletSpeed } = difficulty;
    this.#context = {
      width: options.width,
      height: options.height,
      random,
      fireRate: difficulty.fireRate,
      playerX: 0,
      playerY: 0,
      fireBullet: (x, y, heading, spec) => {
        shots.fireBullet(x, y, heading, { ...spec, speed: spec.speed * bulletSpeed });
      },
      fireMissile: (x, y, heading, spec) => {
        shots.fireMissile(x, y, heading, spec);
      },
      fireLaser: (owner, spec) => {
        shots.fireLaser(owner, spec);
      },
      spawn: (enemy) => {
        this.#spawned.push(enemy);
      },
    };
  }

  /** Adds enemies, updated from the next step. */
  add(...enemies: Enemy[]): void {
    for (const enemy of enemies) {
      enemy.id = this.#nextId++;
      this.enemies.push(enemy);
      this.spawned++;
      this.spawnedHealth += enemy.maxHealth;
    }
    this.#rebuildTargets();
  }

  /** Number of enemies whose centre is over the playfield. */
  get onScreen(): number {
    return this.enemies.filter((enemy) => this.#within(enemy, 0)).length;
  }

  /** Removes every enemy and shot. */
  clear(): void {
    this.enemies.length = 0;
    this.shots.clear();
    this.blasts = [];
    this.#rebuildTargets();
  }

  /** Advances everything by `dt` seconds. */
  step(dt: number): void {
    this.blasts = [];
    this.#context.playerX = this.playerX;
    this.#context.playerY = this.playerY;
    this.#collectDestroyed();
    for (const enemy of this.enemies) {
      enemy.age += dt;
      enemy.update(this.#context, dt);
      this.#checkGone(enemy);
    }
    this.#collectDestroyed();
    for (const missile of this.shots.missiles) {
      if (missile.alive && missile.health <= 0) {
        this.blasts.push({ kind: 'missile', x: missile.x, y: missile.y, radius: missile.radius });
      }
    }
    this.shots.step(dt, this.playerX, this.playerY);
    this.#removeGone();
    this.add(...this.#spawned.splice(0));
  }

  /** Scores the enemies the player's shots destroyed and lets them spawn their parts. */
  #collectDestroyed(): void {
    for (const enemy of this.enemies) {
      if (enemy.gone || isAlive(enemy)) continue;
      enemy.gone = true;
      this.kills++;
      this.score += enemy.points;
      this.blasts.push({ kind: 'enemy', x: enemy.x, y: enemy.y, radius: enemy.radius });
      enemy.onDestroyed?.(this.#context);
    }
  }

  /** Whether the enemy's centre is within `margin` of the playfield. */
  #within(enemy: Enemy, margin: number): boolean {
    const { width, height } = this.options;
    const { x, y } = enemy;
    return x >= -margin && x <= width + margin && y >= -margin && y <= height + margin;
  }

  /** Marks an enemy gone once it has been on the playfield and then left it, or is too old. */
  #checkGone(enemy: Enemy): void {
    if (this.#within(enemy, enemy.radius)) this.#entered.add(enemy);
    const left = !this.#within(enemy, this.options.cullMargin) && this.#entered.has(enemy);
    if (left || enemy.age > this.options.maxEnemyAge) enemy.gone = true;
  }

  #removeGone(): void {
    for (let i = this.enemies.length - 1; i >= 0; i--) {
      if (this.enemies[i]?.gone) this.enemies.splice(i, 1);
    }
  }

  #rebuildTargets(): void {
    this.targets.length = 0;
    for (const enemy of this.enemies) if (!enemy.gone) this.targets.push(enemy);
    for (const missile of this.shots.missiles) if (missile.alive) this.targets.push(missile);
  }
}
