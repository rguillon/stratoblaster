import type { LogicalScreen } from '../content/game-definition';
import type { GameLevel } from '../content/game-level';
import type { EnemyEntry, EnemyKindDefinition } from '../entities/enemy';
import type { ShotTarget } from '../entities/shot-target';
import type { WeaponDefinition } from '../entities/weapon';
import { createRng } from '../math/rng';
import { levelLength } from '../scenery/scenery-level';
import { ScrollTrack } from '../scenery/scroll-track';
import { BonusWorld, type BonusRules } from './bonus-world';
import { EnemyWorld, type EnemyBlast } from './enemy-world';
import { PlayerFlight, type FlightBounds, type FlightInput } from './player-flight';
import { findPlayerHits, type PlayerHitKind } from './player-hits';
import { PlayerHull, type HullEvent, type HullRules } from './player-hull';
import type { EnemyLaser } from './enemy-shots';
import { ShotWorld, type ShotImpact } from './shot-world';
import { validateWaveScript, WaveRunner } from './wave-runner';

/** Where a level stands (P06-R03); `over` once the player has lost every life (GD-20). */
export type LevelPhase = 'playing' | 'clearing' | 'complete' | 'over';

/** What the "Level complete" (or "Game over") overlay shows (P06-R03). */
export interface LevelResult {
  readonly levelId: string;
  readonly destroyed: number;
  readonly spawned: number;
  /** Whether the level was completed, or the game is over (phase 6 review). */
  readonly outcome: 'complete' | 'over';
}

/** A hit that landed on the player during a step, and what it did. */
export interface LandedHit {
  readonly kind: PlayerHitKind;
  readonly x: number;
  readonly y: number;
  readonly event: HullEvent;
}

/** The player's controls for one step. */
export interface LevelControls {
  readonly move: FlightInput;
  readonly fire: boolean;
  /** Switch to the next weapon of `LevelRunOptions.weapons` (phase 6 review). */
  readonly switchWeapon?: boolean;
}

/** The player ship of a run. */
export interface RunShip {
  readonly start: { readonly x: number; readonly y: number };
  readonly maxSpeed: number;
  readonly accelerationSeconds: number;
  /** Shots leave this far above the ship's centre (its nose). */
  readonly muzzleOffset: number;
  /** Its health (GD-20); 100 when omitted. */
  readonly maxHealth?: number;
}

export interface LevelRunOptions {
  readonly screen: LogicalScreen;
  readonly level: GameLevel;
  readonly kinds: readonly EnemyKindDefinition[];
  /** The weapon and its level the ship starts with. */
  readonly weapon: WeaponDefinition;
  readonly weaponLevel: number;
  /**
   * The weapons the player can switch between, in order (`LevelControls.switchWeapon`), each
   * starting at `weaponLevel` and keeping its own level. Only `weapon` when omitted.
   */
  readonly weapons?: readonly WeaponDefinition[];
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
  /**
   * Weapon bonuses (phase 6 review): some destroyed enemies drop one, and picking it up raises
   * the weapon in use by a level. None when omitted.
   */
  readonly bonuses?: BonusRules;
  /**
   * What hurts the player, and its lives (GD-20..GD-22, phase 6 review). The player cannot be
   * hurt when omitted.
   */
  readonly hull?: HullRules;
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
  readonly bonuses: BonusWorld | undefined;
  readonly hull: PlayerHull | undefined;
  /** Explosions, shot impacts and hits on the player of the last step. */
  blasts: readonly EnemyBlast[] = [];
  impacts: readonly ShotImpact[] = [];
  hits: readonly LandedHit[] = [];
  #phase: LevelPhase = 'playing';
  #clearingFor = 0;
  /** What the player's shots can hit: the enemies and missiles on screen. */
  readonly #targets: ShotTarget[] = [];
  /** The level of each weapon used so far (phase 6 review: each keeps its own). */
  readonly #levels = new Map<WeaponDefinition, number>();
  /** Where the ship can reach at the bottom of the screen. */
  readonly #reach: readonly [number, number];
  /** Laser beams that already hit the player (a beam hits once). */
  readonly #lasersHit = new WeakSet<EnemyLaser>();

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
    const { bounds } = options;
    const reach = bounds.halfWidthAt(bounds.minY);
    this.#reach = [bounds.centerX - reach, bounds.centerX + reach];
    this.bonuses =
      options.bonuses &&
      new BonusWorld(options.bonuses, createRng(options.seed + 1), this.#reach, cullMargin);
    this.hull = options.hull && new PlayerHull(options.hull, options.ship.maxHealth ?? 100);
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
      outcome: this.#phase === 'over' ? 'over' : 'complete',
    };
  }

  /** Advances the run by `dt` seconds with the player's `controls`. */
  step(dt: number, controls: LevelControls): void {
    this.blasts = [];
    this.impacts = [];
    this.hits = [];
    if (this.#phase === 'complete') return;
    // Once the game is over the ship is gone; the enemies go on until the overlay shows.
    const flying = this.#phase !== 'over';
    if (flying && controls.switchWeapon) this.#switchWeapon();
    if (flying) this.ship.step(dt, controls.move, this.options.bounds);
    this.#aimShots();
    this.shots.firing = flying && controls.fire;
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
    this.#stepHull(dt);
    this.#stepBonuses(dt);
    if (this.#phase === 'clearing') this.#clear(dt);
  }

  /**
   * Starts again at `time` seconds into the level (P06-R09): the enemies and shots on screen
   * go, the waves before that point are skipped and the later ones come as usual.
   */
  seek(time: number): void {
    if (this.#phase === 'over') return;
    this.track.seek(time);
    this.enemies.clear();
    this.bonuses?.clear();
    for (const shot of this.shots.projectiles) shot.alive = false;
    this.waves.skipTo(this.track.distance);
    this.#phase = 'playing';
    this.#clearingFor = 0;
  }

  /** The next weapon of the list, at its own level; shots in flight keep flying. */
  #switchWeapon(): void {
    const weapons = this.options.weapons ?? [this.options.weapon];
    const index = weapons.indexOf(this.shots.weapon);
    const next = weapons[(index + 1) % weapons.length] ?? this.options.weapon;
    this.#levels.set(this.shots.weapon, this.shots.level);
    this.shots.select(next, this.#levels.get(next) ?? this.options.weaponLevel);
  }

  /**
   * The most damaging enemy shot or enemy touching the ship lands, unless the ship is
   * invincible (GD-21, GD-22); with no life left the game is over (GD-20).
   */
  #stepHull(dt: number): void {
    const { hull } = this;
    const rules = this.options.hull;
    if (!hull || !rules || this.#phase === 'over') return;
    hull.step(dt);
    if (hull.invincible > 0) return;
    const [hit] = findPlayerHits(this.ship, rules, this.enemies, this.#lasersHit);
    if (!hit) return;
    hit.land();
    const event = hull.hit(hit.damage);
    this.hits = [{ kind: hit.kind, x: hit.x, y: hit.y, event }];
    if (event !== 'gameOver') return;
    this.#phase = 'over';
    this.waves.stop();
  }

  /** Drops bonuses where enemies blew up, moves them, and levels up for each one picked up. */
  #stepBonuses(dt: number): void {
    const bonuses = this.bonuses;
    if (!bonuses) return;
    bonuses.drop(this.enemies.destroyed);
    bonuses.step(dt, this.#phase === 'over' ? undefined : this.ship);
    // A level per bonus, up to the weapon's last; the new level fires at once.
    const up = bonuses.picked.length;
    if (up > 0) this.shots.select(this.shots.weapon, this.shots.level + up);
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
    // Phase 6 review: from the top, only where the ship can reach at the bottom of the screen.
    this.enemies.add(...kind.spawn({ width, height, random, entry, topRange: this.#reach }));
  }

  /** Shots leave from the ship's nose (muzzle) and centre. */
  #aimShots(): void {
    const { x, y } = this.ship;
    this.shots.muzzleX = this.shots.centerX = x;
    this.shots.centerY = y;
    this.shots.muzzleY = y + this.options.ship.muzzleOffset;
  }
}
