/** Engine-wide tunables (ENG-17). Game-specific values go in `src/game/config/`. */
export const ENGINE_CONFIG = {
  /** Fixed simulation rate in Hz (ENG-100). */
  simulationHz: 60,
  /** Maximum simulation steps per rendered frame, to avoid a spiral of death after a stall. */
  maxStepsPerFrame: 5,
  /** Device pixel ratio cap (ENG-110). */
  maxDevicePixelRatio: 2,
  /**
   * e2e builds only (ENG-52): pixels drawn per screen pixel, across, and whether to antialias.
   * The e2e tests check the game's state, not its pixels, and software WebGL (CI) pays per pixel:
   * a quarter of the pixels, without multisampling, makes their frames several times cheaper.
   */
  e2e: { renderScale: 0.5, antialias: false },
} as const;
