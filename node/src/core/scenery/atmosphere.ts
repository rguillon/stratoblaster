// The changing part of a level's look (phase 8, P08-R04, P08-R05): the time of day, the clouds,
// the haze, the ground lights and the weather (phase 9: rain and lightning; phase 10: ash and embers, two at once), as plain numbers that blend smoothly from one
// look to another along the level. Pure; the renderer applies it to the scene every frame.

type Rgb = readonly [number, number, number];

/** The times of day a level's look can have (P08-R04). */
export const TIMES_OF_DAY = ['dawn', 'morning', 'midday', 'afternoon', 'dusk', 'night'] as const;
export type TimeOfDay = (typeof TIMES_OF_DAY)[number];

/** Whether `value` names a time of day. */
export function isTimeOfDay(value: string): value is TimeOfDay {
  return (TIMES_OF_DAY as readonly string[]).includes(value);
}

/** A colour of the sky gradient at a height (-1 straight down … 1 straight up). */
export interface SkyStop {
  readonly at: number;
  readonly color: Rgb;
}

/** One cloud layer as the atmosphere shows it. */
export interface CloudCover {
  /** Share (0..1) of the sky the layer covers. */
  readonly coverage: number;
  /** 0 = invisible, 1 = opaque. */
  readonly opacity: number;
  readonly color: Rgb;
  /** Colour of the thin edges. */
  readonly shade: Rgb;
}

/** Weather (P08-R05): a kind (e.g. `snow`, a key of the engine's weather kinds) and its strength. */
export interface Weather {
  readonly kind: string;
  /** 0 = none, 1 = the heaviest (a blizzard for snow). */
  readonly strength: number;
}

/** Everything about a level's look that changes with the time of day and the weather. */
export interface Atmosphere {
  readonly sun: {
    readonly elevationDeg: number;
    /** 0 = straight ahead (+Z), positive towards +X. */
    readonly azimuthDeg: number;
    readonly color: Rgb;
    readonly intensity: number;
    /** 0 = black shadows, 1 = no shadows. */
    readonly shadowDarkness: number;
  };
  readonly sky: {
    /** Clear and fog colour. */
    readonly haze: Rgb;
    /** Sky gradient for reflections (sea, metal); every atmosphere of a level has as many stops. */
    readonly stops: readonly SkyStop[];
    readonly environmentIntensity: number;
  };
  readonly ambient: { readonly sky: Rgb; readonly ground: Rgb; readonly intensity: number };
  /** Linear fog, in world units from the camera. */
  readonly fog: { readonly start: number; readonly end: number };
  readonly clouds: readonly CloudCover[];
  /** Brightness of the window, street, neon and car lights of the ground (0 = off). */
  readonly groundLights: number;
  readonly weather: Weather;
  /** Phase 10: a second weather at the same time (P10-R06: ash and embers together). */
  readonly secondWeather?: Weather;
  /** Strength (0..1) of the aurora's curtains in the haze. */
  readonly aurora: number;
  /** Strength (0..1) of a storm's lightning flashes (P09-R05). */
  readonly lightning: number;
}

const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

function lerpRgb(a: Rgb, b: Rgb, t: number): Rgb {
  return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
}

/** Turns `a` towards `b` the short way round, by `t` (degrees). */
function lerpAngle(a: number, b: number, t: number): number {
  const turn = ((((b - a) % 360) + 540) % 360) - 180;
  return a + turn * t;
}

function blendClouds(a: readonly CloudCover[], b: readonly CloudCover[], t: number): CloudCover[] {
  return a.map((ca, i) => {
    const cb = b[i] ?? ca;
    return {
      coverage: lerp(ca.coverage, cb.coverage, t),
      opacity: lerp(ca.opacity, cb.opacity, t),
      color: lerpRgb(ca.color, cb.color, t),
      shade: lerpRgb(ca.shade, cb.shade, t),
    };
  });
}

/** Weather between `a` and `b`: the strength blends; the kind is the one that is there. */
function blendWeather(a: Weather, b: Weather, t: number): Weather {
  const kind = a.strength <= 0 ? b.kind : b.strength <= 0 || t < 0.5 ? a.kind : b.kind;
  return { kind, strength: lerp(a.strength, b.strength, t) };
}

/** No weather (a second weather missing on one side blends from or to it). */
const NO_WEATHER: Weather = { kind: 'snow', strength: 0 };

/** The second weathers of `a` and `b` blended, if either has one (phase 10). */
function blendSecondWeather(a: Atmosphere, b: Atmosphere, t: number): { secondWeather?: Weather } {
  if (!a.secondWeather && !b.secondWeather) return {};
  const [wa, wb] = [a.secondWeather ?? NO_WEATHER, b.secondWeather ?? NO_WEATHER];
  return { secondWeather: blendWeather(wa, wb, t) };
}

/** The atmosphere `t` of the way from `a` to `b` (0 = `a`, 1 = `b`): every number halfway at 0.5. */
export function blendAtmosphere(a: Atmosphere, b: Atmosphere, t: number): Atmosphere {
  if (t <= 0) return a;
  if (t >= 1) return b;
  return {
    sun: {
      elevationDeg: lerp(a.sun.elevationDeg, b.sun.elevationDeg, t),
      azimuthDeg: lerpAngle(a.sun.azimuthDeg, b.sun.azimuthDeg, t),
      color: lerpRgb(a.sun.color, b.sun.color, t),
      intensity: lerp(a.sun.intensity, b.sun.intensity, t),
      shadowDarkness: lerp(a.sun.shadowDarkness, b.sun.shadowDarkness, t),
    },
    sky: {
      haze: lerpRgb(a.sky.haze, b.sky.haze, t),
      stops: a.sky.stops.map((s, i) => ({
        at: s.at,
        color: lerpRgb(s.color, b.sky.stops[i]?.color ?? s.color, t),
      })),
      environmentIntensity: lerp(a.sky.environmentIntensity, b.sky.environmentIntensity, t),
    },
    ambient: {
      sky: lerpRgb(a.ambient.sky, b.ambient.sky, t),
      ground: lerpRgb(a.ambient.ground, b.ambient.ground, t),
      intensity: lerp(a.ambient.intensity, b.ambient.intensity, t),
    },
    fog: { start: lerp(a.fog.start, b.fog.start, t), end: lerp(a.fog.end, b.fog.end, t) },
    clouds: blendClouds(a.clouds, b.clouds, t),
    groundLights: lerp(a.groundLights, b.groundLights, t),
    weather: blendWeather(a.weather, b.weather, t),
    ...blendSecondWeather(a, b, t),
    aurora: lerp(a.aurora, b.aurora, t),
    lightning: lerp(a.lightning, b.lightning, t),
  };
}

/** A change of look over a stretch of the level: from distance `from` to `to` it becomes `look`. */
export interface AtmosphereChange<L> {
  readonly from: number;
  readonly to: number;
  readonly look: L;
}

/**
 * A level's look along its length (P08-R04): `start`, then each change in turn, blending every
 * number smoothly over its stretch. It follows the distance, so a jump along the level shows
 * the look of where it lands. `resolve` turns a look description into an atmosphere.
 */
export class AtmosphereTrack<L> {
  readonly #start: Atmosphere;
  readonly #changes: readonly {
    readonly from: number;
    readonly to: number;
    readonly end: Atmosphere;
  }[];

  constructor(start: L, changes: readonly AtmosphereChange<L>[], resolve: (look: L) => Atmosphere) {
    this.#start = resolve(start);
    this.#changes = [...changes]
      .sort((a, b) => a.from - b.from)
      .map((c) => {
        if (!(c.to >= c.from)) throw new RangeError('A look change must end after it starts');
        return { from: c.from, to: c.to, end: resolve(c.look) };
      });
  }

  /** The atmosphere at `distance` along the level. */
  at(distance: number): Atmosphere {
    let now = this.#start;
    for (const { from, to, end } of this.#changes) {
      if (distance <= from) break;
      const t = to > from ? Math.min(1, (distance - from) / (to - from)) : 1;
      now = blendAtmosphere(now, end, smooth(t));
    }
    return now;
  }
}

/** An eased 0..1 ramp that stays at one half halfway (smoothstep). */
function smooth(t: number): number {
  return t * t * (3 - 2 * t);
}
