import type { TimeOfDay } from '../core/scenery/atmosphere';
import type { AtmosphereOptions } from '../render/scenery/atmosphere-of';
import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { BossRank } from '../core/systems/boss-fights';
import type { LevelRun } from '../core/systems/level-run';
import type { GameDefinition } from '../core/content/game-definition';
import { GameControls } from '../input/game-controls';
import type { GamepadSource } from '../input/gamepad-menu-input';
import { GAME_CONTROLS_CONFIG } from '../config/game-controls';
import type { GameView } from '../render/game-view';
import type { MenuDocument } from '../ui/screens/elements';
import type { KeyValueStorage } from '../platform/key-value-storage';
import { GamePlay } from './game-play';
import { LevelPrefetcher, prepareLevel } from './level-prepare';
import { startBackgroundLoader, type BackgroundLoader } from '../render/scenery/background-loader';
import { LevelLoadingScreen } from '../ui/level-loading';
import type { MenuState } from './menu-flow';
import { loadSavedWeapons, saveWeapons } from './saved-weapons';

type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

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
}

/** Most frames a level's loading waits for its shaders to compile in parallel (P13-R03). */
const COMPILE_FRAMES = 60;

/** A level being loaded in steps (P13-R03). */
interface LevelLoad {
  /** A step returning false is not over: it runs again on the next frame. */
  readonly steps: readonly (() => unknown)[];
  /** Frames the step being run has taken so far. */
  tries: number;
  done: number;
  play?: GamePlay;
  readonly screen: LevelLoadingScreen | undefined;
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

/** Keys go to the level's debug keys first (when on), then to the in-game controls. */
export function listenControls(
  target: ListenTarget | undefined,
  controls: GameControls,
  game: () => GamePlay | undefined,
): () => void {
  if (!target) return () => undefined;
  const onKey = (event: Event): void => {
    const { code, type } = event as KeyboardEvent;
    const down = type === 'keydown';
    if (!game()?.debugKey(code, down)) controls.key(code, down);
  };
  const onBlur = (): void => {
    controls.clear();
  };
  target.addEventListener('keydown', onKey);
  target.addEventListener('keyup', onKey);
  target.addEventListener('blur', onBlur);
  return () => {
    target.removeEventListener('keydown', onKey);
    target.removeEventListener('keyup', onKey);
    target.removeEventListener('blur', onBlur);
  };
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
  readonly #stopListening: () => void;
  readonly #loader: BackgroundLoader | undefined;
  readonly #prefetcher: LevelPrefetcher;
  /** The level highlighted on the level select screen, if it shows. */
  #highlighted: string | null = null;

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
    this.#stopListening();
    this.#loader?.stop();
  }

  sync(state: MenuState): void {
    this.#highlighted = highlightedLevel(state);
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
    if (!load) return;
    load.tries++;
    if (load.steps[load.done]?.() === false) return;
    load.done++;
    load.tries = 0;
    load.screen?.show(load.done / load.steps.length);
    if (load.done >= load.steps.length) {
      load.screen?.dispose();
      this.#load = undefined;
    }
  }

  /**
   * Starts `levelId` for the flow's attempt (from its checkpoint when it has one): at once, or in
   * steps (P13-R03): the level's ground, its scene, a first drawing that compiles its shaders.
   */
  #start(state: MenuState, levelId: string): void {
    this.options.onLoadStart?.();
    this.#prefetcher.start(levelId);
    const { doc, overlay } = this.options;
    const load: LevelLoad = {
      steps: [
        // The ground, generated in the background (often already, while the level was chosen).
        () => prepareLevel(this.game, levelId),
        () => {
          load.play = this.#newPlay(state, levelId);
        },
        () => {
          if (this.options.steppedLoading)
            load.play?.prepare(this.options.precompileShaders ?? true);
        },
        // Hidden by the loading screen, the shaders compile (in parallel where WebGL can, over
        // a few frames), then a first drawing finishes them.
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
          if (load.play) this.#started(load.play, state, levelId);
        },
      ],
      done: 0,
      tries: 0,
      screen:
        this.options.steppedLoading && overlay
          ? new LevelLoadingScreen(doc, overlay, this.game.texts.loading)
          : undefined,
    };
    this.#load = load;
    load.screen?.show(0);
    if (this.options.steppedLoading) return;
    while (this.#load === load) this.loadStep();
  }

  #newPlay(state: MenuState, levelId: string): GamePlay {
    const shipId = state.chosenShipId ?? state.highlightedShipId;
    const { storage } = this.options;
    const weapons = storage && loadSavedWeapons(storage, this.game.id);
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
        ...(weapons ? { weapons } : {}),
        highScore: this.scores?.highScore() ?? 0,
        ...(state.resume ? { resume: state.resume } : {}),
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
    this.audio?.started(levelId);
    this.#startTime = 0;
    this.#startBoss = null;
    this.#attempt = state.attempt;
    this.play = play;
  }

  /** The level is over: a completed one keeps its weapons for the next (D-071). */
  #completed(play: GamePlay): void {
    const { storage } = this.options;
    if (storage && play.run.phase === 'complete') {
      saveWeapons(storage, this.game.id, play.run.arsenal.snapshot());
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
