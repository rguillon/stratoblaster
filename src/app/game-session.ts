import type { TimeOfDay } from '../core/scenery/atmosphere';
import type { AtmosphereOptions } from '../render/scenery/atmosphere-of';
import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { BossRank } from '../core/systems/boss-fights';
import type { LevelRun } from '../core/systems/level-run';
import type { GameDefinition } from '../core/content/game-definition';
import { GameControls } from '../input/game-controls';
import { listenControls, type ListenTarget } from './listen-controls';
import type { GamepadSource } from '../input/gamepad-menu-input';
import { GAME_CONTROLS_CONFIG } from '../config/game-controls';
import type { GameView } from '../render/game-view';
import type { MenuDocument } from '../ui/screens/elements';
import type { KeyValueStorage } from '../platform/key-value-storage';
import { GamePlay, type GamePlayOptions } from './game-play';
import { LevelPrefetcher, prepareLevel } from './level-prepare';
import { startBackgroundLoader, type BackgroundLoader } from '../render/scenery/background-loader';
import { LevelLoadingScreen } from '../ui/level-loading';
import type { MenuState } from './menu-flow';
import { loadSavedSupplies, saveSupplies } from './saved-supplies';
import { loadSavedWeapons, saveWeapons } from './saved-weapons';

/**
 * Debug options from the URL (P06-R09), e.g. `?level=1-3&t=120&ship=heavy`: start a level
 * straight away, at a given time, with the playback keys and the FPS / polygons tile.
 */
export interface GameDebugOptions {
  readonly levelId: string;
  /** Seconds into the level to start at. */
  readonly time: number;
  /** The ship to fly; the game's first ship when null. */
  readonly shipId: string | null;
  /** Starts at the arrival of the level's mini or final boss instead (P07-R09). */
  readonly boss: BossRank | null;
  /** `weather=0`: no weather (P08-R12); the level's own weather otherwise. */
  readonly weather?: boolean;
  /** `look=<time of day>`: the level at that time of day (P08-R12). */
  readonly timeOfDay?: TimeOfDay | null;
}

/** The debug choices on the level's look (P08-R12): none without debug options. */
function atmosphereOf(debug: GameDebugOptions | undefined): AtmosphereOptions {
  if (!debug) return {};
  return {
    ...(debug.weather === false ? { weather: false } : {}),
    ...(debug.timeOfDay ? { timeOfDay: debug.timeOfDay } : {}),
  };
}

/** What a {@link GameSession} needs from the app's options. */
export interface GameSessionOptions {
  readonly environment: boolean;
  readonly doc: MenuDocument;
  readonly debug?: GameDebugOptions;
  readonly statsParent?: HTMLElement;
  /** Where the in-game HUD goes: the overlay, laid out at the logical resolution. */
  readonly overlay?: HTMLElement;
  /** Where keys are listened to. No keyboard when omitted. */
  readonly keyboardTarget?: ListenTarget;
  /** Connected gamepads. No gamepad when omitted. */
  readonly gamepads?: GamepadSource;
  /** Where the weapons are kept from one completed level to the next. Not kept when omitted. */
  readonly storage?: KeyValueStorage;
  /** A level starts loading (P13-R01). */
  readonly onLoadStart?: () => void;
  /**
   * Loads a level in steps, one per {@link GameSession.loadStep} (one per frame), behind a
   * loading screen (P13-R02, R03). All at once in `sync` when omitted.
   */
  readonly steppedLoading?: boolean;
  /**
   * With stepped loading, compiles the level's shaders while it loads (P13-R04). Off in e2e
   * builds: software WebGL compiles them slowly, one after the other, and the tests check the
   * game's state, not its frame times (ENG-52).
   */
  readonly precompileShaders?: boolean;
  /** Prepares the level highlighted on the level select screen in a worker (P13-R03). */
  readonly backgroundLoading?: boolean;
  /**
   * With stepped loading, also builds the level highlighted on the level select screen, one
   * step per frame, so that confirming it starts it at once (P13-R03).
   */
  readonly prebuildLevels?: boolean;
}

/** Most frames a level's loading waits for its shaders to compile in parallel (P13-R03). */
const COMPILE_FRAMES = 60;

/**
 * Seconds the level select highlight rests on a level before it is built ahead (P13-R03): longer
 * than a move across the grid, so passing over a level does not build it.
 */
const BUILD_AHEAD_AFTER = 0.6;

/** A level being loaded in steps (P13-R03). */
interface LevelLoad {
  readonly levelId: string;
  readonly shipId: string;
  /** The flow's state the level was confirmed in; none while it is built ahead. */
  state: MenuState | undefined;
  /** A step returning false is not over: it runs again on the next frame. */
  readonly steps: readonly (() => unknown)[];
  /** Frames the step being run has taken so far. */
  tries: number;
  done: number;
  play?: GamePlay;
  screen: LevelLoadingScreen | undefined;
}

/** Where a {@link GameSession} reads the high score from and records its scores (P11-R03). */
export interface SessionScores {
  /** The saved high score, for the HUD. */
  readonly highScore: () => number;
  /** A level attempt ended (completed, lost, or left) with `score`. */
  readonly record: (score: number) => void;
}

/** What the audio hears of the levels played (P12-R07, P12-R09). */
export interface SessionAudio {
  /** A level starts, or starts again from its checkpoint. */
  readonly started: (levelId: string) => void;
  /** A step of the level was run. */
  readonly step: (run: LevelRun) => void;
}

/** The cell highlighted on the level select screen, if it shows (P13-R03: prefetched). */
function highlightedLevel(state: MenuState): string | null {
  return state.screen === 'level-select' ? state.selectedId : null;
}

/** The ship the flow's levels are flown with: the one chosen, or else the one highlighted. */
function shipOf(state: MenuState): string {
  return state.chosenShipId ?? state.highlightedShipId;
}

/**
 * Starts the level chosen on the game screen, and ends it when the flow leaves it (P06-R02),
 * or starts it again from its checkpoint (P07-R08). The debug options' start time and boss
 * apply to the first level played only.
 */
export class GameSession {
  play: GamePlay | undefined;
  /** Whether the level being played is paused (P12-R01): it is kept, but not advanced. */
  paused = false;
  /** The player's in-game controls, fed by the keyboard target and the gamepads. */
  readonly controls: GameControls;
  #startTime: number;
  #startBoss: BossRank | null;
  /** The menu flow's attempt the level being played was started for. */
  #attempt = -1;
  #load: LevelLoad | undefined;
  /** The level highlighted on the level select screen, built ahead (P13-R03). */
  #ahead: LevelLoad | undefined;
  readonly #stopListening: () => void;
  readonly #loader: BackgroundLoader | undefined;
  readonly #prefetcher: LevelPrefetcher;
  /** The level highlighted on the level select screen, if it shows. */
  #highlighted: string | null = null;
  /** The ship the level highlighted on the level select screen would be flown with. */
  #aheadShip: string | null = null;

  constructor(
    private readonly engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    private readonly options: GameSessionOptions,
    private readonly onComplete: (play: GamePlay) => void,
    private readonly scores?: SessionScores,
    private readonly audio?: SessionAudio,
  ) {
    this.#startTime = options.debug?.time ?? 0;
    this.#startBoss = options.debug?.boss ?? null;
    this.controls = new GameControls(GAME_CONTROLS_CONFIG, options.gamepads);
    this.#loader = options.backgroundLoading ? startBackgroundLoader() : undefined;
    this.#prefetcher = new LevelPrefetcher(game, this.#loader);
    // No debug keys while paused (P12-R01: nothing in the level changes).
    this.#stopListening = listenControls(options.keyboardTarget, this.controls, () =>
      this.paused ? undefined : this.play,
    );
  }

  /** Ends the level being played and stops listening to the keys. */
  dispose(): void {
    this.end();
    this.#dropAhead();
    this.#stopListening();
    this.#loader?.stop();
  }

  sync(state: MenuState): void {
    this.#highlighted = highlightedLevel(state);
    this.#aheadShip = shipOf(state);
    const levelId = state.screen === 'game' || state.paused ? state.chosenLevelId : null;
    // Presses made while paused (e.g. a bomb key) do not carry into the level (P12-R01).
    if (state.paused !== this.paused) this.controls.clear();
    this.paused = state.paused;
    if (levelId === null) {
      this.end();
      return;
    }
    // Continue from a checkpoint (P07-R08): the level starts again.
    if (this.play && state.attempt !== this.#attempt) this.end();
    if (this.play || this.#load || state.levelResult) return;
    this.#start(state, levelId);
  }

  /** Whether a level is being loaded (P13-R03). */
  get loading(): boolean {
    return this.#load !== undefined;
  }

  /**
   * Runs the next step of the level being loaded, if any (P13-R03), one per frame of `dt`
   * seconds, and prefetches the level highlighted on the level select screen once it rests there.
   */
  loadStep(dt = 0): void {
    this.#prefetcher.update(dt, this.#highlighted);
    const load = this.#load;
    if (!load) {
      this.#buildAhead();
      return;
    }
    if (this.#runStep(load)) this.#load = undefined;
  }

  /** Runs the next step of `load`; true once its last step has run. */
  #runStep(load: LevelLoad): boolean {
    load.tries++;
    if (load.steps[load.done]?.() === false) return false;
    load.done++;
    load.tries = 0;
    load.screen?.show(load.done / load.steps.length);
    if (load.done < load.steps.length) return false;
    load.screen?.dispose();
    return true;
  }

  /**
   * Builds the level the level select highlight rests on, one step per frame (P13-R03), short of
   * starting it; drops the one built for another level or ship.
   */
  #buildAhead(): void {
    if (!this.options.prebuildLevels || !this.options.steppedLoading) return;
    // Off the level select screen, the level built ahead is dropped.
    if (this.#highlighted === null) this.#dropAhead();
    const levelId = this.#prefetcher.restedOn(BUILD_AHEAD_AFTER);
    const shipId = this.#aheadShip;
    if (levelId === null || shipId === null) return;
    if (!this.#isAhead(levelId, shipId)) this.#dropAhead();
    const ahead = (this.#ahead ??= this.#newLoad(levelId, shipId, undefined));
    // Its last step (starting it) waits for the confirmation.
    if (ahead.done < ahead.steps.length - 1) this.#runStep(ahead);
  }

  /** Whether the level built ahead (if any) is `levelId` flown by `shipId`. */
  #isAhead(levelId: string, shipId: string): boolean {
    return this.#ahead?.levelId === levelId && this.#ahead.shipId === shipId;
  }

  #dropAhead(): void {
    this.#ahead?.play?.dispose();
    this.#ahead = undefined;
  }

  /**
   * Starts `levelId` for the flow's attempt (from its checkpoint when it has one): at once, or in
   * steps (P13-R03): the level's ground, its scene, a first drawing that compiles its shaders.
   */
  #start(state: MenuState, levelId: string): void {
    this.options.onLoadStart?.();
    this.#prefetcher.start(levelId);
    const load = this.#takeAhead(state, levelId) ?? this.#newLoad(levelId, shipOf(state), state);
    load.state = state;
    this.#load = load;
    if (!this.options.steppedLoading) {
      while (this.#load === load) this.loadStep();
      return;
    }
    const { doc, overlay } = this.options;
    // Already built: it starts in this very frame; otherwise behind the loading screen.
    if (load.done >= load.steps.length - 1) this.loadStep();
    else if (overlay) {
      load.screen = new LevelLoadingScreen(doc, overlay, this.game.texts.loading);
      load.screen.show(load.done / load.steps.length);
    }
  }

  /** The level built ahead on the level select screen, if it is the one confirmed (P13-R03). */
  #takeAhead(state: MenuState, levelId: string): LevelLoad | undefined {
    const usable = this.#isAhead(levelId, shipOf(state)) && !state.resume;
    if (!usable) this.#dropAhead();
    const ahead = this.#ahead;
    this.#ahead = undefined;
    return ahead;
  }

  /**
   * The steps loading `levelId` flown by `shipId` (P13-R03): the level's ground, its scene, a
   * first drawing that compiles its shaders, then its start (for the flow's state when it is
   * confirmed).
   */
  #newLoad(levelId: string, shipId: string, state: MenuState | undefined): LevelLoad {
    const load: LevelLoad = {
      levelId,
      shipId,
      state,
      steps: [
        // The ground, generated in the background (often already, while the level was chosen).
        () => prepareLevel(this.game, levelId),
        () => {
          load.play = this.#newPlay(load.state, levelId, shipId);
        },
        () => {
          if (this.options.steppedLoading)
            load.play?.prepare(this.options.precompileShaders ?? true);
        },
        // Hidden by the loading screen (or the menus), the shaders compile (in parallel where
        // WebGL can, over a few frames), then a first drawing finishes them.
        () => {
          const scene = load.play?.view.scene;
          if (!this.options.steppedLoading || !scene) return true;
          if (this.options.precompileShaders === false) return true;
          const parallel = scene.getEngine().getCaps().parallelShaderCompile !== undefined;
          if (!scene.isReady(true) && parallel && load.tries < COMPILE_FRAMES) return false;
          scene.render();
          return true;
        },
        () => {
          if (load.play && load.state) this.#started(load.play, load.state, levelId);
        },
      ],
      done: 0,
      tries: 0,
      screen: undefined,
    };
    return load;
  }

  /**
   * What the player kept from the levels completed before: the weapons (D-071), the lives and
   * bombs (reviewer, 2026-10-28). A Continue, after a game over, starts again with the starting
   * lives and bombs.
   */
  #kept(state: MenuState | undefined): Pick<GamePlayOptions, 'weapons' | 'supplies'> {
    const { storage } = this.options;
    if (!storage) return {};
    const weapons = loadSavedWeapons(storage, this.game.id);
    const supplies = state?.resume ? null : loadSavedSupplies(storage, this.game.id);
    return { ...(weapons ? { weapons } : {}), ...(supplies ? { supplies } : {}) };
  }

  #newPlay(state: MenuState | undefined, levelId: string, shipId: string): GamePlay {
    // Presses made outside the level (e.g. a bomb key on a menu) do not carry into it.
    this.controls.clear();
    const play: GamePlay = new GamePlay(
      this.engine,
      this.game,
      { shipId, levelId },
      this.controls,
      {
        environment: this.options.environment,
        debug: this.options.debug !== undefined,
        startTime: this.#startTime,
        startBoss: this.#startBoss,
        atmosphere: atmosphereOf(this.options.debug),
        ...this.#kept(state),
        highScore: this.scores?.highScore() ?? 0,
        ...(state?.resume ? { resume: state.resume } : {}),
        doc: this.options.doc,
        ...(this.options.statsParent ? { statsParent: this.options.statsParent } : {}),
        ...(this.options.overlay ? { hudParent: this.options.overlay } : {}),
        onComplete: () => {
          this.#completed(play);
        },
        onStep: (run) => {
          this.audio?.step(run);
        },
      },
    );
    return play;
  }

  /** The level is loaded: it is played from now on. */
  #started(play: GamePlay, state: MenuState, levelId: string): void {
    // Presses made while it loaded do not carry into it either.
    this.controls.clear();
    play.attach();
    this.audio?.started(levelId);
    this.#startTime = 0;
    this.#startBoss = null;
    this.#attempt = state.attempt;
    this.play = play;
  }

  /**
   * The level is over: a completed one keeps its weapons (D-071), lives and bombs (reviewer,
   * 2026-10-28) for the next.
   */
  #completed(play: GamePlay): void {
    const { storage } = this.options;
    if (storage && play.run.phase === 'complete') {
      saveWeapons(storage, this.game.id, play.run.arsenal.snapshot());
      const { supplies } = play.run;
      if (supplies) saveSupplies(storage, this.game.id, supplies);
    }
    this.onComplete(play);
  }

  /** Ends the level being played, or drops the one being loaded; its score counts (P11-R03). */
  end(): void {
    if (this.#load) {
      this.#load.play?.dispose();
      this.#load.screen?.dispose();
      this.#load = undefined;
    }
    if (this.play) this.scores?.record(this.play.run.score);
    this.play?.dispose();
    this.play = undefined;
    this.controls.clear();
  }
}
