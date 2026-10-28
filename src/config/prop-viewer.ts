/** Tunables of the props viewer page (`props/`, reviewer 2026-10-28). World units. */
export const PROP_VIEWER_CONFIG = {
  /** Room between two props of the grid, beyond the largest footprint of the group. */
  gap: 6,
  clearColor: [0.05, 0.02, 0.1, 1],
  camera: { alpha: -Math.PI / 2, beta: 1, fov: 0.8, framingMargin: 1.15 },
  lights: {
    ambientIntensity: 0.7,
    keyIntensity: 1.6,
    keyDirection: [-0.4, -1, 0.6],
  },
  /** Strength of the self-lit parts (windows, lamps, headlights). */
  lightIntensity: 1.2,
  environment: {
    cubeSize: 64,
    intensity: 0.8,
    stops: [
      { at: -1, color: [0.06, 0.05, 0.08] },
      { at: 0, color: [0.5, 0.5, 0.6] },
      { at: 1, color: [0.85, 0.9, 1] },
    ],
  },
  glow: { intensity: 0.6, blurKernelSize: 32 },
  /** Ground under the grid; its margin beyond the props, in tiles. */
  ground: { color: [0.16, 0.16, 0.2], margin: 1 },
  /** Lines of the grid of tiles on the ground (phase 15), above the road tiles. */
  grid: { color: [0.45, 0.5, 0.65], height: 0.3 },
  /** Grid of tiles when the game names none. */
  tile: { size: 10, sidewalk: 2 },
} as const;
