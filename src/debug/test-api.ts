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
}

/** What the test API reads from and sends to the running app. */
export interface GameTestHooks {
  readonly state: () => Omit<GameTestState, 'loadingProgress' | 'game'>;
  readonly loadingProgress: () => readonly number[];
  readonly game: () => GameTestLevelState | undefined;
  readonly send: (action: MenuAction) => void;
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
  };
  Object.defineProperty(target, '__GAME_TEST__', { value: api, configurable: true });
  return api;
}
