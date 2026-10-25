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
});
