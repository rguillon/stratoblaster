import { createRng } from '../math/rng';
import { levelLength } from '../scenery/scenery-level';
import { ScrollTrack } from '../scenery/scroll-track';
import type { DropSource, EnemyEntry } from '../entities/enemy';
import { damageTarget, type ShotTarget } from '../entities/shot-target';
import { BonusWorld, type BonusKind } from './bonus-world';
import { BossFights, type BossFightRules } from './boss-fights';
import { EnemyWorld, type EnemyBlast } from './enemy-world';
import type { EnemyLaser } from './enemy-shots';
import type {
  LandedHit,
  LevelCheckpoint,
  LevelControls,
  LevelPhase,
  LevelResult,
  LevelRunOptions,
  Supplies,
} from './level-run-types';
import { PlayerBombs } from './player-bombs';
import { PlayerFlight } from './player-flight';
import { findPlayerHits } from './player-hits';
import { PlayerHull } from './player-hull';
import { RunArsenal } from './run-arsenal';
import { ShotWorld, type ShotImpact } from './shot-world';
import { validateWaveScript, WaveRunner } from './wave-runner';

export type {
  LandedHit,
  LevelCheckpoint,
  LevelControls,
  LevelPhase,
  LevelResult,
  LevelRunOptions,
  RunShip,
  Supplies,
} from './level-run-types';

/** Fight timings when the run is given none (only matters for levels with bosses). */
const NO_BOSS_RULES: BossFightRules = { speedEaseSeconds: 0, barFillSeconds: 1 };

/**
 * The bonuses, hull and bombs of a run, each only when its rules are given. The life and bomb
 * bonuses draw from a source of their own (P11-R07), so the weapon bonuses drop as before.
 */
function playerSystems(
  options: LevelRunOptions,
  reach: readonly [number, number],
): { bonuses?: BonusWorld; hull?: PlayerHull; bombs?: PlayerBombs } {
  const { seed, cullMargin, startSupplies: supplies } = options;
  return {
    ...(options.bonuses && {
      bonuses: new BonusWorld(
        options.bonuses,
        createRng(seed + 1),
        reach,
        cullMargin,
        createRng(seed + 2),
      ),
    }),
    ...(options.hull && {
      hull: new PlayerHull(options.hull, options.ship.maxHealth ?? 100, supplies?.lives),
    }),
    ...(options.bombs && { bombs: new PlayerBombs(options.bombs, supplies?.bombs) }),
  };
}

/**
 * One play of a level (P06-R02, R03, R07): the ground scrolls, the wave script brings the
 * enemies in by distance, the player flies and shoots them. When the scroll reaches the end no
 * more enemies come; once the last ones are gone (or after `endWait`) the level is complete.
 * With bosses (P07-R06), no wave comes while one is fought, and a level with a final boss ends
 * once that boss is destroyed instead. Pure and deterministic: everything depends on the `dt`
 * and controls given to {@link step}.
 */
export class LevelRun {
  readonly track: ScrollTrack;
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly ship: PlayerFlight;
  readonly waves: WaveRunner;
  readonly bonuses: BonusWorld | undefined;
  readonly hull: PlayerHull | undefined;
  readonly bombs: PlayerBombs | undefined;
  readonly fights: BossFights;
  readonly arsenal: RunArsenal;
  /** Explosions, shot impacts and hits on the player of the last step. */
  blasts: readonly EnemyBlast[] = [];
  impacts: readonly ShotImpact[] = [];
  hits: readonly LandedHit[] = [];
  #phase: LevelPhase = 'playing';
  #clearingFor = 0;
  /** What the player's shots can hit: the enemies and missiles on screen. */
  readonly #targets: ShotTarget[] = [];
  /** Saved when the mini boss is destroyed (P07-R08). */
  #checkpoint: LevelCheckpoint | undefined;
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
    const world = { ...area, maxEnemyAge, eye: options.eye };
    this.enemies = new EnemyWorld(world, random, level.difficulty);
    this.shots = new ShotWorld(area, options.weapon);
    this.shots.select(options.weapon, options.weaponLevel);
    this.shots.targets = this.#targets;
    const { bounds } = options;
    const reach = bounds.halfWidthAt(bounds.minY);
    this.#reach = [bounds.centerX - reach, bounds.centerX + reach];
    ({
      bonuses: this.bonuses,
      hull: this.hull,
      bombs: this.bombs,
    } = playerSystems(options, this.#reach));
    this.ship = new PlayerFlight(
      options.ship.start,
      options.ship.maxSpeed,
      options.ship.accelerationSeconds,
    );
    this.waves = new WaveRunner(level.waves, (kind, entry) => {
      this.#spawn(kind, entry, random);
    });
    this.arsenal = new RunArsenal(
      this.shots,
      options.weapons ?? [options.weapon],
      options.weaponLevel,
    );
    this.fights = new BossFights(
      level.bosses ?? [],
      options.bossKinds ?? [],
      options.bossRules ?? NO_BOSS_RULES,
      {
        area: () => ({ width: screen.width, height: screen.height, random, topRange: this.#reach }),
        add: (boss) => {
          this.enemies.add(boss);
        },
      },
    );
    if (options.startWeapons) this.arsenal.restore(options.startWeapons);
    if (options.checkpoint) this.#resume(options.checkpoint);
    this.#aimShots();
  }

  get phase(): LevelPhase {
    return this.#phase;
  }

  get result(): LevelResult {
    const over = this.#phase === 'over';
    return {
      levelId: this.options.level.id,
      destroyed: this.enemies.kills,
      spawned: this.enemies.spawned,
      outcome: over ? 'over' : 'complete',
      score: this.score,
      ...(over && this.#checkpoint ? { checkpoint: this.#checkpoint } : {}),
    };
  }

  /** Points scored so far in this attempt (P11-R01), from the checkpoint's after a Continue. */
  get score(): number {
    return this.enemies.score;
  }

  /** The lives and bombs left, kept for the next level (reviewer, 2026-10-28); none without a hull. */
  get supplies(): Supplies | undefined {
    return this.hull && { lives: this.hull.lives, bombs: this.bombs?.count ?? 0 };
  }

  /** The checkpoint saved so far (P07-R08), if any. */
  get checkpoint(): LevelCheckpoint | undefined {
    return this.#checkpoint;
  }

  /** Advances the run by `dt` seconds with the player's `controls`. */
  step(dt: number, controls: LevelControls): void {
    this.blasts = [];
    this.impacts = [];
    this.hits = [];
    if (this.#phase === 'complete') return;
    // Once the game is over the ship is gone; the enemies go on until the overlay shows.
    const flying = this.#phase !== 'over';
    if (flying && controls.switchWeapon) this.arsenal.switchWeapon();
    if (flying) this.ship.step(dt, controls.move, this.options.bounds);
    this.#aimShots();
    this.shots.firing = flying && controls.fire;
    this.track.step(dt);
    if (this.#phase === 'playing') this.#stepLevel(dt);
    this.enemies.playerX = this.ship.x;
    this.enemies.playerY = this.ship.y;
    this.enemies.step(dt);
    this.#aimAtVisible();
    this.#stepBomb(dt, flying && controls.bomb === true);
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
    this.#restartAt();
  }

  /** From the checkpoint (P07-R08): its progress, its bosses passed and its weapons. */
  #resume(checkpoint: LevelCheckpoint): void {
    this.track.seek(checkpoint.progress / this.track.speed);
    this.#restartAt(checkpoint.bossesPassed);
    this.arsenal.restore(checkpoint.weapons);
    this.enemies.score = checkpoint.score;
    this.#checkpoint = checkpoint;
  }

  /** Clears the playfield and goes on from the track's progress, as if the level began there. */
  #restartAt(bossesPassed?: number): void {
    this.enemies.clear();
    this.bonuses?.clear();
    for (const shot of this.shots.projectiles) shot.alive = false;
    this.waves.skipTo(this.track.progress);
    this.fights.skipTo(this.track, bossesPassed);
    this.#phase = 'playing';
    this.#clearingFor = 0;
  }

  /**
   * The level goes on: bosses come and go, the waves come while no boss is fought (P07-R06),
   * and the level ends with its final boss, or at the end of its scroll without one.
   */
  #stepLevel(dt: number): void {
    const { fights, track } = this;
    fights.step(dt, track);
    if (!fights.active) this.waves.step(dt, track.progress);
    const defeated = fights.justDefeated;
    if (defeated?.rank === 'mini') {
      this.#checkpoint = {
        // Where the mini boss is (the fight may start a hair before it).
        progress: Math.max(track.progress, defeated.at),
        bossesPassed: fights.passed,
        weapons: this.arsenal.snapshot(),
        score: this.score,
      };
    }
    if (fights.hasFinal ? fights.finalDefeated : track.ended) {
      this.waves.stop();
      this.#phase = 'clearing';
    }
  }

  /** A debug key (P07-R09): destroys the next intact part of the boss fought, or its core. */
  breakBossPart(): void {
    this.fights.boss?.breakNext();
  }

  /**
   * A bomb (P11-R05): when one goes off, every enemy and boss piece on screen takes its damage
   * once (a shielded core takes none); while it lasts, the enemy shots are cleared.
   */
  #stepBomb(dt: number, pressed: boolean): void {
    const { bombs } = this;
    if (!bombs) return;
    bombs.step(dt);
    if (pressed && bombs.fire(this.ship.x, this.ship.y)) {
      for (const target of this.#targets) damageTarget(target, bombs.rules.damage);
    }
    if (bombs.active) this.enemies.shots.clear();
  }

  /**
   * The most damaging enemy shot or enemy touching the ship lands, unless the ship is
   * invincible (GD-21, GD-22) or a bomb is going off (P11-R05); with no life left the game is
   * over (GD-20). A lost life tops the bombs back up (P11-R05).
   */
  #stepHull(dt: number): void {
    const { hull } = this;
    const rules = this.options.hull;
    if (!hull || !rules || this.#phase === 'over') return;
    hull.step(dt);
    if (hull.invincible > 0 || this.bombs?.active) return;
    const [hit] = findPlayerHits(this.ship, rules, this.enemies, this.#lasersHit);
    if (!hit) return;
    hit.land();
    this.#landed({ kind: hit.kind, x: hit.x, y: hit.y, event: hull.hit(hit.damage) });
  }

  /** A hit landed: a lost life tops the bombs up, the last one ends the game. */
  #landed(hit: LandedHit): void {
    this.hits = [hit];
    if (hit.event === 'lifeLost') this.bombs?.refill();
    if (hit.event !== 'gameOver') return;
    this.#phase = 'over';
    this.waves.stop();
  }

  /**
   * Drops bonuses where enemies blew up (a life bonus where a mini boss did, P11-R07), moves
   * them, and gives what each one picked up gives.
   */
  #stepBonuses(dt: number): void {
    const bonuses = this.bonuses;
    if (!bonuses) return;
    const { destroyed, brokenParts } = this.enemies;
    const { boss, rank } = this.fights;
    const enemies: readonly DropSource[] = destroyed;
    bonuses.drop([...destroyed, ...brokenParts], (t) => t !== boss && enemies.includes(t));
    if (boss && rank === 'mini' && destroyed.includes(boss)) bonuses.place('life', boss);
    bonuses.step(dt, this.#phase === 'over' ? undefined : this.ship);
    for (const bonus of bonuses.picked) this.#collect(bonus.kind);
  }

  /**
   * A weapon bonus raises the weapon in use by a level, up to its last (the new level fires at
   * once); a life or a bomb bonus adds one, or scores its points at the most (P11-R07).
   */
  #collect(kind: BonusKind): void {
    if (kind === 'weapon') {
      this.arsenal.levelUp(1);
      return;
    }
    const added = kind === 'life' ? this.hull?.addLife() : this.bombs?.add();
    if (added !== true) this.enemies.score += this.options.bonuses?.overflowPoints?.[kind] ?? 0;
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
