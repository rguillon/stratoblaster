/** What `window.__BOSSES_TEST__.getState()` returns on the `bosses/` page (P07-R09). */
export interface BossViewerState {
  readonly boss: {
    readonly id: string;
    readonly name: string;
    readonly state: 'entering' | 'fighting' | 'dying';
    readonly stage: number;
    readonly parts: number;
    readonly partsLeft: number;
    readonly health: number;
    readonly fullHealth: number;
  } | null;
  readonly kills: number;
  readonly bullets: number;
  readonly missiles: number;
  readonly lasers: number;
  readonly groundSpeed: number;
  readonly player: { readonly x: number; readonly y: number };
}

/** The e2e test API of the `bosses/` page (ENG-52, P07-R09), in e2e builds only. */
export interface BossViewerTestApi {
  getState(): BossViewerState;
  /** Advances the page by `frames` frames of 1/60 s. */
  step(frames: number): void;
}

/** Installs `__BOSSES_TEST__` on `target` (the window). Only call it when `__E2E__` is true. */
export function installBossViewerTestApi(
  target: object,
  hooks: { readonly state: () => BossViewerState; readonly frame: (dt: number) => void },
): BossViewerTestApi {
  const api: BossViewerTestApi = {
    getState: hooks.state,
    step: (frames) => {
      for (let i = 0; i < frames; i++) hooks.frame(1 / 60);
    },
  };
  Object.defineProperty(target, '__BOSSES_TEST__', { value: api, configurable: true });
  return api;
}
