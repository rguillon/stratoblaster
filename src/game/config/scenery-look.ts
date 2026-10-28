type Rgb = readonly [number, number, number];

/** P04-R05: the camera above the playfield, tilted 35° from straight down, looking forward. */
/** The playfield camera; the ground drawn twice as big, as if flying lower (reviewer, 2026-10-28). */
export const PLAYFIELD_CAMERA = {
  tiltDeg: 35,
  fovDeg: 40,
  flightAltitude: 320,
  groundScale: 2,
} as const;

interface TextureExtras {
  readonly speckle?: number;
  readonly speckleColor?: Rgb;
  readonly strata?: number;
  readonly octaves?: number;
  readonly cracks?: number;
}

/** A generated ground texture: three colours and a noise frequency, plus extras. */
export const texture = (
  colors: readonly [Rgb, Rgb, Rgb],
  frequency: number,
  extra: TextureExtras = {},
) => ({
  colors,
  frequency,
  octaves: extra.octaves ?? 5,
  speckle: extra.speckle ?? 0,
  speckleColor: extra.speckleColor ?? colors[0],
  strata: extra.strata ?? 0,
  ...(extra.cracks === undefined ? {} : { cracks: extra.cracks }),
});

/**
 * Level Zero's look: a dusty wasteland in late-afternoon light (low, warm sun ahead of the
 * camera, light haze), wet dark sand on the shores, grey-brown rock on slopes, dirty snow on
 * the peaks, a dark teal sea and two cloud layers. Gamma-space RGB, 0..1.
 */
export const LEVEL_ZERO_LOOK = {
  sky: {
    haze: [0.74, 0.65, 0.56],
    stops: [
      { at: -1, color: [0.25, 0.22, 0.2] },
      { at: 0, color: [0.92, 0.76, 0.58] },
      { at: 0.35, color: [0.62, 0.68, 0.8] },
      { at: 1, color: [0.3, 0.45, 0.72] },
    ],
    environmentIntensity: 0.6,
  },
  fog: { start: 1000, end: 2600 },
  sun: {
    elevationDeg: 38,
    azimuthDeg: 25,
    color: [1, 0.84, 0.64],
    intensity: 1.6,
    shadow: { mapSize: 2048, frustum: 1600, bias: 0.0008, normalBias: 0.6, darkness: 0.35 },
  },
  ambient: { sky: [0.62, 0.68, 0.8], ground: [0.36, 0.3, 0.24], intensity: 0.6 },
  terrain: {
    textureSize: 256,
    tileSize: 150,
    low: texture(
      [
        [0.3, 0.27, 0.22],
        [0.38, 0.33, 0.26],
        [0.45, 0.4, 0.32],
      ],
      16,
      { speckle: 0.02 },
    ),
    ground: texture(
      [
        [0.5, 0.4, 0.27],
        [0.6, 0.48, 0.32],
        [0.68, 0.57, 0.4],
      ],
      12,
      {
        speckle: 0.03,
        speckleColor: [0.3, 0.25, 0.2],
      },
    ),
    steep: texture(
      [
        [0.3, 0.29, 0.28],
        [0.4, 0.39, 0.37],
        [0.5, 0.49, 0.47],
      ],
      8,
      { strata: 0.3 },
    ),
    high: texture(
      [
        [0.74, 0.74, 0.76],
        [0.83, 0.83, 0.85],
        [0.9, 0.9, 0.92],
      ],
      8,
      { octaves: 3 },
    ),
    /** Phase 4 review: grass of the meadows, with a few dry yellow tufts. */
    lush: texture(
      [
        [0.2, 0.3, 0.11],
        [0.28, 0.4, 0.15],
        [0.37, 0.49, 0.2],
      ],
      14,
      { speckle: 0.04, speckleColor: [0.55, 0.52, 0.26] },
    ),
    /** Phase 4 review: worn concrete of the industrial zone and the city centre. */
    paved: texture(
      [
        [0.33, 0.33, 0.34],
        [0.41, 0.41, 0.42],
        [0.49, 0.49, 0.5],
      ],
      10,
      { speckle: 0.03, speckleColor: [0.22, 0.22, 0.23] },
    ),
    /** Phase 6: desert sand (Level Zero has none; World 1 has its own look). */
    sand: texture(
      [
        [0.66, 0.53, 0.35],
        [0.76, 0.62, 0.42],
        [0.84, 0.71, 0.5],
      ],
      18,
      { speckle: 0.02, speckleColor: [0.5, 0.38, 0.24] },
    ),
    lowHeight: 7,
    highHeight: 205,
    heightBlend: 12,
    steepSlope: [0.22, 0.45],
    jitter: { height: 30, slope: 0.2 },
    noiseTileSize: 300,
    tints: [
      [1.04, 0.98, 0.9],
      [0.82, 0.8, 0.78],
    ],
    tintTileSize: 1600,
    shore: {
      sand: [0.72, 0.62, 0.45],
      beach: 4,
      shallow: [0.1, 0.5, 0.48],
      deep: [0.03, 0.17, 0.2],
      depth: 30,
      foam: { color: [0.92, 0.94, 0.92], width: 0.7, spacing: 2.5, speed: 0.3, reach: 7 },
    },
    specular: 0,
  },
  sea: {
    color: [0.03, 0.17, 0.2],
    alpha: 0.4,
    roughness: 0.3,
    sunGlint: 1.6,
    normalMap: { size: 256, frequency: 5, octaves: 3, strength: 4 },
    tileSize: 320,
    drift: [3, 7],
  },
  /** Both layers fly above the highest peaks (250) and under the ships (320). */
  clouds: [
    {
      altitude: 265,
      coverage: 0.3,
      opacity: 0.75,
      tileSize: 1100,
      drift: [6, 3],
      softness: 0.12,
      color: [0.98, 0.95, 0.9],
      shade: [0.72, 0.7, 0.72],
    },
    {
      altitude: 295,
      coverage: 0.2,
      opacity: 0.5,
      tileSize: 1600,
      drift: [10, -2],
      softness: 0.18,
      color: [1, 0.97, 0.93],
      shade: [0.8, 0.78, 0.8],
    },
  ],
  /**
   * P04-R07: worn dusty asphalt for the roads, packed dust for the paths, both slightly
   * see-through with soft edges, so they blend with the ground (phase 4 review).
   */
  roads: {
    main: [0.36, 0.33, 0.3],
    cross: [0.66, 0.57, 0.43],
    opacity: { main: 0.85, cross: 0.6 },
    shoulder: 2.5,
    // Review: hard-edged streets, so their crossings and corners stay square.
    streetShoulder: 0.4,
    wear: 0.3,
    lift: 0.6,
    centreLine: {
      color: [0.7, 0.56, 0.12],
      laneColor: [0.7, 0.7, 0.66],
      width: 0.35,
      dash: 4,
      lift: 0.05,
    },
    /** Phase 15 (P15-R02): dark asphalt, grey sidewalks and pale kerbs on the tiles. */
    tiles: {
      roadway: [0.2, 0.2, 0.22],
      sidewalk: [0.38, 0.37, 0.38],
      kerb: [0.55, 0.54, 0.52],
      kerbWidth: 0.35,
      centreLine: [0.7, 0.56, 0.12],
      laneLine: [0.6, 0.6, 0.58],
      lineWidth: 0.3,
      lift: 0.15,
    },
  },
  /** Matte props: specular highlights on their facets flickered as the view scrolled (review). */
  props: { specular: 0, lightIntensity: 1 },
  glow: { intensity: 0.3, blurKernelSize: 16 },
} as const;
