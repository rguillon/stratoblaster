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
  /** Farms of World 1's green land (reviewer, 2026-10-26): pale panelled walls, dark roofs. */
  farmWall: [0.66, 0.64, 0.6],
  farmRoof: [0.2, 0.21, 0.25],
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
  /**
   * World 3 (phase 9): dark wet soil and red-brown mud, moss, the canopy's greens (deep, mid,
   * sunlit, yellowish and blue-green, so packed crowns read as separate trees), grey-green mossy
   * stone and old paving, red dirt, rusty and dark metal, reeds, lily pads, white water.
   */
  jungleSoil: [0.2, 0.16, 0.11],
  mud: [0.38, 0.24, 0.15],
  redDirt: [0.5, 0.27, 0.16],
  moss: [0.26, 0.37, 0.14],
  mossDark: [0.15, 0.24, 0.1],
  canopy: [0.15, 0.34, 0.12],
  canopyDark: [0.09, 0.22, 0.09],
  canopyLight: [0.28, 0.46, 0.14],
  canopyYellow: [0.37, 0.46, 0.13],
  canopyBlue: [0.1, 0.29, 0.21],
  fern: [0.21, 0.43, 0.16],
  jungleBark: [0.33, 0.27, 0.2],
  swampBark: [0.23, 0.2, 0.16],
  hangingMoss: [0.42, 0.45, 0.3],
  reed: [0.42, 0.43, 0.19],
  cattail: [0.32, 0.21, 0.12],
  lilyPad: [0.19, 0.4, 0.17],
  lilyFlower: [0.86, 0.55, 0.68],
  mossStone: [0.42, 0.43, 0.35],
  mossStoneDark: [0.29, 0.32, 0.25],
  paving: [0.51, 0.48, 0.41],
  bamboo: [0.55, 0.48, 0.3],
  corrugated: [0.4, 0.36, 0.31],
  log: [0.43, 0.31, 0.2],
  logEnd: [0.63, 0.49, 0.33],
  rustDark: [0.3, 0.17, 0.11],
  jungleMetal: [0.22, 0.25, 0.23],
  damConcrete: [0.56, 0.55, 0.5],
  riverWater: [0.23, 0.29, 0.2],
  foam: [0.87, 0.91, 0.91],
  spray: [0.76, 0.82, 0.83],
  /**
   * World 4 (phase 10): soot black and basalt, grey ash (lighter on the roofs it covers), charred
   * wood, rust red and sulphur yellow mineral stains, dark industrial iron, dark slag, hardy
   * yellow-green grass, the steaming water of the hot springs and the pale steam itself.
   */
  soot: [0.07, 0.07, 0.075],
  basalt: [0.15, 0.15, 0.16],
  basaltLight: [0.25, 0.24, 0.24],
  ash: [0.5, 0.49, 0.47],
  ashLight: [0.63, 0.62, 0.6],
  ashDark: [0.35, 0.34, 0.33],
  charred: [0.13, 0.1, 0.08],
  charcoal: [0.08, 0.07, 0.06],
  rustRed: [0.47, 0.17, 0.09],
  sulphur: [0.78, 0.68, 0.16],
  sulphurDark: [0.55, 0.46, 0.12],
  iron: [0.23, 0.22, 0.22],
  ironDark: [0.12, 0.12, 0.13],
  slag: [0.11, 0.1, 0.1],
  hardyGrass: [0.4, 0.41, 0.2],
  hardyGrassDark: [0.26, 0.3, 0.15],
  hotWater: [0.34, 0.55, 0.54],
  steam: [0.8, 0.82, 0.83],
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
  /** World 3 (phase 9): the bio-labs' toxic green, and the enemy's violet neon in the ruins. */
  toxic: [0.42, 1, 0.16],
  toxicDim: [0.2, 0.48, 0.08],
  violet: [0.62, 0.2, 1],
  /**
   * World 4 (phase 10): molten metal, the furnaces' glowing mouths, lava and glowing slag (dimmer,
   * as there is a lot of it), and the enemy's orange neon in the foundries and the war factory.
   */
  molten: [1, 0.7, 0.22],
  furnace: [1, 0.36, 0.06],
  lava: [0.95, 0.3, 0.05],
  slagGlow: [0.55, 0.16, 0.03],
  orange: [1, 0.45, 0.05],
} as const;
