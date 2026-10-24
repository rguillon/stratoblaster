import { SCENERY_VIEWER_CONFIG } from './scenery-viewer';

/**
 * Tunables of the enemies debug page (`enemies/`, P05-R11). Logical pixels, Y up, origin at the
 * bottom left of the playfield; times in seconds.
 */
export const ENEMY_VIEWER_CONFIG = {
  /** Fixed simulation rate (ENG-100) and the most steps run in one frame. */
  stepHz: 60,
  maxStepsPerFrame: 5,
  /** Longest frame time used, so a stall does not jump the animations. */
  maxFrameSeconds: 0.1,
  environmentCubeSize: 64,
  /** The Level Zero scenery, as on `level_zero/`. */
  stage: SCENERY_VIEWER_CONFIG.stage,
  /** Where the player ship starts, and how close to the visible edges it may fly. */
  shipStart: { x: 240, y: 90 },
  shipMargin: { side: 18, bottom: 30, top: 200 },
  /** Player shots leave this far below the tip of the ship's nose (as on `player_shots/`). */
  muzzleInset: 3,
  /** Shots and enemies this far outside the playfield are removed. */
  cullMargin: 80,
  /** Enemies older than this are removed, whatever they do. */
  maxEnemyAge: 40,
  /** A new group appears this long after the last one has gone. */
  respawnDelay: 1,
  seed: 505,
  /**
   * Model view (phase 5 review: like `player_ship/`, close up, dark background): turns per
   * second, share of the screen width the model fills, how far the wheel zooms in and out, and
   * the camera angles: from -Z (behind the model), 45° above it, as the enemies are flat ships
   * mostly seen from above.
   */
  closeUp: {
    spinRadPerSec: 0.6,
    fill: 0.6,
    zoom: [0.4, 3],
    alpha: -Math.PI / 2,
    beta: Math.PI / 4,
  },
  /** Debug tile: FPS averaged over `fpsWindow` s, text refreshed every `refresh` s. */
  stats: { fpsWindow: 0.5, refresh: 0.25 },
} as const;
