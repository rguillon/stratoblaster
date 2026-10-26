import type { TimeOfDay } from '../core/scenery/atmosphere';

type Rgb = readonly [number, number, number];

/** How a time of day lights a level (P08-R04), before its clouds and weather. */
export interface TimeOfDayPreset {
  readonly sun: {
    readonly elevationDeg: number;
    readonly azimuthDeg: number;
    readonly color: Rgb;
    readonly intensity: number;
  };
  readonly sky: {
    readonly haze: Rgb;
    /**
     * Colours of the gradient used for reflections only (the camera never sees the sky): under
     * the horizon, at it, a little above, and straight up.
     */
    readonly gradient: readonly [ground: Rgb, horizon: Rgb, low: Rgb, zenith: Rgb];
    readonly environmentIntensity: number;
  };
  readonly ambient: { readonly sky: Rgb; readonly ground: Rgb; readonly intensity: number };
  /** Colour of the clouds and of their thin edges (P08-R04). */
  readonly clouds: { readonly color: Rgb; readonly shade: Rgb };
  /** Brightness of the ground's window, street, neon and car lights. */
  readonly groundLights: number;
  /** Factor on the level's fog distances (the haze comes closer at night). */
  readonly fog: number;
}

/** Heights of the sky gradient's stops (see `TimeOfDayPreset.sky.gradient`). */
export const SKY_STOPS = [-1, 0, 0.35, 1] as const;

/**
 * The six times of day (P08-R04): the sun's height, direction and colour, the sky and haze, the
 * ambient light, the clouds' colour and the ground lights. At night the sun is a dim, cold moon;
 * the reflections' gradient stays lit enough for the ships to show their shapes and colours.
 * Gamma-space RGB, 0..1, as the scenery looks.
 */
export const TIME_OF_DAY: Readonly<Record<TimeOfDay, TimeOfDayPreset>> = {
  dawn: {
    sun: { elevationDeg: 9, azimuthDeg: -62, color: [1, 0.66, 0.46], intensity: 1.45 },
    sky: {
      haze: [0.86, 0.7, 0.68],
      gradient: [
        [0.22, 0.2, 0.24],
        [1, 0.7, 0.54],
        [0.8, 0.66, 0.74],
        [0.38, 0.46, 0.7],
      ],
      environmentIntensity: 0.6,
    },
    ambient: { sky: [0.66, 0.6, 0.72], ground: [0.32, 0.28, 0.32], intensity: 0.7 },
    clouds: { color: [1, 0.76, 0.66], shade: [0.8, 0.54, 0.58] },
    groundLights: 0.7,
    fog: 1,
  },
  morning: {
    sun: { elevationDeg: 30, azimuthDeg: 48, color: [1, 0.95, 0.86], intensity: 1.75 },
    sky: {
      haze: [0.78, 0.86, 0.95],
      gradient: [
        [0.24, 0.26, 0.3],
        [0.88, 0.92, 0.98],
        [0.62, 0.76, 0.93],
        [0.2, 0.42, 0.82],
      ],
      environmentIntensity: 0.7,
    },
    ambient: { sky: [0.64, 0.74, 0.92], ground: [0.32, 0.34, 0.4], intensity: 0.6 },
    clouds: { color: [1, 1, 1], shade: [0.78, 0.81, 0.88] },
    groundLights: 0.15,
    fog: 1,
  },
  midday: {
    sun: { elevationDeg: 62, azimuthDeg: 20, color: [1, 0.97, 0.92], intensity: 1.7 },
    sky: {
      haze: [0.8, 0.85, 0.9],
      gradient: [
        [0.25, 0.25, 0.27],
        [0.86, 0.9, 0.95],
        [0.66, 0.76, 0.9],
        [0.25, 0.48, 0.82],
      ],
      environmentIntensity: 0.7,
    },
    ambient: { sky: [0.68, 0.76, 0.88], ground: [0.34, 0.35, 0.37], intensity: 0.62 },
    clouds: { color: [0.98, 0.98, 0.98], shade: [0.76, 0.78, 0.82] },
    groundLights: 0.1,
    fog: 1,
  },
  afternoon: {
    sun: { elevationDeg: 34, azimuthDeg: 42, color: [1, 0.88, 0.72], intensity: 1.6 },
    sky: {
      haze: [0.82, 0.78, 0.74],
      gradient: [
        [0.26, 0.24, 0.22],
        [0.96, 0.84, 0.66],
        [0.66, 0.7, 0.82],
        [0.3, 0.44, 0.74],
      ],
      environmentIntensity: 0.65,
    },
    ambient: { sky: [0.68, 0.68, 0.76], ground: [0.38, 0.33, 0.3], intensity: 0.6 },
    clouds: { color: [0.98, 0.95, 0.9], shade: [0.74, 0.72, 0.74] },
    groundLights: 0.2,
    fog: 1,
  },
  dusk: {
    sun: { elevationDeg: 7, azimuthDeg: 66, color: [1, 0.52, 0.34], intensity: 1.15 },
    sky: {
      haze: [0.6, 0.46, 0.52],
      gradient: [
        [0.16, 0.14, 0.18],
        [0.98, 0.54, 0.38],
        [0.62, 0.44, 0.6],
        [0.18, 0.2, 0.44],
      ],
      environmentIntensity: 0.55,
    },
    ambient: { sky: [0.54, 0.46, 0.64], ground: [0.24, 0.2, 0.26], intensity: 0.65 },
    clouds: { color: [1, 0.62, 0.52], shade: [0.6, 0.36, 0.46] },
    groundLights: 1.2,
    fog: 0.95,
  },
  night: {
    // A dim, cold moon instead of the sun.
    sun: { elevationDeg: 42, azimuthDeg: -28, color: [0.62, 0.74, 1], intensity: 0.6 },
    sky: {
      haze: [0.07, 0.09, 0.17],
      // Moonlit: the ships' metal still catches some light (readability, P08-R04).
      gradient: [
        [0.08, 0.09, 0.14],
        [0.34, 0.4, 0.56],
        [0.26, 0.32, 0.5],
        [0.14, 0.18, 0.34],
      ],
      environmentIntensity: 0.6,
    },
    ambient: { sky: [0.34, 0.42, 0.64], ground: [0.12, 0.13, 0.2], intensity: 0.6 },
    clouds: { color: [0.42, 0.48, 0.64], shade: [0.22, 0.26, 0.4] },
    groundLights: 1.5,
    fog: 0.85,
  },
};

/**
 * How clouds and storms change the light (P08-R04): a heavy low cover (from `overcast[0]` to
 * full at `overcast[1]`) dims the sun by up to `sunDim`, softens the shadows towards
 * `softShadows`, brightens the ambient light by up to `ambientGain` and greys the haze by up to
 * `hazeGrey`; heavy layers turn see-through by up to `thinning` so the ground still shows. A
 * storm turns the clouds towards `storm`.
 */
export const OVERCAST = {
  overcast: [0.45, 1] as const,
  sunDim: 0.6,
  shadowDarkness: 0.35,
  softShadows: 0.85,
  ambientGain: 0.45,
  hazeGrey: 0.35,
  thinning: 0.65,
  storm: { color: [0.36, 0.38, 0.42] as Rgb, shade: [0.22, 0.23, 0.26] as Rgb },
} as const;

/**
 * Phase 10: a glow from below (P10-R04: fire and lava lighting the clouds, the haze and the
 * ambient light from the ground): at strength 1 the clouds' edges turn `shade` of the way to its
 * colour, their body `cloud` of the way (dark smoke stays dark), the haze `haze` and the ambient light from the ground
 * `ground` of the way.
 */
export const UNDERGLOW = { shade: 0.75, cloud: 0.2, haze: 0.35, ground: 0.6 } as const;
