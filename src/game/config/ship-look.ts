/** Player ship look (GD-61: shiny grey/blue, blue light behind each reactor). Linear RGB, 0..1. */
export const SHIP_LOOK = {
  hull: { albedo: [0.56, 0.63, 0.74], metallic: 0.9, roughness: 0.25 },
  accent: { albedo: [0.16, 0.3, 0.6], metallic: 0.75, roughness: 0.3 },
  canopy: { albedo: [0.03, 0.08, 0.18], metallic: 0.3, roughness: 0.05, emissive: [0, 0.06, 0.12] },
  trim: { albedo: [0.24, 0.28, 0.36], metallic: 0.85, roughness: 0.3 },
  navLight: { emissive: [0.45, 0.85, 1] },
  nozzle: { albedo: [0.18, 0.2, 0.24], metallic: 1, roughness: 0.45 },
  reactorCore: { emissive: [0.35, 0.75, 1] },
  reactorExhaust: { emissive: [0.1, 0.45, 1], alpha: 0.45 },
  /** Hot inner flame, shorter and whiter than the exhaust cone around it. */
  reactorFlame: { emissive: [0.55, 0.85, 1], alpha: 0.75 },
  /** Plasma puffs flowing down the exhaust. */
  reactorPlasma: { emissive: [0.3, 0.7, 1], alpha: 0.6 },
} as const;

/** Reactor flame animation. Lengths are relative to the exhaust cone; frequencies in Hz. */
export const REACTOR_FLAME = {
  /** Flicker amplitude (± fraction) of the flame length, width and brightness. */
  lengthFlicker: 0.14,
  widthFlicker: 0.06,
  brightnessFlicker: 0.2,
  /** Mixed sine frequencies: incommensurate so the flicker never looks periodic. */
  flickerHz: [5.3, 11.7, 19.1],
  /** Inner flame size, relative to the exhaust cone. */
  coreLength: 0.6,
  coreWidth: 0.55,
  puffCount: 3,
  /** Exhaust lengths travelled per second by a plasma puff. */
  puffSpeed: 1.8,
  /** Puff diameter relative to the nacelle radius, at the nozzle. */
  puffSize: 1.1,
} as const;
