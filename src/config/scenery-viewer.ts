/** Tunables of the generated level viewer page (`level_zero/`, P04). World units = logical pixels. */
export const SCENERY_VIEWER_CONFIG = {
  /** Fixed simulation rate (ENG-100) and the most steps run in one frame. */
  stepHz: 60,
  maxStepsPerFrame: 5,
  /** Longest frame time used, so a stall does not jump the animations. */
  maxFrameSeconds: 0.1,
  /** Face size of the generated sky cube used for reflections. */
  environmentCubeSize: 64,
  stage: {
    /** Terrain chunk length along Z, and the grid cell of the terrain mesh. */
    chunkLength: 320,
    cell: 8,
    /** Extra ground generated around what the camera sees. */
    margin: 80,
    /** Cloud layers stay at least this high above the highest ground. */
    cloudClearance: 15,
    sunDistance: 2500,
    farClip: 4000,
  },
  /** Height of the ship's centre on the playfield, in logical pixels from its bottom. */
  shipY: 80,
  /** Simulated seconds per second when fast-forwarding. */
  fastForward: 4,
  /** Seconds skipped by the ← / → keys. */
  seekStep: 10,
  /** Colour of the playfield outline (toggled with O). */
  frameColor: [0.99, 0.93, 0.04],
  /** Debug tile: FPS averaged over `fpsWindow` s, text refreshed every `refresh` s. */
  stats: { fpsWindow: 0.5, refresh: 0.25 },
} as const;
