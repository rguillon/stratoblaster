import { AtmosphereTrack, type Atmosphere, type TimeOfDay } from '../../core/scenery/atmosphere';
import {
  atTimeOfDay,
  CLEAR,
  resolveSky,
  withoutWeather,
  type SkyLook,
  type SkyScript,
} from '../../core/scenery/sky-look';
import type { SceneryLook } from './scenery-look';

/** A level's atmosphere at each distance along it. */
export interface AtmosphereAlong {
  at(distance: number): Atmosphere;
}

/** Debug choices on a level's look (P08-R12). */
export interface AtmosphereOptions {
  /** `look=<time of day>`: every look of the level at this time of day. */
  readonly timeOfDay?: TimeOfDay | undefined;
  /** `weather=0`: no weather at all. */
  readonly weather?: boolean;
  /** Phase 15 (P15-R10), `tiles=1`: the grid of tiles drawn over the districts. */
  readonly tileGrid?: boolean;
}

/**
 * The fixed atmosphere of a look without a sky script (World 1): its own sky, fog,
 * sun, ambient light, clouds and lights, as they always were.
 */
export function lookAtmosphere(look: SceneryLook): Atmosphere {
  return {
    sun: {
      elevationDeg: look.sun.elevationDeg,
      azimuthDeg: look.sun.azimuthDeg,
      color: look.sun.color,
      intensity: look.sun.intensity,
      shadowDarkness: look.sun.shadow.darkness,
    },
    sky: {
      haze: look.sky.haze,
      stops: look.sky.stops,
      environmentIntensity: look.sky.environmentIntensity,
    },
    ambient: look.ambient,
    fog: look.fog,
    clouds: look.clouds.map((c) => ({
      coverage: c.coverage,
      opacity: c.opacity,
      color: c.color,
      shade: c.shade,
    })),
    groundLights: look.props.lightIntensity,
    weather: CLEAR,
    aurora: 0,
    lightning: 0,
  };
}

/** The sky script of `look`, or one made from its own clouds when a time of day is forced. */
function scriptOf(look: SceneryLook, timeOfDay: TimeOfDay | undefined): SkyScript | undefined {
  if (look.atmosphere) return look.atmosphere;
  if (!timeOfDay) return undefined;
  const [low, high] = look.clouds;
  return { start: { timeOfDay, clouds: [low?.coverage ?? 0, high?.coverage ?? 0] } };
}

/**
 * The atmosphere of a level along its length (P08-R04): its sky script's looks, their changes
 * turned from seconds into distances at `scrollSpeed`; or its fixed look.
 */
export function atmosphereTrack(
  look: SceneryLook,
  scrollSpeed: number,
  options: AtmosphereOptions = {},
): AtmosphereAlong {
  const script = scriptOf(look, options.timeOfDay);
  const tone = look.tone ?? 1;
  // A fixed look has no weather to turn off.
  if (!script) return new AtmosphereTrack(look, [], (l) => toned(lookAtmosphere(l), tone));
  const base = { fog: look.fog, cloudOpacity: look.clouds.map((c) => c.opacity) };
  const adjust = (sky: SkyLook): SkyLook => {
    const timed = atTimeOfDay(sky, options.timeOfDay);
    return options.weather === false ? withoutWeather(timed) : timed;
  };
  const changes = (script.changes ?? []).map((c) => ({
    from: c.from * scrollSpeed,
    to: c.to * scrollSpeed,
    look: adjust(c.look),
  }));
  return new AtmosphereTrack(adjust(script.start), changes, (sky) =>
    toned(resolveSky(sky, base), tone),
  );
}

/** `atmosphere` with its haze and clouds `tone` (0..1) as bright (`SceneryLook.tone`). */
export function toned(atmosphere: Atmosphere, tone: number): Atmosphere {
  if (tone === 1) return atmosphere;
  const dim = ([r, g, b]: readonly [number, number, number]) =>
    [r * tone, g * tone, b * tone] as const;
  return {
    ...atmosphere,
    sky: { ...atmosphere.sky, haze: dim(atmosphere.sky.haze) },
    clouds: atmosphere.clouds.map((c) => ({ ...c, color: dim(c.color), shade: dim(c.shade) })),
  };
}
