import type { MenuScreen } from '../core/menu/menu-screen';
import { isMenuAction, type MenuAction } from '../input/menu-action';

/** What `window.__GAME_TEST__.getState()` returns. */
export interface GameTestState {
  readonly screen: MenuScreen;
  readonly selection: number;
  readonly selectedId: string | null;
  readonly highlightedShipId: string;
  readonly chosenShipId: string | null;
  readonly chosenLevelId: string | null;
  readonly transitioning: boolean;
  /** Every progress value the loading screen showed, in order. */
  readonly loadingProgress: readonly number[];
}

/** The e2e test API (ENG-52), installed as `window.__GAME_TEST__` in e2e builds only. */
export interface GameTestApi {
  getState(): GameTestState;
  /** Sends a menu action as an input device would (P01-R12). */
  sendAction(action: MenuAction): void;
}

/** What the test API reads from and sends to the running app. */
export interface GameTestHooks {
  readonly state: () => Omit<GameTestState, 'loadingProgress'>;
  readonly loadingProgress: () => readonly number[];
  readonly send: (action: MenuAction) => void;
}

/** Installs `__GAME_TEST__` on `target` (the window). Only call it when `__E2E__` is true. */
export function installTestApi(target: object, hooks: GameTestHooks): GameTestApi {
  const api: GameTestApi = {
    getState: () => ({ ...hooks.state(), loadingProgress: [...hooks.loadingProgress()] }),
    sendAction: (action) => {
      if (!isMenuAction(action)) throw new TypeError(`Unknown menu action "${String(action)}"`);
      hooks.send(action);
    },
  };
  Object.defineProperty(target, '__GAME_TEST__', { value: api, configurable: true });
  return api;
}
