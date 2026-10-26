type Rgb = readonly [number, number, number];

/**
 * A kind of weather (P08-R05): particles falling through the air between the ground and the
 * flight altitude, drawn behind everything on the playfield. Kinds are data, so later worlds can
 * add rain or falling ash without changing how levels use weather.
 */
export interface WeatherKind {
  /** Particles drawn at strength 1 (`snow_flakes_max`; fewer, in proportion, below it). */
  readonly maxParticles: number;
  /** How far the fog ends at strength 1, as a share of its clear-weather distance. */
  readonly fogAt1: number;
  /** Speed they fall at, and the sideways wind at strength 0 and 1 (world units / s). */
  readonly fall: readonly [min: number, max: number];
  readonly wind: readonly [calm: number, strong: number];
  /** Size of a particle (world units) and how much longer it streaks along the wind at 1. */
  readonly size: readonly [min: number, max: number];
  readonly streak: number;
  /** Slow sway of each particle as it falls (world units, cycles a second). */
  readonly sway: readonly [amplitude: number, frequency: number];
  readonly color: Rgb;
  /** Opacity of a particle: kept low so it never hides what flies above it. */
  readonly alpha: number;
  /**
   * Phase 9: `fall` stretches each particle along the way it falls, by `streak` at every
   * strength (rain streaks); `wind` (the default) stretches it sideways at strength 1 only (a
   * blizzard).
   */
  readonly align?: 'wind' | 'fall';
  /** Phase 9: at strength 1 the haze turns `share` of the way to `color` (rain greys it). */
  readonly haze?: { readonly color: Rgb; readonly share: number };
  /**
   * Phase 9: faint rings spreading on the water where drops land (rain): about `perCell` in each
   * square of `cell` world units at strength 1, each growing to `radius` over `period` seconds,
   * as opaque as `alpha` at most, in `color`.
   */
  readonly rings?: {
    readonly color: Rgb;
    readonly cell: number;
    readonly perCell: number;
    readonly radius: number;
    readonly period: number;
    readonly alpha: number;
  };
  /**
   * The box of air they fill around the view: half its width across the level, its length along
   * it, and its bottom and top heights.
   */
  readonly volume: {
    readonly halfWidth: number;
    readonly length: number;
    readonly bottom: number;
    readonly top: number;
  };
}

/** The weather kinds of the engine (P08-R05, P09-R05). */
export const WEATHER_KINDS: Readonly<Record<string, WeatherKind>> = {
  snow: {
    maxParticles: 1500,
    fogAt1: 0.55,
    fall: [26, 48],
    wind: [6, 120],
    size: [1.4, 2.6],
    streak: 4,
    sway: [6, 0.35],
    color: [0.96, 0.97, 1],
    alpha: 0.5,
    volume: { halfWidth: 420, length: 1100, bottom: 0, top: 300 },
  },
  // P09-R05: thin, light streaks falling fast at a slight slant (`rain_streaks_max`).
  rain: {
    maxParticles: 2000,
    fogAt1: 0.6,
    fall: [380, 520],
    wind: [30, 70],
    size: [0.35, 0.55],
    streak: 16,
    sway: [0, 0],
    color: [0.76, 0.81, 0.9],
    alpha: 0.32,
    align: 'fall',
    haze: { color: [0.52, 0.56, 0.6], share: 0.45 },
    rings: { color: [0.86, 0.9, 0.95], cell: 9, perCell: 1, radius: 2.2, period: 0.8, alpha: 0.32 },
    volume: { halfWidth: 420, length: 1100, bottom: 0, top: 300 },
  },
};

/**
 * Lightning (P09-R05), a storm option on top of rain: strikes come every `gap` seconds (drawn
 * from the level's seed), each a flash or, by `double.chance`, two flashes `double.after` apart,
 * so never more than 2 in any second (`lightning_max_flashes`: 3). A flash rises in `rise`
 * seconds and fades out by `flash`, lighting the ambient light and the sky up to `brightness`
 * times the storm's, the haze never past `maxHaze` (never white); `boltChance` of the strikes
 * draw a bolt in the clouds.
 */
export const LIGHTNING = {
  gap: [4, 10] as const,
  flash: 0.15,
  rise: 0.03,
  double: { chance: 0.35, after: 0.25 },
  brightness: 1.8,
  maxHaze: 0.85,
  boltChance: 0.6,
  maxPerSecond: 3,
} as const;
