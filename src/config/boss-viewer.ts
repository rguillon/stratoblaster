import { GAME_PLAY_CONFIG } from './game-play';

/**
 * Tunables of the bosses debug page (`bosses/`, P07-R09). Logical pixels, Y up, origin at the
 * bottom left of the playfield; times in seconds.
 */
export const BOSS_VIEWER_CONFIG = {
  /** Fixed simulation rate (ENG-100) and the most steps run in one frame. */
  stepHz: 60,
  maxStepsPerFrame: 5,
  /** Longest frame time used, so a stall does not jump the animations. */
  maxFrameSeconds: 0.1,
  environmentCubeSize: 64,
  /** The levels' scenery, as on the game screen. */
  stage: GAME_PLAY_CONFIG.stage,
  /** Where the player ship starts, and how close to the visible edges it may fly. */
  shipStart: { x: 240, y: 90 },
  shipMargin: GAME_PLAY_CONFIG.shipMargin,
  /** Player shots leave this far below the tip of the ship's nose (as on `enemies/`). */
  muzzleInset: 3,
  /** Shots and enemies this far outside the playfield are removed. */
  cullMargin: 80,
  /** Enemies the bosses launch are removed this old, whatever they do. */
  maxEnemyAge: 40,
  /** A boss comes again this long after the last one blew up. */
  respawnDelay: 1.5,
  seed: 707,
  /** Wireframe view: colours of the core's circle, of the parts that shield it, of the others. */
  circles: {
    core: [1, 0.2, 0.2] as const,
    shield: [1, 0.9, 0.1] as const,
    part: [0.1, 0.9, 1] as const,
  },
  /** Debug tile: FPS averaged over `fpsWindow` s, text refreshed every `refresh` s. */
  stats: { fpsWindow: 0.5, refresh: 0.25 },
} as const;
