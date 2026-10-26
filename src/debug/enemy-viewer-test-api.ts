import { stepFrames, type ViewerStepHooks } from './viewer-test-api';

/** One enemy as the test API reports it. */
export interface EnemyTestState {
  readonly model: string;
  readonly x: number;
  readonly y: number;
  readonly health: number;
}

/** What `window.__ENEMIES_TEST__.getState()` returns on the `enemies/` page. */
export interface EnemyViewerTestState {
  readonly enemies: readonly EnemyTestState[];
  readonly bullets: number;
  readonly missiles: number;
  readonly lasers: readonly string[];
  readonly kills: number;
  readonly score: number;
  readonly player: { readonly x: number; readonly y: number };
}

/** The e2e test API of the `enemies/` page (ENG-52), in e2e builds only. */
export interface EnemyViewerTestApi {
  getState(): EnemyViewerTestState;
  /** Advances the page by `frames` frames of 1/60 s, then renders once (no render loop in e2e). */
  step(frames: number): void;
}

/** Installs `__ENEMIES_TEST__` on `target` (the window). Only call it when `__E2E__` is true. */
export function installEnemyViewerTestApi(
  target: object,
  hooks: ViewerStepHooks & { readonly state: () => EnemyViewerTestState },
): EnemyViewerTestApi {
  const api: EnemyViewerTestApi = {
    getState: hooks.state,
    step: (frames) => {
      stepFrames(hooks, frames);
    },
  };
  Object.defineProperty(target, '__ENEMIES_TEST__', { value: api, configurable: true });
  return api;
}
