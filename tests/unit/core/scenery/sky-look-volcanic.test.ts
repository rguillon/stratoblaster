import { describe, expect, it } from 'vitest';
import { WEATHER_KINDS } from '../../../../src/config/weather';
import { blendAtmosphere } from '../../../../src/core/scenery/atmosphere';
import {
  resolveSky,
  weatherFog,
  weatherParticles,
  withoutWeather,
  type SkyLook,
} from '../../../../src/core/scenery/sky-look';

const BASE = { fog: { start: 1000, end: 2600 }, cloudOpacity: [0.75, 0.5] };
const ash = (strength: number) => ({ kind: 'ash', strength });
const embers = (strength: number) => ({ kind: 'embers', strength });
const NIGHT: SkyLook = { timeOfDay: 'night', clouds: [0.6, 0.5] };

describe('Sky looks: falling ash, embers and fire light (phase 10)', () => {
  it('P10-R06: no ash or ember at strength 0, the most allowed at strength 1', () => {
    expect(WEATHER_KINDS.ash?.maxParticles).toBe(1500);
    expect(WEATHER_KINDS.embers?.maxParticles).toBeLessThanOrEqual(800);
    for (const kind of ['ash', 'embers']) {
      expect(weatherParticles({ kind, strength: 0 })).toBe(0);
      expect(weatherParticles({ kind, strength: 1 })).toBe(WEATHER_KINDS[kind]?.maxParticles);
    }
  });

  it('P10-R06: ash falls slowly like a dull snow; embers rise, glow and flicker, never fall', () => {
    const [a, e] = [WEATHER_KINDS.ash, WEATHER_KINDS.embers];
    if (!a || !e) throw new Error('missing kinds');
    expect(a.fall[1]).toBeLessThan(WEATHER_KINDS.snow?.fall[1] ?? 0);
    expect(a.fall[0]).toBeGreaterThan(0);
    expect(a.blend).toBeUndefined();
    // Up the screen: a negative fall, at every speed.
    expect(e.fall[0]).toBeLessThan(0);
    expect(e.fall[1]).toBeLessThan(0);
    expect(e.blend).toBe('add');
    expect(e.flicker?.amount).toBeGreaterThan(0);
    expect(e.fadeHigh).toBeGreaterThan(0);
    // No streak: a small round spark, no outline.
    expect(e.streak).toBe(0);
  });

  it('P10-R06: ash brings the haze closer and turns it brown-grey with its strength', () => {
    expect(weatherFog(ash(1))).toBeLessThan(weatherFog(ash(0.5)));
    const clear = resolveSky({ timeOfDay: 'midday', clouds: [0.9, 0.9] }, BASE);
    const ashen = resolveSky({ timeOfDay: 'midday', clouds: [0.9, 0.9], weather: ash(1) }, BASE);
    expect(ashen.fog.end).toBeLessThan(clear.fog.end);
    // Browner: less blue than red.
    expect(ashen.sky.haze[2]).toBeLessThan(ashen.sky.haze[0]);
  });

  it('P10-R06: a second weather falls at the same time, its fog adding to the first', () => {
    const both = resolveSky({ ...NIGHT, weather: ash(0.3), secondWeather: embers(0.3) }, BASE);
    const one = resolveSky({ ...NIGHT, weather: ash(0.3) }, BASE);
    expect(both.weather).toEqual(ash(0.3));
    expect(both.secondWeather).toEqual(embers(0.3));
    expect(both.fog.end).toBeLessThanOrEqual(one.fog.end);
    expect(one.secondWeather).toBeUndefined();
    // weather=0 removes both.
    const calm = withoutWeather({ ...NIGHT, weather: ash(0.3), secondWeather: embers(0.3) });
    expect(calm.weather?.strength).toBe(0);
    expect(calm.secondWeather?.strength).toBe(0);
    expect(withoutWeather(NIGHT).secondWeather).toBeUndefined();
  });

  it('P10-R06: the second weather blends along the level, from none to some', () => {
    const a = resolveSky({ ...NIGHT, weather: embers(0.6) }, BASE);
    const b = resolveSky({ ...NIGHT, weather: embers(0.6), secondWeather: ash(1) }, BASE);
    expect(blendAtmosphere(a, b, 0.5).secondWeather).toEqual(ash(0.5));
    expect(blendAtmosphere(a, a, 0.5).secondWeather).toBeUndefined();
  });

  it('P10-R04: fire below lights the clouds, the haze and the ground light; a tint colours the clouds', () => {
    const plain = resolveSky({ ...NIGHT, storm: 0.6 }, BASE);
    const glow = { color: [1, 0.4, 0.1] as const, strength: 1 };
    const lit = resolveSky({ ...NIGHT, storm: 0.6, underglow: glow }, BASE);
    const red = (c: readonly number[] | undefined) => (c?.[0] ?? 0) - (c?.[2] ?? 0);
    expect(red(lit.clouds[0]?.shade)).toBeGreaterThan(red(plain.clouds[0]?.shade));
    expect(red(lit.clouds[0]?.color)).toBeGreaterThan(red(plain.clouds[0]?.color));
    expect(red(lit.sky.haze)).toBeGreaterThan(red(plain.sky.haze));
    expect(red(lit.ambient.ground)).toBeGreaterThan(red(plain.ambient.ground));
    // The sun and the fog stay the time of day's.
    expect(lit.sun).toEqual(plain.sun);
    expect(lit.fog).toEqual(plain.fog);
    const brown = resolveSky({ ...NIGHT, cloudTint: [0.8, 0.7, 0.6] }, BASE);
    const grey = resolveSky(NIGHT, BASE);
    expect(brown.clouds[0]?.color[2]).toBeCloseTo((grey.clouds[0]?.color[2] ?? 0) * 0.6);
  });
});
