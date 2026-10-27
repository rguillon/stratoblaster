import { SCENERY_VIEWER_CONFIG } from './scenery-viewer';

/**
 * Tunables of the game screen (P06-R02, R03, R09). Logical pixels, Y up, origin at the bottom
 * left of the playfield; times in seconds.
 */
export const GAME_PLAY_CONFIG = {
  /**
   * Fixed simulation rate (ENG-100) and the most steps run in one frame: enough for the longest
   * frame (`maxFrameSeconds`) fast-forwarded ×4.
   */
  stepHz: 60,
  maxStepsPerFrame: 25,
  /** Longest frame time used, so a stall does not jump the game. */
  maxFrameSeconds: 0.1,
  environmentCubeSize: 64,
  /** The level's scenery, as on `level_zero/`. */
  stage: SCENERY_VIEWER_CONFIG.stage,
  /** Where the ship starts (from the middle of the bottom edge), and how close to the edges of
   * what the camera shows it may fly. */
  shipStartY: 90,
  shipMargin: { side: 18, bottom: 30, top: 200 },
  /**
   * The ship banks as it moves sideways (phase 6 review): up to `maxDeg` at full sideways speed,
   * easing to its target at `easePerSec` (share of the gap closed per second).
   */
  roll: { maxDeg: 35, easePerSec: 8 },
  /**
   * Hits on the player (phase 6 review): the ship blinks `blinkHz` times a second while
   * invincible (GD-22); a hit makes a spark of radius `hitSpark`, a lost life a blast of radius
   * `shipBlast`; the "Game over" overlay shows `gameOverDelay` after the last life is lost.
   */
  damage: { blinkHz: 10, hitSpark: 6, shipBlast: 16, gameOverDelay: 2 },
  /** Player shots leave this far below the tip of the ship's nose. */
  muzzleInset: 3,
  /** Shots and enemies this far outside the playfield are removed. */
  cullMargin: 80,
  /** Enemies older than this are removed, whatever they do. */
  maxEnemyAge: 40,
  /** `level_end_wait`: the longest wait for the last enemies after the scroll ends (P06-R03). */
  endWait: 10,
  /** Input is ignored this long after the "Level complete" overlay shows, so a held fire key
   * does not skip it. */
  completeDelay: 1,
  /** Seed of the enemies' random choices: a level plays the same every time (P06-R07). */
  seed: 606,
  /** Debug options (P06-R09): F fast-forwards ×4, ← / → jump 10 s. */
  debug: { fastForward: 4, seekStep: 10 },
  /** Debug tile: FPS averaged over `fpsWindow` s, text refreshed every `refresh` s. */
  stats: { fpsWindow: 0.5, refresh: 0.25 },
  /**
   * Phase 14 (P14-R08): the readability probe measures round the ship and round a player shot
   * this far (logical pixels; enemies and bullets use their hit radius), only objects this far
   * inside the view, and only player shots this far ahead of the ship.
   */
  readabilityProbe: { shipRadius: 14, shotRadius: 5, margin: 12, shotAhead: 60 },
} as const;
