type Rgb = readonly [number, number, number];

/** P04-R05: the camera above the playfield, tilted 35° from straight down, looking forward. */
export const PLAYFIELD_CAMERA = { tiltDeg: 35, fovDeg: 40, flightAltitude: 320 } as const;

interface TextureExtras {
  readonly speckle?: number;
  readonly speckleColor?: Rgb;
  readonly strata?: number;
  readonly octaves?: number;
}

/** A generated ground texture: three colours and a noise frequency, plus extras. */
const texture = (
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
    shadow: { mapSize: 2048, bias: 0.0008, normalBias: 0.6, darkness: 0.35 },
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
    foam: { color: [0.9, 0.92, 0.9], width: 2.5 },
    specular: 0.04,
  },
  sea: {
    color: [0.03, 0.17, 0.2],
    alpha: 0.82,
    roughness: 0.3,
    sunGlint: 1.6,
    normalMap: { size: 256, frequency: 5, octaves: 3, strength: 4 },
    tileSize: 320,
    drift: [3, 7],
  },
  clouds: [
    {
      altitude: 170,
      coverage: 0.3,
      opacity: 0.75,
      tileSize: 1100,
      drift: [6, 3],
      softness: 0.12,
      color: [0.98, 0.95, 0.9],
      shade: [0.72, 0.7, 0.72],
    },
    {
      altitude: 250,
      coverage: 0.2,
      opacity: 0.5,
      tileSize: 1600,
      drift: [10, -2],
      softness: 0.18,
      color: [1, 0.97, 0.93],
      shade: [0.8, 0.78, 0.8],
    },
  ],
  props: { specular: 0.08, lightIntensity: 1 },
  glow: { intensity: 0.5, blurKernelSize: 16 },
} as const;
