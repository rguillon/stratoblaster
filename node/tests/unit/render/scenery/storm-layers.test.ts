import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { LIGHTNING, WEATHER_KINDS } from '../../../../src/config/weather';
import { LightningSchedule } from '../../../../src/core/scenery/lightning';
import type { SkyScript } from '../../../../src/core/scenery/sky-look';
import { boltLines } from '../../../../src/render/scenery/lightning-layer';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import type { SceneryLook } from '../../../../src/render/scenery/scenery-look';
import { SceneryStage } from '../../../../src/render/scenery/scenery-stage';
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

const rain = (strength: number) => ({ kind: 'rain', strength }) as const;

/** A thunderstorm all along: heavy rain with lightning. */
const STORM: SkyScript = {
  start: {
    timeOfDay: 'afternoon',
    clouds: [0.9, 0.9],
    storm: 1,
    weather: rain(1),
    lightning: 1,
  },
};

const look = (atmosphere: SkyScript): SceneryLook => ({ ...SAMPLE_SCENERY_LOOK, atmosphere });

describe('Rain and lightning (P09-R05)', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function stage(sky: SkyScript, atmosphere = {}): SceneryStage {
    scene = new Scene(new NullEngine());
    return new SceneryStage(scene, {
      screen: { width: 300, height: 400 },
      camera: SAMPLE_SCENERY.camera,
      level: SAMPLE_SCENERY_LEVEL,
      look: look(sky),
      propModels: SAMPLE_SCENERY.propModels,
      kit: createPlainSceneryKit,
      config: CONFIG,
      atmosphere,
    });
  }

  /** Runs `s` from its start up to `time` seconds, in frames of 1/60 s. */
  function runTo(s: SceneryStage, time: number, from = 0): void {
    for (let t = from; t < time; t += 1 / 60)
      s.update(t * SAMPLE_SCENERY_LEVEL.scrollSpeed, 1 / 60);
  }

  it('P09-R05: no streak at strength 0, the most allowed at strength 1; rings on the water', () => {
    const heavy = stage(STORM);
    heavy.update(0, 1 / 60);
    expect(heavy.weatherParticles).toBe(WEATHER_KINDS.rain?.maxParticles);
    expect(scene?.getMeshByName('weather-rain')?.isEnabled()).toBe(true);
    expect(heavy.rainRings).toBe(1);
    expect(scene?.getMeshByName('rain-rings')?.isEnabled()).toBe(true);
    // The rings show only where there is water to see.
    heavy.setSeaEnabled(false);
    heavy.update(0, 1 / 60);
    expect(heavy.rainRings).toBe(0);
    const none = stage({ start: { timeOfDay: 'midday', clouds: [0.5, 0.3], weather: rain(0) } });
    none.update(0, 1 / 60);
    expect(none.weatherParticles).toBe(0);
    expect(none.rainRings).toBe(0);
    // Snow makes no rings.
    const snow = stage({
      start: { timeOfDay: 'midday', clouds: [0.5, 0.3], weather: { kind: 'snow', strength: 1 } },
    });
    snow.update(0, 1 / 60);
    expect(snow.rainRings).toBe(0);
  });

  it('P09-R05: a flash lights the scene at the times of the level’s strikes, a bolt in the clouds', () => {
    const s = stage(STORM);
    const schedule = new LightningSchedule(SAMPLE_SCENERY_LEVEL.seed);
    const withBolt = schedule.strikesBefore(120).find((strike) => strike.bolt);
    const start = withBolt?.flashes[0];
    if (start === undefined) throw new Error('no bolt in two minutes');
    runTo(s, start - 0.05);
    expect(s.lightningFlash).toBe(0);
    const ambient = scene?.getLightByName('scenery-ambient') as HemisphericLight;
    const calm = ambient.intensity;
    runTo(s, start + LIGHTNING.rise, start - 0.05);
    expect(s.lightningFlash).toBeGreaterThan(0.5);
    expect(ambient.intensity).toBeGreaterThan(calm);
    expect(ambient.intensity).toBeLessThanOrEqual(calm * LIGHTNING.brightness + 1e-9);
    expect(scene?.getMeshByName('lightning-bolt')?.isEnabled()).toBe(true);
    runTo(s, start + 0.6, start + LIGHTNING.rise);
    expect(s.lightningFlash).toBe(0);
    expect(scene?.getMeshByName('lightning-bolt')?.isEnabled()).toBe(false);
    expect(ambient.intensity).toBeCloseTo(calm);
  });

  it('P09-R11: with the weather off, no rain, no rings and no flash', () => {
    const s = stage(STORM, { weather: false });
    runTo(s, 30);
    expect(s.weatherParticles).toBe(0);
    expect(s.rainRings).toBe(0);
    expect(s.atmosphere.lightning).toBe(0);
    expect(s.lightningFlash).toBe(0);
  });

  it('P09-R05: a bolt is a jagged line with forks, drawn the same for the same strike', () => {
    const lines = boltLines(42, 400);
    expect(lines).toHaveLength(3);
    expect(lines[0]?.length).toBe(13);
    expect(boltLines(42, 400)).toEqual(lines);
    expect(boltLines(43, 400)).not.toEqual(lines);
  });
});
