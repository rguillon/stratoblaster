/** What a viewer page's e2e test API drives: one frame of the page, and its rendering. */
export interface ViewerStepHooks {
  /** Advances the page by one frame of `dt` seconds, without rendering. */
  readonly frame: (dt: number) => void;
  /** Renders the scene the page shows. */
  readonly render: () => void;
}

/**
 * Advances a viewer page by `frames` frames of 1/60 s, then renders once (ENG-52). Viewer pages
 * have no render loop in e2e builds: nothing moves between two calls.
 */
export function stepFrames(hooks: ViewerStepHooks, frames: number): void {
  if (!Number.isInteger(frames) || frames < 0) {
    throw new RangeError(`Cannot step by ${String(frames)} frames`);
  }
  for (let i = 0; i < frames; i++) hooks.frame(1 / 60);
  hooks.render();
}

/** The e2e test API of a viewer page that reports no state (`player_shots/`). */
export interface ViewerTestApi {
  /** Advances the page by `frames` frames of 1/60 s, then renders once. */
  step(frames: number): void;
}

/**
 * Installs a {@link ViewerTestApi} as `target[name]` (the window). Only call it when `__E2E__`
 * is true.
 */
export function installViewerTestApi(
  target: object,
  name: '__SCENERY_TEST__' | '__SHOTS_TEST__' | '__PROPS_TEST__',
  hooks: ViewerStepHooks,
): ViewerTestApi {
  const api: ViewerTestApi = {
    step: (frames) => {
      stepFrames(hooks, frames);
    },
  };
  Object.defineProperty(target, name, { value: api, configurable: true });
  return api;
}
