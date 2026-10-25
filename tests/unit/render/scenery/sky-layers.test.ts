import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { SkyScript } from '../../../../src/core/scenery/sky-look';
import { WEATHER_KINDS } from '../../../../src/config/weather';
import { atmosphereTrack, lookAtmosphere } from '../../../../src/render/scenery/atmosphere-of';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import { SceneryStage } from '../../../../src/render/scenery/scenery-stage';
import type { SceneryLook } from '../../../../src/render/scenery/scenery-look';
import {
  SAMPLE_SCENERY,
  SAMPLE_SCENERY_LEVEL,
  SAMPLE_SCENERY_LOOK,
} from '../../../fixtures/sample-scenery';

const CONFIG = {
  chunkLength: 100,
  cell: 10,
  margin: 20,
  cloudClearance: 10,
  sunDistance: 500,
  farClip: 2000,
  propReach: [40, 120] as const,
  propStep: 40,
};

const snow = (strength: number) => ({ kind: 'snow', strength }) as const;

/** Dusk with light snow, turning to a snowy night between 5 and 15 s (100 and 300 units). */
const SCRIPT: SkyScript = {
  start: { timeOfDay: 'dusk', clouds: [0.3, 0.2], weather: snow(0.2) },
  changes: [
    {
      from: 5,
      to: 15,
      look: { timeOfDay: 'night', clouds: [0.1, 0.05], weather: snow(1), aurora: 1 },
    },
  ],
};

const LOOK: SceneryLook = { ...SAMPLE_SCENERY_LOOK, atmosphere: SCRIPT };

describe('Sky layers', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function stage(look: SceneryLook, atmosphere = {}): SceneryStage {
    scene = new Scene(new NullEngine());
    return new SceneryStage(scene, {
      screen: { width: 300, height: 400 },
      camera: SAMPLE_SCENERY.camera,
      level: SAMPLE_SCENERY_LEVEL,
      look,
      propModels: SAMPLE_SCENERY.propModels,
      kit: createPlainSceneryKit,
      config: CONFIG,
      atmosphere,
    });
  }

  it('P08-R04: a look without a time of day keeps its own sky, light and clouds', () => {
    const s = stage(SAMPLE_SCENERY_LOOK);
    s.update(150, 1 / 60);
    expect(s.atmosphere).toEqual(lookAtmosphere(SAMPLE_SCENERY_LOOK));
    expect(s.sun.intensity).toBe(SAMPLE_SCENERY_LOOK.sun.intensity);
    expect(s.clouds[0]?.coverage).toBe(SAMPLE_SCENERY_LOOK.clouds[0]?.coverage);
    expect(s.weatherParticles).toBe(0);
  });

  it('P08-R04: the look follows the distance: dusk, then halfway, then night with an aurora', () => {
    const s = stage(LOOK);
    const track = atmosphereTrack(LOOK, SAMPLE_SCENERY_LEVEL.scrollSpeed);
    s.update(0, 1 / 60);
    expect(s.atmosphere).toEqual(track.at(0));
    expect(s.clouds[0]?.coverage).toBeCloseTo(0.3);
    s.update(200, 1 / 60);
    expect(s.atmosphere.clouds[0]?.coverage).toBeCloseTo(0.2);
    expect(s.sun.intensity).toBeCloseTo(s.atmosphere.sun.intensity);
    // A jump far along gives the night at once, with its aurora and the clouds' cover.
    s.update(380, 1 / 60);
    expect(s.atmosphere).toEqual(track.at(380));
    expect(s.atmosphere.aurora).toBe(1);
    expect(s.clouds[0]?.coverage).toBeCloseTo(0.1);
    expect(scene?.getMeshByName('aurora')?.isEnabled()).toBe(true);
    expect(scene?.fogEnd).toBeCloseTo(s.atmosphere.fog.end);
  });

  it('P08-R05: as many snowflakes as the strength asks, none with the weather off', () => {
    const s = stage(LOOK);
    s.update(380, 1 / 60);
    expect(s.weatherParticles).toBe(WEATHER_KINDS.snow?.maxParticles);
    expect(scene?.getMeshByName('weather-snow')?.isEnabled()).toBe(true);
    const calm = stage(LOOK, { weather: false });
    calm.update(380, 1 / 60);
    expect(calm.weatherParticles).toBe(0);
    expect(calm.atmosphere.weather.strength).toBe(0);
  });

  it('P08-R12: look= forces a time of day, even on a look without one', () => {
    const forced = stage(LOOK, { timeOfDay: 'midday' });
    forced.update(380, 1 / 60);
    const midday = atmosphereTrack(LOOK, 20, { timeOfDay: 'midday' }).at(380);
    expect(forced.atmosphere.sun).toEqual(midday.sun);
    const plain = stage(SAMPLE_SCENERY_LOOK, { timeOfDay: 'night' });
    plain.update(0, 1 / 60);
    expect(plain.atmosphere.groundLights).toBeGreaterThan(1);
  });
});
