import { describe, expect, it } from 'vitest';
import { TIMES_OF_DAY } from '../../../../src/core/scenery/atmosphere';
import {
  atTimeOfDay,
  resolveSky,
  weatherFog,
  weatherParticles,
  withoutWeather,
} from '../../../../src/core/scenery/sky-look';
import { WEATHER_KINDS } from '../../../../src/config/weather';
import { at } from '../../../helpers/at';

const BASE = { fog: { start: 1000, end: 2600 }, cloudOpacity: [0.75, 0.5] };

describe('Sky looks', () => {
  it('P08-R04: each time of day has its own sun, sky and lights; at night a dim cold moon', () => {
    const skies = TIMES_OF_DAY.map((t) => resolveSky({ timeOfDay: t, clouds: [0, 0] }, BASE));
    expect(new Set(skies.map((s) => JSON.stringify(s.sun))).size).toBe(6);
    const [dawn, midday, dusk, night] = [at(skies, 0), at(skies, 2), at(skies, 4), at(skies, 5)];
    expect(dawn.sun.elevationDeg).toBeLessThan(15);
    expect(midday.sun.elevationDeg).toBeGreaterThan(45);
    expect(night.sun.intensity).toBeLessThan(midday.sun.intensity);
    // Cold moonlight: more blue than red.
    expect(night.sun.color[2]).toBeGreaterThan(night.sun.color[0]);
    // Ground lights off by day, on at dusk and at night.
    expect(midday.groundLights).toBeLessThan(0.3);
    expect(dusk.groundLights).toBeGreaterThan(1);
    expect(night.groundLights).toBeGreaterThan(1);
    // The ships still catch some light at night (readability).
    expect(night.sky.environmentIntensity).toBeGreaterThanOrEqual(0.5);
  });

  it('P08-R04: the cloud cover sets both layers; a heavy cover dims and softens the sun', () => {
    const clear = resolveSky({ timeOfDay: 'midday', clouds: [0.1, 0.1] }, BASE);
    const overcast = resolveSky({ timeOfDay: 'midday', clouds: [0.9, 0.8] }, BASE);
    expect(overcast.clouds.map((c) => c.coverage)).toEqual([0.9, 0.8]);
    expect(overcast.sun.intensity).toBeLessThan(clear.sun.intensity);
    expect(overcast.sun.shadowDarkness).toBeGreaterThan(clear.sun.shadowDarkness);
    expect(overcast.ambient.intensity).toBeGreaterThan(clear.ambient.intensity);
    // A storm turns the clouds dark grey; dawn clouds are pink-orange.
    const storm = resolveSky({ timeOfDay: 'midday', clouds: [0.9, 0.8], storm: 1 }, BASE);
    expect(storm.clouds[0]?.color[0]).toBeLessThan(0.5);
    const dawn = resolveSky({ timeOfDay: 'dawn', clouds: [0.3, 0.2] }, BASE);
    expect(dawn.clouds[0]?.color[0]).toBeGreaterThan(dawn.clouds[0]?.color[2] ?? 1);
  });

  it('P08-R05: snow brings the haze closer, to 55 % of its distance in a blizzard', () => {
    expect(weatherFog({ kind: 'snow', strength: 0 })).toBe(1);
    expect(weatherFog({ kind: 'snow', strength: 1 })).toBeCloseTo(0.55);
    const blizzard = resolveSky(
      { timeOfDay: 'afternoon', clouds: [0.9, 0.8], weather: { kind: 'snow', strength: 1 } },
      BASE,
    );
    expect(blizzard.fog.end).toBeCloseTo(2600 * 0.55);
    expect(weatherFog({ kind: 'acid rain', strength: 1 })).toBe(1);
  });

  it('P08-R05: no flake at strength 0, the most allowed at strength 1', () => {
    const max = WEATHER_KINDS.snow?.maxParticles ?? 0;
    expect(max).toBeLessThanOrEqual(1500);
    expect(weatherParticles({ kind: 'snow', strength: 0 })).toBe(0);
    expect(weatherParticles({ kind: 'snow', strength: 1 })).toBe(max);
    expect(weatherParticles({ kind: 'snow', strength: 0.5 })).toBe(Math.round(max / 2));
    expect(weatherParticles({ kind: 'snow', strength: 3 })).toBe(max);
    expect(weatherParticles({ kind: 'unknown', strength: 1 })).toBe(0);
  });

  it('P08-R12: a look at another time of day, and without its weather', () => {
    const look = {
      timeOfDay: 'dusk',
      clouds: [0.3, 0.2],
      weather: { kind: 'snow', strength: 0.4 },
    } as const;
    expect(atTimeOfDay(look, 'night').timeOfDay).toBe('night');
    expect(atTimeOfDay(look, undefined)).toBe(look);
    expect(withoutWeather(look).weather?.strength).toBe(0);
  });

  it('P09-R05: no rain streak at strength 0, the most allowed (rain_streaks_max) at strength 1', () => {
    const rain = WEATHER_KINDS.rain;
    expect(rain?.maxParticles).toBe(2000);
    expect(weatherParticles({ kind: 'rain', strength: 0 })).toBe(0);
    expect(weatherParticles({ kind: 'rain', strength: 1 })).toBe(2000);
    expect(weatherParticles({ kind: 'rain', strength: 0.4 })).toBe(800);
  });

  it('P09-R05: rain is thin streaks along their fall, much faster than snow, rings on the water', () => {
    const rain = WEATHER_KINDS.rain;
    expect(rain?.align).toBe('fall');
    expect(rain?.fall[0]).toBeGreaterThan(5 * (WEATHER_KINDS.snow?.fall[1] ?? Infinity));
    expect(rain?.size[1]).toBeLessThan(WEATHER_KINDS.snow?.size[0] ?? 0);
    expect(rain?.rings?.alpha).toBeLessThan(0.5);
  });

  it('P09-R05: rain brings the haze closer and greyer with its strength', () => {
    const look = { timeOfDay: 'midday', clouds: [0.5, 0.3] } as const;
    const dry = resolveSky(look, BASE);
    const wet = resolveSky({ ...look, weather: { kind: 'rain', strength: 1 } }, BASE);
    expect(wet.fog.end).toBeCloseTo(dry.fog.end * (WEATHER_KINDS.rain?.fogAt1 ?? 0));
    const saturation = (c: readonly number[]) => Math.max(...c) - Math.min(...c);
    expect(saturation(wet.sky.haze)).toBeLessThan(saturation(dry.sky.haze));
  });

  it('P09-R04: a mist brings the haze in and whitens it; a tint colours the ambient light', () => {
    const look = { timeOfDay: 'morning', clouds: [0.3, 0.2] } as const;
    const clear = resolveSky(look, BASE);
    const misty = resolveSky({ ...look, mist: { fog: 0.4, white: 0.8 } }, BASE);
    expect(misty.fog.end).toBeCloseTo(clear.fog.end * 0.4);
    expect(Math.min(...misty.sky.haze)).toBeGreaterThan(Math.min(...clear.sky.haze));
    const green = resolveSky({ ...look, tint: [0.9, 1.1, 0.9] }, BASE);
    expect(green.ambient.sky[1]).toBeCloseTo(clear.ambient.sky[1] * 1.1);
    expect(green.ambient.ground[0]).toBeCloseTo(clear.ambient.ground[0] * 0.9);
  });

  it('P09-R05, P09-R11: lightning is part of the look, and turned off with the weather', () => {
    const look = {
      timeOfDay: 'afternoon',
      clouds: [0.9, 0.9],
      weather: { kind: 'rain', strength: 0.8 },
      lightning: 1,
    } as const;
    expect(resolveSky(look, BASE).lightning).toBe(1);
    expect(resolveSky(withoutWeather(look), BASE)).toMatchObject({
      lightning: 0,
      weather: { strength: 0 },
    });
  });
});
