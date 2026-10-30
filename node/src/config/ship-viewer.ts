/** Tunables of the player ship viewer page (`player_ship/`). */
export const SHIP_VIEWER_CONFIG = {
  /** Distance between two ship centres, in world units. Must exceed the largest wingspan. */
  spacing: 8,
  rotationSpeedRadPerSec: 0.6,
  clearColor: [0.05, 0.02, 0.1, 1],
  camera: {
    /** Horizontal angle: -π/2 looks from -Z towards +Z. */
    alpha: -Math.PI / 2,
    /** Angle from the vertical axis. */
    beta: 1.15,
    /** Fixed horizontal field of view, so the 3 ships always fit the width. */
    horizontalFov: 1.0,
    /** Extra room around the row of ships (1 = ships touch the screen edges). */
    framingMargin: 1.1,
    minZoomFactor: 0.3,
    maxZoomFactor: 2.5,
  },
  lights: {
    ambientIntensity: 0.35,
    keyIntensity: 2.2,
    keyDirection: [-0.4, -1, 0.6],
    rimIntensity: 1.2,
    rimDirection: [0.6, -0.3, -1],
  },
  environment: {
    cubeSize: 64,
    intensity: 1.1,
    stops: [
      { at: -1, color: [0.03, 0.02, 0.06] },
      { at: -0.1, color: [0.12, 0.08, 0.2] },
      { at: 0, color: [0.95, 0.55, 0.85] },
      { at: 0.12, color: [0.45, 0.6, 1] },
      { at: 1, color: [0.85, 0.9, 1] },
    ],
  },
  glow: { intensity: 0.9, blurKernelSize: 48 },
} as const;
