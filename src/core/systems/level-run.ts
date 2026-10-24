import type { LogicalScreen } from '../content/game-definition';
import type { GameLevel } from '../content/game-level';
import type { EnemyEntry, EnemyKindDefinition } from '../entities/enemy';
import type { ShotTarget } from '../entities/shot-target';
import type { WeaponDefinition } from '../entities/weapon';
import { createRng } from '../math/rng';
import { levelLength } from '../scenery/scenery-level';
import { ScrollTrack } from '../scenery/scroll-track';
import { EnemyWorld, type EnemyBlast } from './enemy-world';
import { PlayerFlight, type FlightBounds, type FlightInput } from './player-flight';
import { ShotWorld, type ShotImpact } from './shot-world';
import { validateWaveScript, WaveRunner } from './wave-runner';

/** Where a level stands (P06-R03). */
export type LevelPhase = 'playing' | 'clearing' | 'complete';

/** What the "Level complete" overlay shows (P06-R03). */
export interface LevelResult {
  readonly levelId: string;
  readonly destroyed: number;
  readonly spawned: number;
}

/** The player's controls for one step. */
export interface LevelControls {
  readonly move: FlightInput;
  readonly fire: boolean;
}

/** The player ship of a run. */
export interface RunShip {
  readonly start: { readonly x: number; readonly y: number };
  readonly maxSpeed: number;
  readonly accelerationSeconds: number;
  /** Shots leave this far above the ship's centre (its nose). */
  readonly muzzleOffset: number;
}

export interface LevelRunOptions {
  readonly screen: LogicalScreen;
  readonly level: GameLevel;
  readonly kinds: readonly EnemyKindDefinition[];
  /** The weapon and its level the ship starts with. */
  readonly weapon: WeaponDefinition;
  readonly weaponLevel: number;
  readonly ship: RunShip;
  readonly bounds: FlightBounds;
  /** Enemies and shots this far outside the playfield are removed. */
  readonly cullMargin: number;
  readonly maxEnemyAge: number;
  /** Longest wait for the last enemies once the scroll has ended (P06-R03). */
  readonly endWait: number;
  readonly seed: number;
  /**
   * Whether a point of the playfield is on screen. Only enemies (and missiles) whose centre is
   * on screen can be hit, so nothing blows up where the player cannot see it. Defaults to the
   * playfield's rectangle.
   */
  readonly inView?: (x: number, y: number) => boolean;
}

/**
 * One play of a level (P06-R02, R03, R07): the ground scrolls, the wave script brings the
 * enemies in by distance, the player flies and shoots them. When the scroll reaches the end no
 * more enemies come; once the last ones are gone (or after `endWait`) the level is complete.
 * Pure and deterministic: everything depends on the `dt` and controls given to {@link step}.
 */
export class LevelRun {
  readonly track: ScrollTrack;
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly ship: PlayerFlight;
  readonly waves: WaveRunner;
  /** Explosions and shot impacts of the last step. */
  blasts: readonly EnemyBlast[] = [];
  impacts: readonly ShotImpact[] = [];
  #phase: LevelPhase = 'playing';
  #clearingFor = 0;
  /** What the player's shots can hit: the enemies and missiles on screen. */
  readonly #targets: ShotTarget[] = [];

  constructor(private readonly options: LevelRunOptions) {
    const { screen, level, kinds, cullMargin, maxEnemyAge } = options;
    validateWaveScript(
      level.waves,
      kinds.map((k) => k.id),
    );
    this.track = new ScrollTrack(level.scenery.scrollSpeed, levelLength(level.scenery));
    const random = createRng(options.seed);
    const area = { width: screen.width, height: screen.height, cullMargin };
    this.enemies = new EnemyWorld({ ...area, maxEnemyAge }, random, level.difficulty);
    this.shots = new ShotWorld(area, options.weapon);
    this.shots.select(options.weapon, options.weaponLevel);
    this.shots.targets = this.#targets;
    this.ship = new PlayerFlight(
      options.ship.start,
      options.ship.maxSpeed,
      options.ship.accelerationSeconds,
    );
    this.waves = new WaveRunner(level.waves, (kind, entry) => {
      this.#spawn(kind, entry, random);
    });
    this.#aimShots();
  }

  get phase(): LevelPhase {
    return this.#phase;
  }

  get result(): LevelResult {
    return {
      levelId: this.options.level.id,
      destroyed: this.enemies.kills,
      spawned: this.enemies.spawned,
    };
  }

  /** Advances the run by `dt` seconds with the player's `controls`. */
  step(dt: number, controls: LevelControls): void {
    this.blasts = [];
    this.impacts = [];
    if (this.#phase === 'complete') return;
    this.ship.step(dt, controls.move, this.options.bounds);
    this.#aimShots();
    this.shots.firing = controls.fire;
    this.track.step(dt);
    if (this.#phase === 'playing') {
      this.waves.step(dt, this.track.distance);
      if (this.track.ended) {
        this.waves.stop();
        this.#phase = 'clearing';
      }
    }
    this.enemies.playerX = this.ship.x;
    this.enemies.playerY = this.ship.y;
    this.enemies.step(dt);
    this.#aimAtVisible();
    this.shots.step(dt);
    this.blasts = this.enemies.blasts;
    this.impacts = this.shots.impacts;
    if (this.#phase === 'clearing') this.#clear(dt);
  }

  /**
   * Starts again at `time` seconds into the level (P06-R09): the enemies and shots on screen
   * go, the waves before that point are skipped and the later ones come as usual.
   */
  seek(time: number): void {
    this.track.seek(time);
    this.enemies.clear();
    for (const shot of this.shots.projectiles) shot.alive = false;
    this.waves.skipTo(this.track.distance);
    this.#phase = 'playing';
    this.#clearingFor = 0;
  }

  /** Only what is on screen can be hit (see `LevelRunOptions.inView`). */
  #aimAtVisible(): void {
    const { width, height } = this.options.screen;
    const inView =
      this.options.inView ??
      ((x: number, y: number) => x >= 0 && x <= width && y >= 0 && y <= height);
    this.#targets.length = 0;
    for (const target of this.enemies.targets) {
      if (inView(target.x, target.y)) this.#targets.push(target);
    }
  }

  /** Completes the level once the last enemies are gone, or after the longest wait. */
  #clear(dt: number): void {
    this.#clearingFor += dt;
    const empty = this.enemies.enemies.length === 0;
    if (empty || this.#clearingFor >= this.options.endWait) this.#phase = 'complete';
  }

  #spawn(kindId: string, entry: EnemyEntry, random: () => number): void {
    const kind = this.options.kinds.find((k) => k.id === kindId);
    if (!kind) return;
    const { width, height } = this.options.screen;
    this.enemies.add(...kind.spawn({ width, height, random, entry }));
  }

  /** Shots leave from the ship's nose (muzzle) and centre. */
  #aimShots(): void {
    const { x, y } = this.ship;
    this.shots.muzzleX = this.shots.centerX = x;
    this.shots.centerY = y;
    this.shots.muzzleY = y + this.options.ship.muzzleOffset;
  }
}
