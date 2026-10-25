import { describe, expect, it } from 'vitest';
import {
  AtmosphereTrack,
  blendAtmosphere,
  isTimeOfDay,
  type Atmosphere,
} from '../../../../src/core/scenery/atmosphere';

const A: Atmosphere = {
  sun: { elevationDeg: 10, azimuthDeg: 350, color: [1, 0.5, 0], intensity: 1, shadowDarkness: 0.2 },
  sky: {
    haze: [0, 0, 0],
    stops: [
      { at: -1, color: [0, 0, 0] },
      { at: 1, color: [0.2, 0.2, 0.2] },
    ],
    environmentIntensity: 0.4,
  },
  ambient: { sky: [0, 0, 0], ground: [0, 0, 0], intensity: 0.2 },
  fog: { start: 1000, end: 2000 },
  clouds: [{ coverage: 0, opacity: 0.5, color: [1, 1, 1], shade: [0.5, 0.5, 0.5] }],
  groundLights: 0,
  weather: { kind: 'snow', strength: 0 },
  aurora: 0,
};

const B: Atmosphere = {
  sun: { elevationDeg: 50, azimuthDeg: 30, color: [0, 0.5, 1], intensity: 2, shadowDarkness: 0.8 },
  sky: {
    haze: [1, 1, 1],
    stops: [
      { at: -1, color: [1, 1, 1] },
      { at: 1, color: [0.6, 0.6, 0.6] },
    ],
    environmentIntensity: 0.8,
  },
  ambient: { sky: [1, 1, 1], ground: [1, 1, 1], intensity: 0.6 },
  fog: { start: 500, end: 1000 },
  clouds: [{ coverage: 1, opacity: 0.3, color: [0, 0, 0], shade: [0, 0, 0] }],
  groundLights: 2,
  weather: { kind: 'snow', strength: 1 },
  aurora: 1,
};

describe('Atmosphere', () => {
  it('P08-R04: halfway between two looks, every number is halfway', () => {
    const half = blendAtmosphere(A, B, 0.5);
    expect(half.sun.elevationDeg).toBeCloseTo(30);
    // The sun turns the short way round, through north.
    expect(half.sun.azimuthDeg).toBeCloseTo(370);
    expect(half.sun.color).toEqual([0.5, 0.5, 0.5]);
    expect(half.sun.intensity).toBeCloseTo(1.5);
    expect(half.sky.haze).toEqual([0.5, 0.5, 0.5]);
    expect(half.sky.stops.map((s) => s.color[0])).toEqual([0.5, 0.4]);
    expect(half.ambient.intensity).toBeCloseTo(0.4);
    expect(half.fog).toEqual({ start: 750, end: 1500 });
    expect(half.clouds[0]?.coverage).toBeCloseTo(0.5);
    expect(half.groundLights).toBeCloseTo(1);
    expect(half.weather).toEqual({ kind: 'snow', strength: 0.5 });
    expect(half.aurora).toBeCloseTo(0.5);
    expect(blendAtmosphere(A, B, 0)).toBe(A);
    expect(blendAtmosphere(A, B, 1)).toBe(B);
  });

  it('P08-R04: a look change from A to B between d1 and d2: A at d1, B at d2, halfway in between', () => {
    const looks: Record<string, Atmosphere> = { a: A, b: B };
    const track = new AtmosphereTrack('a', [{ from: 1000, to: 2000, look: 'b' }], (l) => {
      const look = looks[l];
      if (!look) throw new Error(l);
      return look;
    });
    expect(track.at(0)).toBe(A);
    expect(track.at(1000)).toBe(A);
    expect(track.at(2000)).toBe(B);
    expect(track.at(5000)).toBe(B);
    expect(track.at(1500).sun.intensity).toBeCloseTo(1.5);
    expect(track.at(1500).weather.strength).toBeCloseTo(0.5);
    // Following the distance: going back gives the earlier look again (a debug jump).
    expect(track.at(1200).sun.intensity).toBeLessThan(track.at(1800).sun.intensity);
  });

  it('P08-R04: changes follow one another, each from where the one before left it', () => {
    const track = new AtmosphereTrack(
      0,
      [
        { from: 200, to: 300, look: 0 },
        { from: 0, to: 100, look: 1 },
      ],
      (k) => (k === 1 ? B : A),
    );
    expect(track.at(150)).toBe(B);
    expect(track.at(300)).toBe(A);
    expect(() => new AtmosphereTrack(0, [{ from: 10, to: 5, look: 0 }], () => A)).toThrow();
  });

  it('P08-R04: the six times of day', () => {
    for (const t of ['dawn', 'morning', 'midday', 'afternoon', 'dusk', 'night'])
      expect(isTimeOfDay(t)).toBe(true);
    expect(isTimeOfDay('noon')).toBe(false);
  });
});
