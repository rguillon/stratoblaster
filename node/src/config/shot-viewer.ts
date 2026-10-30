/**
 * Tunables of the player shots viewer page (`player_shots/`, P03-R10). Positions in logical
 * pixels, Y up, origin at the bottom left of the playfield.
 */
export const SHOT_VIEWER_CONFIG = {
  /** Fixed simulation rate (ENG-100) and the most steps run in one frame. */
  stepHz: 60,
  maxStepsPerFrame: 5,
  /** Ship centre height. */
  shipY: 80,
  /**
   * Shots from the muzzle start this far below the tip of the ship's nose, measured on each
   * ship's model (phase 3 review: bullets started ahead of the ship).
   */
  muzzleInset: 3,
  /** Shots this far outside the playfield are removed. */
  cullMargin: 40,
  clearColor: [0.02, 0.02, 0.05, 1],
  /** Faint reference grid, to judge angles and speeds; `depth` puts it behind everything. */
  grid: { cell: 40, depth: 200, color: [0.1, 0.12, 0.2] },
  /** Lines along each stream of the selected level (toggled with G). */
  guides: { length: 900, color: [0.55, 0.45, 0.1] },
  /**
   * Dummy targets. A column above the ship shows the laser going through ships; the side
   * targets pull the homing missiles sideways. They sway together and come back after
   * `respawnSeconds` once destroyed.
   */
  targets: {
    radius: 20,
    maxHealth: 300,
    anchors: [
      { x: 240, y: 300 },
      { x: 240, y: 380 },
      { x: 240, y: 460 },
      { x: 240, y: 540 },
      { x: 90, y: 470 },
      { x: 390, y: 470 },
    ],
    swayAmplitude: 40,
    swayHz: 0.12,
    respawnSeconds: 1,
    ring: { thickness: 3, color: [0.85, 0.2, 0.3], deadColor: [0.25, 0.25, 0.3] },
    healthBar: { width: 36, height: 4, gap: 8, color: [0.3, 1, 0.5], backColor: [0.15, 0.15, 0.2] },
  },
  /** Window over which the damage rate is measured, in seconds. */
  damageRateWindow: 1,
  /** Debug tile (phase 3 review): FPS averaged over `fpsWindow` s, text refreshed every `refresh` s. */
  stats: { fpsWindow: 0.5, refresh: 0.25 },
  lights: { ambientIntensity: 0.6, keyIntensity: 2, keyDirection: [0.3, 0.5, 1] },
  environment: {
    cubeSize: 64,
    intensity: 1,
    stops: [
      { at: -1, color: [0.03, 0.02, 0.06] },
      { at: 0, color: [0.4, 0.45, 0.6] },
      { at: 1, color: [0.85, 0.9, 1] },
    ],
  },
  glow: { intensity: 0.35, blurKernelSize: 24 },
} as const;
