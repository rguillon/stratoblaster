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
  /** Every progress value the loading screen showed, in order. */
  readonly loadingProgress: readonly number[];
  /** The level being played, on the game screen (P06). */
  readonly game: GameTestLevelState | null;
}

/** The e2e test API (ENG-52), installed as `window.__GAME_TEST__` in e2e builds only. */
export interface GameTestApi {
  getState(): GameTestState;
  /** Sends a menu action as an input device would (P01-R12). */
  sendAction(action: MenuAction): void;
  /** Runs the level being played for `seconds` at once, without rendering; no level, no-op. */
  advance(seconds: number): void;
}

/** What the test API reads from and sends to the running app. */
export interface GameTestHooks {
  readonly state: () => Omit<GameTestState, 'loadingProgress' | 'game'>;
  readonly loadingProgress: () => readonly number[];
  readonly game: () => GameTestLevelState | undefined;
  readonly send: (action: MenuAction) => void;
  readonly advance: (seconds: number) => void;
}

/** Installs `__GAME_TEST__` on `target` (the window). Only call it when `__E2E__` is true. */
export function installTestApi(target: object, hooks: GameTestHooks): GameTestApi {
  const api: GameTestApi = {
    getState: () => ({
      ...hooks.state(),
      loadingProgress: [...hooks.loadingProgress()],
      game: hooks.game() ?? null,
    }),
    sendAction: (action) => {
      if (!isMenuAction(action)) throw new TypeError(`Unknown menu action "${String(action)}"`);
      hooks.send(action);
    },
    advance: (seconds) => {
      if (!(seconds >= 0)) throw new RangeError(`Cannot advance by ${String(seconds)} s`);
      hooks.advance(seconds);
    },
  };
  Object.defineProperty(target, '__GAME_TEST__', { value: api, configurable: true });
  return api;
}
