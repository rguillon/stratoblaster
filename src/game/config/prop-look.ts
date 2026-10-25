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
  /** Desert homes and plants (phase 6): rammed earth, solar panels, dry and green leaves. */
  adobe: [0.74, 0.62, 0.47],
  adobeDark: [0.56, 0.45, 0.33],
  adobeRoof: [0.64, 0.55, 0.43],
  solar: [0.07, 0.11, 0.24],
  thatch: [0.52, 0.42, 0.26],
  palmLeaf: [0.27, 0.44, 0.16],
  palmTrunk: [0.42, 0.33, 0.22],
  cactus: [0.27, 0.4, 0.24],
  dryLeaf: [0.46, 0.43, 0.25],
  dryLeafDark: [0.33, 0.3, 0.18],
  /**
   * World 2 (phase 8): snow with a blue-grey shade on its lower faces, ice, snowy pines and pale
   * frosted wood, painted metal of the harbours and mines, insulated panels.
   */
  snow: [0.9, 0.92, 0.96],
  snowShade: [0.7, 0.76, 0.85],
  ice: [0.8, 0.89, 0.95],
  iceBlue: [0.56, 0.73, 0.87],
  iceDeep: [0.36, 0.55, 0.73],
  pine: [0.11, 0.24, 0.17],
  pineDark: [0.07, 0.16, 0.12],
  frost: [0.68, 0.72, 0.76],
  frostDark: [0.45, 0.47, 0.5],
  timber: [0.28, 0.2, 0.15],
  silver: [0.62, 0.65, 0.7],
  polarRed: [0.58, 0.15, 0.13],
  signalOrange: [0.85, 0.42, 0.12],
  mineYellow: [0.72, 0.56, 0.14],
  ore: [0.27, 0.25, 0.24],
  panel: [0.5, 0.56, 0.63],
  panelDark: [0.3, 0.35, 0.41],
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
