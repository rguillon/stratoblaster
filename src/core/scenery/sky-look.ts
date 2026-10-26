import { OVERCAST, SKY_STOPS, TIME_OF_DAY, UNDERGLOW } from '../../config/time-of-day';
import { WEATHER_KINDS } from '../../config/weather';
import { smoothstep } from '../math/noise';
import type { Atmosphere, AtmosphereChange, CloudCover, TimeOfDay, Weather } from './atmosphere';

// A level's look as its data describes it (P08-R04, R05): a time of day, a cloud cover and a
// weather, turned into an `Atmosphere` with the engine's time-of-day presets.

type Rgb = readonly [number, number, number];

/** How a level looks at one place along it (P08-R04). */
export interface SkyLook {
  readonly timeOfDay: TimeOfDay;
  /** Cover (0 = clear, 1 = overcast) of the low and the high cloud layers. */
  readonly clouds: readonly [low: number, high: number];
  /** How stormy the clouds look: 0 = the time of day's colour, 1 = dark storm grey. */
  readonly storm?: number;
  /** Weather (P08-R05); none when omitted. */
  readonly weather?: Weather;
  /** Strength (0..1) of an aurora in the night haze. */
  readonly aurora?: number;
  /** Phase 9: strength (0..1) of the lightning of a storm (P09-R05). */
  readonly lightning?: number;
  /**
   * Phase 9: a mist (P09-R04, the 3-1 morning): the fog ends at `fog` of its distance (1 = as
   * far as usual) and the haze turns `white` (0..1) of the way to the mist's pale colour.
   */
  readonly mist?: { readonly fog: number; readonly white: number };
  /** Phase 9: a tint (RGB factors) on the ambient light, e.g. green under the canopy. */
  readonly tint?: Rgb;
  /** Phase 10: a second weather at the same time (P10-R06: falling ash and embers together). */
  readonly secondWeather?: Weather;
  /** Phase 10: a tint (RGB factors) on the clouds' colours, e.g. ash-brown clouds. */
  readonly cloudTint?: Rgb;
  /**
   * Phase 10: a glow from below in `color` (fire, lava), lighting the clouds, the haze and the
   * ambient light from the ground, `strength` 0..1 (`UNDERGLOW`).
   */
  readonly underglow?: { readonly color: Rgb; readonly strength: number };
}

/**
 * The look of a level along its length: `start`, and changes over stretches given in seconds
 * of scrolling from the level's start (the stage turns them into distances at its speed).
 */
export interface SkyScript {
  readonly start: SkyLook;
  readonly changes?: readonly AtmosphereChange<SkyLook>[];
}

/** What a level's own look gives the atmosphere: its fog and its cloud layers' opacity. */
export interface SkyBase {
  readonly fog: { readonly start: number; readonly end: number };
  readonly cloudOpacity: readonly number[];
}

/** No weather. */
export const CLEAR: Weather = { kind: 'snow', strength: 0 };

/** The colour a mist turns the haze to (phase 9). */
export const MIST_COLOR: Rgb = [0.9, 0.92, 0.9];

const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;
const mix = (a: Rgb, b: Rgb, t: number): Rgb => [
  lerp(a[0], b[0], t),
  lerp(a[1], b[1], t),
  lerp(a[2], b[2], t),
];
const scale = (c: Rgb, k: number): Rgb => [c[0] * k, c[1] * k, c[2] * k];
const times = (c: Rgb, k: Rgb): Rgb => [c[0] * k[0], c[1] * k[1], c[2] * k[2]];

/** The haze of `weather` (phase 9: rain greys it), over `haze`. */
function weatherHaze(haze: Rgb, weather: Weather): Rgb {
  const tint = WEATHER_KINDS[weather.kind]?.haze;
  if (!tint) return haze;
  return mix(haze, tint.color, tint.share * Math.min(1, Math.max(0, weather.strength)));
}

/** How far the fog comes in for `weather`: 1 in clear weather, down to its kind's `fogAt1`. */
export function weatherFog(weather: Weather): number {
  const kind = WEATHER_KINDS[weather.kind];
  const strength = Math.min(1, Math.max(0, weather.strength));
  return kind ? lerp(1, kind.fogAt1, strength) : 1;
}

/** No glow from below. */
const NO_UNDERGLOW = { color: [0, 0, 0] as Rgb, strength: 0 };

/**
 * The cloud layers of `look`: the time of day's colours, greyed by a storm, tinted, lit from
 * below (phase 10), thinned when heavy.
 */
function cloudsOf(look: SkyLook, base: SkyBase, colors: { color: Rgb; shade: Rgb }): CloudCover[] {
  const storm = look.storm ?? 0;
  const tint = look.cloudTint ?? [1, 1, 1];
  const glow = look.underglow ?? NO_UNDERGLOW;
  const [lit, edge] = [UNDERGLOW.cloud * glow.strength, UNDERGLOW.shade * glow.strength];
  const color = mix(times(mix(colors.color, OVERCAST.storm.color, storm), tint), glow.color, lit);
  const shade = mix(times(mix(colors.shade, OVERCAST.storm.shade, storm), tint), glow.color, edge);
  return look.clouds.map((coverage, i) => ({
    coverage,
    opacity:
      (base.cloudOpacity[i] ?? base.cloudOpacity.at(-1) ?? 1) *
      (1 - OVERCAST.thinning * smoothstep(0.5, 1, coverage)),
    color,
    shade,
  }));
}

/** The optional parts of `look`, with their defaults. */
function optionsOf(look: SkyLook) {
  return {
    weather: look.weather ?? CLEAR,
    second: look.secondWeather ?? CLEAR,
    mist: look.mist ?? { fog: 1, white: 0 },
    glow: look.underglow ?? NO_UNDERGLOW,
    tint: look.tint ?? ([1, 1, 1] as Rgb),
  };
}

/**
 * The atmosphere of `look` (P08-R04): its time of day's light, dimmed and softened under a heavy
 * cloud cover, its clouds, and the fog of `base` brought in by the time of day and the weather.
 */
export function resolveSky(look: SkyLook, base: SkyBase): Atmosphere {
  const preset = TIME_OF_DAY[look.timeOfDay];
  const o = smoothstep(OVERCAST.overcast[0], OVERCAST.overcast[1], look.clouds[0]);
  const clouds = cloudsOf(look, base, preset.clouds);
  const { weather, second, mist, glow, tint } = optionsOf(look);
  // The weathers and the mist bring the end of the haze in, its start only half as much.
  const near = weatherFog(weather) * weatherFog(second) * mist.fog;
  const fogEnd = preset.fog * near;
  const fogStart = (preset.fog * (1 + near)) / 2;
  const cloudColor = clouds[0]?.color ?? preset.clouds.color;
  const haze = mix(preset.sky.haze, scale(cloudColor, 0.9), OVERCAST.hazeGrey * o);
  return {
    sun: {
      ...preset.sun,
      intensity: preset.sun.intensity * (1 - OVERCAST.sunDim * o),
      shadowDarkness: lerp(OVERCAST.shadowDarkness, OVERCAST.softShadows, o),
    },
    sky: {
      haze: mix(
        mix(weatherHaze(weatherHaze(haze, weather), second), MIST_COLOR, mist.white),
        glow.color,
        UNDERGLOW.haze * glow.strength,
      ),
      stops: preset.sky.gradient.map((color, i) => ({ at: SKY_STOPS[i] ?? 0, color })),
      environmentIntensity: preset.sky.environmentIntensity,
    },
    ambient: {
      sky: times(preset.ambient.sky, tint),
      ground: mix(times(preset.ambient.ground, tint), glow.color, UNDERGLOW.ground * glow.strength),
      intensity: preset.ambient.intensity * (1 + OVERCAST.ambientGain * o),
    },
    fog: { start: base.fog.start * fogStart, end: base.fog.end * fogEnd },
    clouds,
    groundLights: preset.groundLights,
    weather,
    ...(look.secondWeather ? { secondWeather: second } : {}),
    aurora: look.aurora ?? 0,
    lightning: look.lightning ?? 0,
  };
}

/** `look` at another time of day (the `look=` debug option, P08-R12). */
export function atTimeOfDay(look: SkyLook, timeOfDay: TimeOfDay | undefined): SkyLook {
  return timeOfDay ? { ...look, timeOfDay } : look;
}

/**
 * `look` without its weather, lightning and second weather included (the `weather=0` debug
 * option, P08-R12).
 */
export function withoutWeather(look: SkyLook): SkyLook {
  return {
    ...look,
    weather: CLEAR,
    lightning: 0,
    ...(look.secondWeather ? { secondWeather: CLEAR } : {}),
  };
}

/**
 * How many particles `weather` draws (P08-R05): none at strength 0, its kind's most at 1, in
 * proportion between.
 */
export function weatherParticles(weather: Weather): number {
  const kind = WEATHER_KINDS[weather.kind];
  const strength = Math.min(1, Math.max(0, weather.strength));
  return kind ? Math.round(kind.maxParticles * strength) : 0;
}
