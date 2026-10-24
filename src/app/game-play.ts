import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import { findGameLevel, type GameLevel } from '../core/content/game-level';
import { findPlayerShip, shipMaxSpeedPxPerSec } from '../core/entities/player-ship';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import type { EnemyBlast } from '../core/systems/enemy-world';
import { LevelRun, type LevelPhase, type LevelResult } from '../core/systems/level-run';
import type { FlightBounds } from '../core/systems/player-flight';
import type { ShotImpact } from '../core/systems/shot-world';
import { EnemyLayer } from '../render/enemy-layer';
import type { GameView } from '../render/game-view';
import { visibleHalfWidth } from '../render/scenery/playfield-framing';
import type { GameControls } from '../input/game-controls';
import { GameHud } from '../ui/game-hud';
import type { MenuDocument } from '../ui/screens/elements';
import { StatsTile } from '../ui/stats-tile';
import { GAME_CONTROLS_CONFIG } from '../config/game-controls';
import { GAME_PLAY_CONFIG as CFG } from '../config/game-play';
import { EnemyViewerShots } from './enemy-viewer-shots';
import { buildLevelScene, type LevelScene } from './level-scene';
import { RateMeter } from './rate-meter';
import { PlayfieldShip } from './shot-viewer-scene';

/** What the player chose: a ship and a level. */
export interface GameChoice {
  readonly shipId: string;
  readonly levelId: string;
}

/** Options of a {@link GamePlay}. */
export interface GamePlayOptions {
  /** Generated textures, sky lighting, shadows and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  /** Debug mode (P06-R09): playback keys and the FPS / polygons tile. */
  readonly debug: boolean;
  /** Seconds into the level to start at (P06-R09). */
  readonly startTime: number;
  readonly doc: MenuDocument;
  /** Where the debug tile goes. No tile when omitted. */
  readonly statsParent?: HTMLElement;
  /** Where the HUD goes (the overlay, at the logical resolution). No HUD when omitted. */
  readonly hudParent?: HTMLElement;
  /** Called once, when the level is complete (P06-R03). */
  readonly onComplete: (result: LevelResult) => void;
}

/** A snapshot of a running level, for the test API. */
export interface GamePlayState {
  readonly levelId: string;
  readonly phase: LevelPhase;
  /** Seconds since the start of the level, and its whole duration. */
  readonly time: number;
  readonly duration: number;
  readonly timeScale: number;
  readonly enemies: number;
  readonly destroyed: number;
  readonly spawned: number;
  readonly wavesTriggered: number;
  readonly player: { readonly x: number; readonly y: number };
  readonly firing: boolean;
  readonly shots: number;
}

function levelOf(game: GameDefinition, id: string): GameLevel {
  const level = findGameLevel(game.gameLevels, id);
  if (!level) throw new Error(`Level "${id}" cannot be played`);
  return level;
}

/**
 * The game screen (P06-R02): the chosen ship flies over the chosen level's scrolling scenery,
 * moved and fired by the {@link GameControls}, while the level's waves come in. It runs the
 * level ({@link LevelRun}) at a fixed step and draws it on the playfield layer.
 */
export class GamePlay {
  readonly view: LevelScene;
  readonly run: LevelRun;
  readonly #clock = new FixedStepClock(CFG.stepHz, CFG.maxStepsPerFrame);
  readonly #ship: PlayfieldShip;
  readonly #enemies: EnemyLayer;
  readonly #shots: EnemyViewerShots;
  readonly #speed: number;
  readonly #stats: StatsTile | undefined;
  readonly #hud: GameHud | undefined;
  /** The ship's health: always full until the player can be hit (a later phase). */
  readonly #maxHealth: number;
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  #previous = 0;
  #timeScale = 1;
  #completed = false;

  constructor(
    engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    choice: GameChoice,
    private readonly controls: GameControls,
    private readonly options: GamePlayOptions,
  ) {
    const level = levelOf(game, choice.levelId);
    this.view = buildLevelScene(engine, game, {
      level: level.scenery,
      environment: options.environment,
      glow: game.view.enemies.glow,
      environmentCubeSize: CFG.environmentCubeSize,
      stage: CFG.stage,
    });
    this.#speed = shipMaxSpeedPxPerSec(game.playerShips, choice.shipId);
    const shipDef = findPlayerShip(game.playerShips, choice.shipId);
    this.#maxHealth = shipDef.maxHealth;
    const pf = this.view.playfield;
    const scale = game.view.playerShipScale;
    const model = game.view.playerShipModels[choice.shipId];
    let nose = 0;
    // The nose is measured on the model before it joins the playfield (as on `enemies/`).
    this.#ship = pf.run(() => {
      const ship = new PlayfieldShip(this.view.scene, scale, 0, 0);
      if (model) nose = ship.show(model);
      return ship;
    });
    this.run = this.#newRun(level, Math.max(0, nose - CFG.muzzleInset));
    this.#enemies = pf.run(() => new EnemyLayer(this.view.scene, game.view.enemies.models));
    this.#shots = new EnemyViewerShots(game, pf);
    this.#stats =
      options.debug && options.statsParent
        ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
        : undefined;
    this.#hud = options.hudParent && this.#newHud(options.hudParent, shipDef.name);
    if (options.startTime > 0) this.#seek(options.startTime);
    this.frame(0);
  }

  #newRun(level: GameLevel, muzzleOffset: number): LevelRun {
    const weapon = this.game.playerWeapons[0];
    if (!weapon) throw new Error('The game has no player weapon');
    const { width } = this.game.screen;
    return new LevelRun({
      screen: this.game.screen,
      level,
      kinds: this.game.enemyKinds,
      weapon,
      weaponLevel: 1,
      ship: {
        start: { x: width / 2, y: CFG.shipStartY },
        maxSpeed: this.#speed,
        accelerationSeconds: GAME_CONTROLS_CONFIG.accelerationSeconds,
        muzzleOffset,
      },
      bounds: this.#bounds(),
      cullMargin: CFG.cullMargin,
      maxEnemyAge: CFG.maxEnemyAge,
      endWait: CFG.endWait,
      seed: CFG.seed,
      inView: this.#inView(),
    });
  }

  /** Whether a playfield point is inside what the tilted camera shows. */
  #inView(): (x: number, y: number) => boolean {
    const { width, height } = this.game.screen;
    const framing = this.view.stage.framing;
    return (x, y) =>
      y >= 0 &&
      y <= height &&
      Math.abs(x - width / 2) <= visibleHalfWidth(framing, width / height, y);
  }

  #newHud(parent: HTMLElement, ship: string): GameHud {
    const { weapon } = this.run.shots;
    const { texts } = this.game;
    return new GameHud(this.options.doc, parent, {
      ship,
      weapon: weapon.name,
      weaponLevels: weapon.levels.length,
      texts: { health: texts.hudHealth, weapon: texts.hudWeapon, destroyed: texts.hudDestroyed },
    });
  }

  /** Where the ship may fly: inside what the tilted camera shows of the playfield (P06-R02). */
  #bounds(): FlightBounds {
    const { width, height } = this.game.screen;
    const m = CFG.shipMargin;
    const framing = this.view.stage.framing;
    return {
      minY: m.bottom,
      maxY: height - m.top,
      centerX: width / 2,
      halfWidthAt: (y) => visibleHalfWidth(framing, width / height, y) - m.side,
    };
  }

  get timeScale(): number {
    return this.#timeScale;
  }

  /** Advances and draws one frame of `dt` real seconds. */
  frame(dt: number): void {
    const { steps, alpha } = this.#clock.advance(dt * this.#timeScale);
    const blasts: EnemyBlast[] = [];
    const impacts: ShotImpact[] = [];
    const step = this.#clock.stepSeconds;
    for (let i = 0; i < steps; i++) {
      this.#previous = this.run.track.distance;
      this.run.step(step, this.controls.read(step, this.#speed));
      blasts.push(...this.run.blasts);
      impacts.push(...this.run.impacts);
    }
    const track = this.run.track;
    const distance = this.#previous + (track.distance - this.#previous) * alpha;
    this.view.update(distance, dt);
    this.#draw(dt, blasts, impacts);
    if (this.run.phase === 'complete' && !this.#completed) {
      this.#completed = true;
      this.options.onComplete(this.run.result);
    }
  }

  #draw(dt: number, blasts: readonly EnemyBlast[], impacts: readonly ShotImpact[]): void {
    const { ship, enemies, shots } = this.run;
    this.#ship.pivot.position.set(ship.x, ship.y, 0);
    this.#ship.update(dt);
    this.view.playfield.run(() => {
      this.#enemies.sync(enemies.enemies, dt);
    });
    this.#shots.sync({ enemies, shots, blasts, impacts, dt });
    this.#hud?.update({
      health: this.#maxHealth,
      maxHealth: this.#maxHealth,
      weaponLevel: shots.level,
      progress: this.run.track.time / this.run.track.duration,
      destroyed: enemies.kills,
    });
    this.#fps.add(dt, ++this.#frames);
    const polygons = this.view.scene.getActiveIndices() / 3;
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons });
  }

  /**
   * A debug key (P06-R09): F toggles ×4 fast forward, ← / → jump 10 s back or on. Returns
   * whether the key was used; without debug mode no key is.
   */
  debugKey(code: string, down: boolean): boolean {
    const { fastForward, seekStep } = CFG.debug;
    const jumps: Readonly<Record<string, number>> = { ArrowLeft: -seekStep, ArrowRight: seekStep };
    if (!this.options.debug || (code !== 'KeyF' && jumps[code] === undefined)) return false;
    if (!down) return true;
    if (code === 'KeyF') this.#timeScale = this.#timeScale === 1 ? fastForward : 1;
    else this.#seek(this.run.track.time + (jumps[code] ?? 0));
    return true;
  }

  #seek(time: number): void {
    if (this.#completed) return;
    this.run.seek(time);
    this.#previous = this.run.track.distance;
  }

  get state(): GamePlayState {
    const { track, enemies, shots, ship, waves } = this.run;
    return {
      levelId: this.run.result.levelId,
      phase: this.run.phase,
      time: track.time,
      duration: track.duration,
      timeScale: this.#timeScale,
      enemies: enemies.enemies.length,
      destroyed: enemies.kills,
      spawned: enemies.spawned,
      wavesTriggered: waves.triggered,
      player: { x: ship.x, y: ship.y },
      firing: shots.firing,
      shots: shots.activeCount,
    };
  }

  dispose(): void {
    this.#enemies.dispose();
    this.#shots.dispose();
    this.#stats?.root.remove();
    this.#hud?.dispose();
    this.view.scene.dispose();
  }
}
