/** Engine-wide tunables (ENG-17). Game-specific values go in `src/game/config/`. */
export const ENGINE_CONFIG = {
  /** Fixed simulation rate in Hz (ENG-100). */
  simulationHz: 60,
  /** Maximum simulation steps per rendered frame, to avoid a spiral of death after a stall. */
  maxStepsPerFrame: 5,
  /** Device pixel ratio cap (ENG-110). */
  maxDevicePixelRatio: 2,
} as const;
