import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import { sunDirection } from '../../../../src/render/scenery/scenery-lighting';
import {
  SceneryStage,
  type SceneryStageOptions,
} from '../../../../src/render/scenery/scenery-stage';
import {
  SAMPLE_SCENERY,
  SAMPLE_SCENERY_LEVEL,
  SAMPLE_SCENERY_LOOK,
} from '../../../fixtures/sample-scenery';

const CONFIG = { chunkLength: 100, cell: 10, margin: 20, sunDistance: 500, farClip: 2000 };

function options(overrides: Partial<SceneryStageOptions> = {}): SceneryStageOptions {
  return {
    screen: { width: 300, height: 400 },
    camera: SAMPLE_SCENERY.camera,
    level: SAMPLE_SCENERY_LEVEL,
    look: SAMPLE_SCENERY_LOOK,
    propModels: SAMPLE_SCENERY.propModels,
    kit: createPlainSceneryKit,
    config: CONFIG,
    ...overrides,
  };
}

describe('SceneryStage', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function stage(overrides: Partial<SceneryStageOptions> = {}): SceneryStage {
    scene = new Scene(new NullEngine());
    return new SceneryStage(scene, options(overrides));
  }

  it('P04-R01, P04-R04: builds terrain chunks and props around the camera, and follows it', () => {
    const s = stage();
    s.update(0, 1 / 60);
    const { chunks, props, roads } = s.stats;
    expect(chunks).toBeGreaterThan(1);
    expect(props).toBeGreaterThan(0);
    // P04-R07: road ribbons on the chunks.
    expect(roads).toBeGreaterThan(0);
    expect(scene?.meshes.some((m) => m.name.startsWith('roads-'))).toBe(true);
    s.update(5000, 1 / 60);
    expect(s.camera.position.z).toBeGreaterThan(4000);
    const meshes =
      scene?.meshes.filter((m) => m.name.startsWith('terrain-chunk') && m.isEnabled()) ?? [];
    for (const mesh of meshes) {
      expect(mesh.getBoundingInfo().boundingBox.maximumWorld.z).toBeGreaterThan(4000);
    }
  });

  it('P04-R05: the camera flies above the flight plane, behind the playfield, tilted forward', () => {
    const s = stage();
    s.update(1000, 0);
    const flight = SAMPLE_SCENERY.camera.flightAltitude;
    expect(s.camera.position.y).toBeCloseTo(flight + s.framing.height);
    expect(s.camera.position.z).toBeCloseTo(1000 + s.framing.back);
    expect(s.camera.fov).toBeCloseTo((SAMPLE_SCENERY.camera.fovDeg * Math.PI) / 180);
    expect(s.playfieldPoint(150, 80, 1000).asArray()).toEqual([0, flight, 1080]);
  });

  it('P04-R02: the sea follows the camera at the sea level, and can be hidden', () => {
    const s = stage();
    s.update(300, 0);
    const sea = scene?.getMeshByName('sea');
    expect(sea?.position.y).toBe(0);
    expect(sea?.position.z).toBeGreaterThan(300);
    expect(s.hasSea && s.seaEnabled).toBe(true);
    s.setSeaEnabled(false);
    expect(sea?.isEnabled()).toBe(false);
    const { sea: wet, ...dryLevel } = SAMPLE_SCENERY_LEVEL;
    expect(wet).toBeDefined();
    const dry = stage({ level: dryLevel });
    expect(dry.hasSea).toBe(false);
    dry.setSeaEnabled(true);
    expect(dry.seaEnabled).toBe(false);
  });

  it('P04-R03: each cloud layer sits at its altitude and hides when off or empty', () => {
    const s = stage();
    s.update(0, 0);
    const layer = scene?.getMeshByName('cloud-layer-0');
    expect(layer?.position.y).toBe(SAMPLE_SCENERY_LOOK.clouds[0]?.altitude);
    expect(layer?.isEnabled()).toBe(true);
    const state = s.clouds[0];
    if (!state) throw new Error('no cloud layer');
    state.coverage = 0;
    s.update(0, 0);
    expect(layer?.isEnabled()).toBe(false);
    state.coverage = 0.5;
    state.enabled = false;
    s.update(0, 0);
    expect(layer?.isEnabled()).toBe(false);
  });

  it('P04-R01: a new seed rebuilds the ground and the props', () => {
    const s = stage();
    s.update(0, 0);
    const before = s.field.height(5, 5);
    s.setSeed(123);
    expect(s.seed).toBe(123);
    expect(s.field.height(5, 5)).not.toBe(before);
    s.update(0, 0);
    expect(s.stats.props).toBeGreaterThan(0);
  });

  it('refuses a level whose props have no model', () => {
    expect(() => stage({ propModels: {} })).toThrow(/block/);
  });

  it('the sun shines from its elevation and azimuth', () => {
    const ahead = sunDirection(30, 0);
    expect(ahead.y).toBeCloseTo(-0.5);
    expect(ahead.z).toBeLessThan(0);
    expect(sunDirection(0, 90).x).toBeCloseTo(-1);
  });
});
