/**
 * Colours of the props (P04-R04): weathered concrete and dark metal, with small neon accents
 * (GD-60/61), and grey dead wood. Gamma-space RGB, 0..1.
 */
export const PROP_COLORS = {
  concrete: [0.46, 0.44, 0.41],
  concreteDark: [0.31, 0.3, 0.29],
  rust: [0.4, 0.23, 0.15],
  metal: [0.34, 0.36, 0.4],
  metalDark: [0.17, 0.18, 0.21],
  roof: [0.24, 0.24, 0.26],
  white: [0.8, 0.8, 0.78],
  glass: [0.07, 0.1, 0.14],
  wood: [0.3, 0.25, 0.2],
  woodDark: [0.21, 0.17, 0.14],
  bark: [0.27, 0.2, 0.14],
  leaf: [0.22, 0.4, 0.15],
  leafDark: [0.13, 0.27, 0.12],
  leafLight: [0.36, 0.52, 0.2],
  glassBlue: [0.1, 0.17, 0.26],
  brick: [0.42, 0.26, 0.2],
  containerBlue: [0.14, 0.27, 0.45],
  containerGreen: [0.2, 0.36, 0.24],
  containerRed: [0.5, 0.17, 0.14],
  /** More city facades (phase 4 review). */
  sand: [0.55, 0.48, 0.38],
  glassGreen: [0.09, 0.2, 0.19],
  glassDark: [0.05, 0.06, 0.09],
} as const;

/** Self-lit accents. */
export const PROP_LIGHTS = {
  cyan: [0, 0.94, 1],
  pink: [1, 0.16, 0.53],
  yellow: [0.99, 0.85, 0.1],
  red: [1, 0.12, 0.1],
  window: [1, 0.72, 0.38],
  /** Dimmer window and trim colours for the city, where hundreds of them glow at once. */
  windowDim: [0.5, 0.36, 0.2],
  cyanDim: [0, 0.42, 0.48],
  pinkDim: [0.5, 0.1, 0.3],
  whiteDim: [0.42, 0.42, 0.4],
  yellowDim: [0.45, 0.38, 0.08],
} as const;
