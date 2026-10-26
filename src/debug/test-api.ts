import type { MenuScreen } from '../core/menu/menu-screen';
import type { LevelResult } from '../core/systems/level-run';

import { isMenuAction, type MenuAction } from '../input/menu-action';

/** The level being played (P06), as the game screen reports it. */
export interface GameTestLevelState {
  readonly levelId: string;
  readonly phase: 'playing' | 'clearing' | 'complete' | 'over';
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
  /** Level of the weapon in use, and weapon bonuses falling / dropped (phase 6 review). */
  readonly weaponLevel: number;
  readonly bonuses: number;
  readonly bonusesDropped: number;
  /** The kind of each bonus falling (P11-R07): `weapon`, `life` or `bomb`. */
  readonly bonusKinds: readonly string[];
  /** Points scored in this attempt, and bombs left (P11-R01, R05). */
  readonly score: number;
  readonly bombs: number;
  /** Enemy bullets and missiles in flight and lasers shown (a bomb clears them, P11-R05). */
  readonly enemyShots: number;
  /** The ship's health, lives left and seconds of invincibility left (GD-20, GD-22). */
  readonly health: number;
  readonly lives: number;
  readonly invincible: number;
  /** The boss being fought, if any; bosses destroyed; the ground's speed factor (P07). */
  readonly boss: {
    readonly name: string;
    readonly rank: 'mini' | 'final';
    readonly state: 'entering' | 'fighting' | 'dying';
    readonly stage: number;
    readonly partsLeft: number;
    readonly parts: number;
    readonly health: number;
    readonly fullHealth: number;
  } | null;
  readonly bossesDefeated: number;
  readonly groundSpeed: number;
  /** Whether the mini boss's checkpoint is saved (P07-R08). */
  readonly checkpoint: boolean;
  /** How the level looks where the view is (P08-R04, R05). */
  readonly sky?: {
    /** Kind of the weather falling (`none` when there is none; P08-R05, P09-R05). */
    readonly weather: string;
    /** Kind of the second weather (phase 10), `none` when there is none. */
    readonly secondWeather: string;
    readonly weatherParticles: number;
    /** Strength of the rain rings on the water, and of the storm's lightning (P09-R05). */
    readonly rainRings: number;
    readonly lightning: number;
    /** How bright the lightning flash is on this frame (0..1). */
    readonly flash: number;
    readonly aurora: number;
    readonly groundLights: number;
    readonly sunIntensity: number;
    readonly fogEnd: number;
    /** Phase 10: lava, its depth under the playfield's middle, plumes drawn, shot style. */
    readonly lava: boolean;
    readonly liquidDepth: number;
    readonly plumes: number;
    readonly shotStyle: string;
  };
}

/** What `window.__GAME_TEST__.getState()` returns. */
export interface GameTestState {
  readonly screen: MenuScreen;
  readonly selection: number;
  readonly selectedId: string | null;
  readonly highlightedShipId: string;
  readonly chosenShipId: string | null;
  readonly chosenLevelId: string | null;
  readonly transitioning: boolean;
  /** The "Level complete" result, while its overlay shows (P06-R03). */
  readonly levelResult: LevelResult | null;
  /** The choice selected on a "Game over" panel with a checkpoint: 0 Continue (P07-R08). */
  readonly choice: number;
  /** Goes up each time a level starts, or starts again from a checkpoint. */
  readonly attempt: number;
  /** The saved high score (P11-R03). */
  readonly highScore: number;
  /** Every progress value the loading screen showed, in order. */
  readonly loadingProgress: readonly number[];
  /** The level being played, on the game screen (P06). */
  readonly game: GameTestLevelState | null;
  /** Whether the level being played is paused (P12-R01, P12-R12). */
  readonly paused: boolean;
  /** Whether the pause menu asks `Leave the level?` (P12-R02). */
  readonly leaving: boolean;
  /** The music and sound effect volumes, in slider steps (P12-R04). */
  readonly volumes: { readonly music: number; readonly sfx: number };
  /** Id of the music playing (`menu`, `level-2-3`, `boss-2`), or null (P12-R12). */
  readonly music: string | null;
  /** Names of the last sound effects played, most recent last (P12-R12). */
  readonly sounds: readonly string[];
  /** The audio context's state: `none` before the first user gesture (P12-R05). */
  readonly audio: string;
}

/** The e2e test API (ENG-52), installed as `window.__GAME_TEST__` in e2e builds only. */
export interface GameTestApi {
  getState(): GameTestState;
  /**
   * Sends a menu action as an input device would (P01-R12; `pause` and `resume` pause and resume
   * a level, P12-R12), or `bomb`: sets a bomb off in the level being played, as the bomb key
   * would (P11-R08).
   */
  sendAction(action: MenuAction | 'bomb'): void;
  /**
   * Runs `frames` frames of 1/60 s at once (menus, transitions, the level being played), then
   * renders once, unless `render` is false. The app has no render loop in e2e builds: nothing
   * moves between two calls.
   */
  step(frames: number, render?: boolean): void;
  /** Steps the app by `seconds` (rounded up to whole frames). */
  advance(seconds: number): void;
}

/** What the test API reads of the audio (P12-R12). */
export interface GameTestAudio {
  readonly music: string | null;
  readonly sounds: readonly string[];
  readonly context: string;
}

/** What the test API reads from and sends to the running app. */
export interface GameTestHooks {
  readonly state: () => Omit<
    GameTestState,
    'loadingProgress' | 'game' | 'highScore' | 'music' | 'sounds' | 'audio'
  >;
  readonly audio: () => GameTestAudio;
  readonly highScore: () => number;
  readonly loadingProgress: () => readonly number[];
  readonly game: () => GameTestLevelState | undefined;
  readonly send: (action: MenuAction) => void;
  readonly bomb: () => void;
  readonly step: (frames: number, render: boolean) => void;
  /** Frames per second of {@link GameTestApi.step}. */
  readonly stepHz: number;
}

/** Installs `__GAME_TEST__` on `target` (the window). Only call it when `__E2E__` is true. */
export function installTestApi(target: object, hooks: GameTestHooks): GameTestApi {
  const api: GameTestApi = {
    getState: () => {
      const { music, sounds, context } = hooks.audio();
      return {
        ...hooks.state(),
        music,
        sounds: [...sounds],
        audio: context,
        highScore: hooks.highScore(),
        loadingProgress: [...hooks.loadingProgress()],
        game: hooks.game() ?? null,
      };
    },
    sendAction: (action) => {
      if (action === 'bomb') {
        hooks.bomb();
        return;
      }
      if (!isMenuAction(action)) throw new TypeError(`Unknown menu action "${String(action)}"`);
      hooks.send(action);
    },
    step: (frames, render = true) => {
      if (!Number.isInteger(frames) || frames < 0) {
        throw new RangeError(`Cannot step by ${String(frames)} frames`);
      }
      hooks.step(frames, render);
    },
    advance: (seconds) => {
      if (!(seconds >= 0)) throw new RangeError(`Cannot advance by ${String(seconds)} s`);
      hooks.step(Math.ceil(seconds * hooks.stepHz - 1e-9), true);
    },
  };
  Object.defineProperty(target, '__GAME_TEST__', { value: api, configurable: true });
  return api;
}
