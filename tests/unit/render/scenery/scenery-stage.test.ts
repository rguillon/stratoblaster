import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import {
  snappedLightPosition,
  sunDirection,
} from '../../../../src/render/scenery/scenery-lighting';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import {
  SceneryStage,
  type SceneryStageOptions,
} from '../../../../src/render/scenery/scenery-stage';
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
    const roadMeshes = scene?.meshes.filter((m) => m.name.startsWith('roads-')) ?? [];
    const pathMeshes = scene?.meshes.filter((m) => m.name.startsWith('paths-')) ?? [];
    expect(roadMeshes.length).toBeGreaterThan(0);
    expect(pathMeshes.length).toBeGreaterThan(0);
    // P04 review: paths are drawn first, so the roads stay on top where they meet.
    for (const path of pathMeshes) {
      for (const road of roadMeshes) expect(path.alphaIndex).toBeLessThan(road.alphaIndex);
    }
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

  it('P04-R03 (review): a cloud layer below the highest ground is lifted above it', () => {
    const [cloud] = SAMPLE_SCENERY_LOOK.clouds;
    if (!cloud) throw new Error('no cloud layer');
    const low = { ...cloud, altitude: 5 };
    const s = stage({ look: { ...SAMPLE_SCENERY_LOOK, clouds: [low] } });
    const ceiling = s.field.ceiling;
    expect(s.cloudAltitude(low)).toBe(ceiling + CONFIG.cloudClearance);
    expect(scene?.getMeshByName('cloud-layer-0')?.position.y).toBe(ceiling + CONFIG.cloudClearance);
    expect(s.cloudAltitude({ ...cloud, altitude: 500 })).toBe(500);
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

  it('P04 review: the sun moves by whole shadow texels, so shadows do not shimmer', () => {
    const direction = sunDirection(40, 25);
    const texel = 0.8;
    const at = (z: number) => snappedLightPosition(direction, new Vector3(0, 0, z), 1000, texel);
    // Seen across the light, two positions differ by a whole number of texels.
    const forward = direction.normalizeToNew();
    const right = Vector3.Cross(Vector3.Up(), forward).normalize();
    const up = Vector3.Cross(forward, right);
    for (const z of [3.7, 120.2, 999.9]) {
      const delta = at(z).subtract(at(0));
      for (const axis of [right, up]) {
        const texels = Vector3.Dot(delta, axis) / texel;
        expect(Math.abs(texels - Math.round(texels))).toBeLessThan(1e-6);
      }
    }
    // And the light stays `distance` behind (about) the target.
    expect(Vector3.Distance(at(500), new Vector3(0, 0, 500))).toBeGreaterThan(995);
  });

  it('the sun shines from its elevation and azimuth', () => {
    const ahead = sunDirection(30, 0);
    expect(ahead.y).toBeCloseTo(-0.5);
    expect(ahead.z).toBeLessThan(0);
    expect(sunDirection(0, 90).x).toBeCloseTo(-1);
  });
});
