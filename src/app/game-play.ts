import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import { findGameLevel, type GameLevel } from '../core/content/game-level';
import { findPlayerShip, shipMaxSpeedPxPerSec } from '../core/entities/player-ship';
import { withRunout } from '../core/scenery/scenery-level';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import type { Bonus } from '../core/systems/bonus-world';
import type { BossRank } from '../core/systems/boss-fights';
import type { EnemyBlast } from '../core/systems/enemy-world';
import {
  LevelRun,
  type LandedHit,
  type LevelCheckpoint,
  type LevelResult,
} from '../core/systems/level-run';
import type { FlightBounds } from '../core/systems/player-flight';
import type { WeaponLevels } from '../core/systems/run-arsenal';
import type { ShotImpact } from '../core/systems/shot-world';
import { EnemyLayer } from '../render/enemy-layer';
import type { BonusRenderer, GameView } from '../render/game-view';
import type { AtmosphereOptions } from '../render/scenery/atmosphere-of';
import { playfieldEye, visibleHalfWidth } from '../render/scenery/playfield-framing';
import type { GameControls } from '../input/game-controls';
import { GameHud } from '../ui/game-hud';
import type { MenuDocument } from '../ui/screens/elements';
import { StatsTile } from '../ui/stats-tile';
import { GAME_CONTROLS_CONFIG } from '../config/game-controls';
import { GAME_PLAY_CONFIG as CFG } from '../config/game-play';
import { EnemyViewerShots } from './enemy-viewer-shots';
import { hudFrame } from './game-play-hud';
import { levelState, type GamePlayState } from './game-play-state';
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
  /** Starts at the arrival of this boss of the level instead (P07-R09). */
  readonly startBoss?: BossRank | null;
  /** Starts again from this checkpoint (P07-R08). */
  readonly resume?: LevelCheckpoint;
  /** The weapons kept from the levels completed before; all at level 1 when omitted. */
  readonly weapons?: WeaponLevels;
  /** Debug choices on the level's look (P08-R12): a forced time of day, no weather. */
  readonly atmosphere?: AtmosphereOptions;
  readonly doc: MenuDocument;
  /** Where the debug tile goes. No tile when omitted. */
  readonly statsParent?: HTMLElement;
  /** Where the HUD goes (the overlay, at the logical resolution). No HUD when omitted. */
  readonly hudParent?: HTMLElement;
  /** Called once, when the level is complete (P06-R03) or the game is over (GD-20). */
  readonly onComplete: (result: LevelResult) => void;
}

/** What happened during the steps of one frame, to draw. */
interface FrameEvents {
  readonly blasts: EnemyBlast[];
  readonly impacts: ShotImpact[];
  readonly picked: Bonus[];
}

/** A spark where a hit landed; a blast at the ship when it cost a life (phase 6 review). */
function hitBlasts(
  hits: readonly LandedHit[],
  ship: { readonly x: number; readonly y: number },
): EnemyBlast[] {
  const { hitSpark, shipBlast } = CFG.damage;
  return hits.map((hit) =>
    hit.event === 'hit'
      ? { kind: 'missile', x: hit.x, y: hit.y, radius: hitSpark }
      : { kind: 'enemy', x: ship.x, y: ship.y, radius: shipBlast },
  );
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
  readonly #bonuses: BonusRenderer;
  readonly #speed: number;
  readonly #stats: StatsTile | undefined;
  readonly #hud: GameHud | undefined;
  readonly #maxHealth: number;
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  #previous = 0;
  #timeScale = 1;
  /** How far the ship is banked, in radians (visual only). */
  #roll = 0;
  #completed = false;
  /** Seconds since the last life was lost (the "Game over" overlay waits a little). */
  #overFor = 0;

  constructor(
    engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    choice: GameChoice,
    private readonly controls: GameControls,
    private readonly options: GamePlayOptions,
  ) {
    const level = levelOf(game, choice.levelId);
    this.view = buildLevelScene(engine, game, {
      // Extra ground past the end, for the final boss fight (P07-R03).
      level: withRunout(level.scenery, level.runout ?? 0),
      environment: options.environment,
      glow: game.view.enemies.glow,
      environmentCubeSize: CFG.environmentCubeSize,
      stage: CFG.stage,
      ...(options.atmosphere ? { atmosphere: options.atmosphere } : {}),
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
    this.#bonuses = pf.run(() => game.view.bonuses(this.view.scene));
    this.#stats =
      options.debug && options.statsParent
        ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
        : undefined;
    this.#hud = options.hudParent && this.#newHud(options.hudParent, shipDef.name);
    if (options.startTime > 0) this.#seek(options.startTime);
    const boss = this.run.fights.bosses.find((b) => b.rank === options.startBoss);
    if (boss) this.#seek(boss.at / this.run.track.speed);
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
      weapons: this.game.playerWeapons,
      ship: {
        start: { x: width / 2, y: CFG.shipStartY },
        maxSpeed: this.#speed,
        accelerationSeconds: GAME_CONTROLS_CONFIG.accelerationSeconds,
        muzzleOffset,
        maxHealth: this.#maxHealth,
      },
      bounds: this.#bounds(),
      cullMargin: CFG.cullMargin,
      eye: playfieldEye(this.game.screen, this.view.stage.framing),
      maxEnemyAge: CFG.maxEnemyAge,
      endWait: CFG.endWait,
      seed: CFG.seed,
      inView: this.#inView(),
      bonuses: this.game.bonuses,
      hull: this.game.hull,
      bossKinds: this.game.bossKinds,
      bossRules: this.game.bossFights,
      ...(this.options.weapons ? { startWeapons: this.options.weapons } : {}),
      ...(this.options.resume ? { checkpoint: this.options.resume } : {}),
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
    const { texts } = this.game;
    return new GameHud(this.options.doc, parent, {
      ship,
      texts: {
        health: texts.hudHealth,
        weapon: texts.hudWeapon,
        destroyed: texts.hudDestroyed,
        lives: texts.hudLives,
      },
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

  /**
   * Runs `seconds` of real time at once, one simulation step a frame, without rendering: the
   * e2e tests' clock (ENG-52), so they do not wait on frames that software WebGL draws slowly.
   */
  advance(seconds: number): void {
    const step = this.#clock.stepSeconds;
    for (let t = 0; t < seconds; t += step) this.frame(step);
  }

  /** Advances and draws one frame of `dt` real seconds. */
  frame(dt: number): void {
    const { steps, alpha } = this.#clock.advance(dt * this.#timeScale);
    const events: FrameEvents = { blasts: [], impacts: [], picked: [] };
    const step = this.#clock.stepSeconds;
    for (let i = 0; i < steps; i++) {
      this.#previous = this.run.track.distance;
      this.run.step(step, this.controls.read(step, this.#speed));
      events.blasts.push(...this.run.blasts);
      events.impacts.push(...this.run.impacts);
      events.picked.push(...(this.run.bonuses?.picked ?? []));
      events.blasts.push(...hitBlasts(this.run.hits, this.run.ship));
    }
    const track = this.run.track;
    const distance = this.#previous + (track.distance - this.#previous) * alpha;
    this.view.update(distance, dt);
    this.#draw(dt, events);
    if (this.run.phase === 'over') this.#overFor += dt * this.#timeScale;
    const over = this.#overFor >= CFG.damage.gameOverDelay;
    if ((this.run.phase === 'complete' || over) && !this.#completed) {
      this.#completed = true;
      this.options.onComplete(this.run.result);
    }
  }

  #draw(dt: number, { blasts, impacts, picked }: FrameEvents): void {
    const { ship, enemies, shots } = this.run;
    this.#ship.pivot.position.set(ship.x, ship.y, 0);
    this.#ship.pivot.setEnabled(this.#shipShown());
    this.#ship.pivot.rotation.y = this.#bank(ship.vx, dt);
    this.#ship.update(dt);
    this.view.playfield.run(() => {
      this.#enemies.sync(enemies.enemies, dt);
      const bonuses = this.run.bonuses?.bonuses ?? [];
      this.#bonuses.sync({ bonuses, picked, dtSeconds: dt });
    });
    this.#shots.sync({ enemies, shots, blasts, impacts, dt });
    this.#hud?.update(hudFrame(this.run, this.#maxHealth, this.game.texts));
    this.#fps.add(dt, ++this.#frames);
    const polygons = this.view.scene.getActiveIndices() / 3;
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons });
  }

  /** Whether the ship shows: not once the game is over, blinking while invincible (GD-22). */
  #shipShown(): boolean {
    const hull = this.run.hull;
    if (this.run.phase === 'over') return false;
    if (!hull || hull.invincible <= 0) return true;
    return Math.floor(hull.invincible * CFG.damage.blinkHz * 2) % 2 === 0;
  }

  /**
   * The ship's bank for a sideways speed `vx` (phase 6 review): the wing on the side it flies
   * to dips, more the faster it goes, easing in and out. Around the nose (the playfield's Y),
   * negative turns +X away from the camera.
   */
  #bank(vx: number, dt: number): number {
    const { maxDeg, easePerSec } = CFG.roll;
    const target = -(vx / this.#speed) * ((maxDeg * Math.PI) / 180);
    this.#roll += (target - this.#roll) * Math.min(1, easePerSec * dt);
    return this.#roll;
  }

  /** The ship's bank, in radians: negative when flying right. */
  get roll(): number {
    return this.#roll;
  }

  /**
   * A debug key (P06-R09): F toggles ×4 fast forward, ← / → jump 10 s back or on, K destroys
   * the next part of the boss fought (P07-R09). Returns whether the key was used; without debug
   * mode no key is.
   */
  debugKey(code: string, down: boolean): boolean {
    const { fastForward, seekStep } = CFG.debug;
    const jumps: Readonly<Record<string, number>> = { ArrowLeft: -seekStep, ArrowRight: seekStep };
    const known = code === 'KeyF' || code === 'KeyK' || jumps[code] !== undefined;
    if (!this.options.debug || !known) return false;
    if (!down) return true;
    if (code === 'KeyF') this.#timeScale = this.#timeScale === 1 ? fastForward : 1;
    else if (code === 'KeyK') this.run.breakBossPart();
    else this.#seek(this.run.track.time + (jumps[code] ?? 0));
    return true;
  }

  #seek(time: number): void {
    if (this.#completed) return;
    this.run.seek(time);
    this.#previous = this.run.track.distance;
  }

  get state(): GamePlayState {
    const { stage } = this.view;
    const { aurora, groundLights, sun, fog } = stage.atmosphere;
    const sky = {
      weatherParticles: stage.weatherParticles,
      aurora,
      groundLights,
      sunIntensity: sun.intensity,
      fogEnd: fog.end,
    };
    return { ...levelState(this.run, this.#timeScale, this.#maxHealth), sky };
  }

  dispose(): void {
    this.#enemies.dispose();
    this.#shots.dispose();
    this.#bonuses.dispose();
    this.#stats?.root.remove();
    this.#hud?.dispose();
    this.view.scene.dispose();
  }
}
