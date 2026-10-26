/**
 * Darksynth night behind the menus (P01-R05, GD-60; reviewer, 2026-10-26, D-103): a crimson
 * sunset glow behind a black skyline, a dark street of towers with magenta, red and violet
 * windows, signs and roof trims, haze and rain (D-012).
 * Linear RGB, 0..1. Distances in world units; heights in gradient stops go from -1 (bottom)
 * to 1 (top).
 */
const NEON = [
  [1, 0.08, 0.55],
  [1, 0.12, 0.22],
  [0.6, 0.15, 1],
  [1, 0.35, 0.75],
] as const;

const WINDOW_COLORS = [
  [0.95, 0.08, 0.4],
  [0.6, 0.1, 0.9],
  [1, 0.12, 0.18],
] as const;

export const TITLE_LOOK = {
  /** Seed of the city generator: the same city on every run. */
  seed: 2077,
  camera: { position: [0, 4, -8], target: [0, 5.5, 40], fov: 0.8 },
  /** Haze colour; also the clear colour, so the street melts into the distance. */
  horizon: [0.11, 0.01, 0.07],
  fog: { start: 30, end: 190 },
  sky: {
    z: 340,
    width: 900,
    height: 400,
    centerY: 150,
    /** Crimson glow of the sunset near the horizon, through violet, to black higher up. */
    stops: [
      { at: -1, color: [0.34, 0.015, 0.15] },
      { at: -0.7, color: [0.22, 0.02, 0.17] },
      { at: -0.2, color: [0.05, 0.008, 0.08] },
      { at: 1, color: [0.006, 0.002, 0.016] },
    ],
  },
  /** Distant towers, flat, in front of the sky; not fogged. */
  skyline: {
    z: 300,
    y: -10,
    halfWidth: 420,
    width: [10, 30],
    height: [40, 150],
    color: [0.018, 0.004, 0.03],
    windows: {
      cellWidth: 3,
      cellHeight: 4,
      width: 1.4,
      height: 1.8,
      groundFloor: 12,
      litChance: 0.12,
      brightness: [0.35, 0.7],
      colors: WINDOW_COLORS,
    },
  },
  city: {
    /** Length of one city chunk; two chunks scroll end to end. */
    length: 200,
    streetHalfWidth: 9,
    /** `title_city_scroll_speed`, in units per second. */
    scrollSpeed: 8,
    rows: [
      {
        facadeOffset: 0,
        width: [6, 14],
        gap: [1, 3],
        depth: [8, 16],
        height: [14, 55],
        signs: true,
      },
      {
        facadeOffset: 22,
        width: [10, 22],
        gap: [2, 6],
        depth: [10, 20],
        height: [45, 115],
        signs: false,
      },
    ],
    colors: { wall: [0.04, 0.02, 0.06], facade: [0.07, 0.03, 0.09], roof: [0.02, 0.01, 0.035] },
    street: {
      halfWidth: 80,
      color: [0.015, 0.005, 0.025],
      laneX: [-3, 3],
      dash: 3,
      dashPeriod: 8,
      lineWidth: 0.15,
      lineColor: [0.55, 0.04, 0.38],
    },
    windows: {
      cellWidth: 2.2,
      cellHeight: 2.8,
      width: 1.1,
      height: 1.5,
      groundFloor: 3,
      litChance: 0.3,
      brightness: [0.3, 0.75],
      colors: WINDOW_COLORS,
    },
    neonColors: NEON,
    signs: {
      chance: 0.5,
      width: [1.4, 2.6],
      height: [5, 12],
      baseHeight: [3, 16],
      panel: [0.02, 0.01, 0.04],
      lines: 3,
    },
    trim: { chance: 0.35, height: 0.3 },
  },
  rain: {
    count: 260,
    halfWidth: 30,
    height: 30,
    /** Bottom of the rain box. */
    y: -2,
    z: [0, 60],
    length: [0.8, 1.6],
    width: 0.04,
    color: [0.32, 0.12, 0.3],
    /** Fall speed, in units per second. */
    speed: 30,
  },
  ship: {
    position: [0, 1.6, 8],
    /** `title_ship_rotation_speed`. */
    rotationSpeedRadPerSec: 0.3,
    /** Gentle up-and-down float. */
    bobAmplitude: 0.25,
    bobHz: 0.35,
  },
  lights: { ambient: 0.7, key: 2, keyDirection: [-0.3, -1, 0.5] },
  /** Brightness of the neon meshes; the glow layer and tone mapping wash them out above this. */
  neonIntensity: 0.45,
} as const;
