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

/** The weather kinds of the engine (P08-R05). */
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
};
