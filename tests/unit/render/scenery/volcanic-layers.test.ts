import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { PLUME_KINDS } from '../../../../src/config/plumes';
import { WEATHER_KINDS } from '../../../../src/config/weather';
import type { SkyScript } from '../../../../src/core/scenery/sky-look';
import { SolidBuilder } from '../../../../src/render/geometry/solids';
import { lookAtmosphere } from '../../../../src/render/scenery/atmosphere-of';
import {
  plumeGeometry,
  plumeLight,
  type PlumeMaterialFactory,
} from '../../../../src/render/scenery/plume-layer';
import { PropField } from '../../../../src/render/scenery/prop-field';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import { SceneryStage } from '../../../../src/render/scenery/scenery-stage';
import type { LavaLook, SceneryLook } from '../../../../src/render/scenery/scenery-look';
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

const LAVA: LavaLook = {
  crust: [0.08, 0.03, 0.02],
  plate: [0.2, 0.07, 0.04],
  glow: [1, 0.35, 0.05],
  hot: [1, 0.85, 0.45],
  cell: 26,
  crack: 0.12,
  churn: 0.05,
  intensity: 1.3,
  edge: { color: [1, 0.4, 0.08], width: 1.6, cracks: 6 },
};

/** A night of falling ash and embers together (P10-R06). */
const FORGE_NIGHT: SkyScript = {
  start: {
    timeOfDay: 'night',
    clouds: [0.6, 0.5],
    weather: { kind: 'ash', strength: 0.3 },
    secondWeather: { kind: 'embers', strength: 1 },
  },
};

/** A vent smoking from two chimneys and steaming from one (phase 10). */
const VENT = () => ({
  structure: new SolidBuilder().box([4, 4, 4], [0.2, 0.2, 0.2]).geometry,
  plumes: [
    { at: [0, 4, 0] as const, kind: 'smoke' },
    { at: [1, 4, 0] as const, kind: 'smoke', scale: 0.5 },
    { at: [0, 2, 1] as const, kind: 'steam' },
  ],
});

describe('World 4 engine layers', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
    scene = undefined;
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

  it('P10-R06: ash and embers fall together, each as many as its strength asks; none with weather=0', () => {
    const s = stage({ ...SAMPLE_SCENERY_LOOK, atmosphere: FORGE_NIGHT });
    s.update(50, 1 / 60);
    const ash = Math.round((WEATHER_KINDS.ash?.maxParticles ?? 0) * 0.3);
    expect(s.weatherParticles).toBe(ash + (WEATHER_KINDS.embers?.maxParticles ?? 0));
    expect(scene?.getMeshByName('weather-ash')?.isEnabled()).toBe(true);
    expect(scene?.getMeshByName('weather-embers')?.isEnabled()).toBe(true);
    const calm = stage({ ...SAMPLE_SCENERY_LOOK, atmosphere: FORGE_NIGHT }, { weather: false });
    calm.update(50, 1 / 60);
    expect(calm.weatherParticles).toBe(0);
    expect(calm.atmosphere.secondWeather?.strength).toBe(0);
  });

  it('P10-R05: a lava look makes the liquid lava: opaque, self-lit, drawn in the glow with the terrain', () => {
    const water = stage(SAMPLE_SCENERY_LOOK);
    expect(water.lava).toBeUndefined();
    const s = stage({ ...SAMPLE_SCENERY_LOOK, sea: { ...SAMPLE_SCENERY_LOOK.sea, lava: LAVA } });
    s.update(50, 1 / 60);
    const lava = s.lava;
    expect(lava?.name).toBe('sea');
    const material = lava?.material;
    expect(material).toBeInstanceOf(StandardMaterial);
    if (!(material instanceof StandardMaterial)) return;
    expect(material.alpha).toBe(1);
    expect(material.emissiveColor.asArray()).toEqual([...LAVA.glow]);
    // Every terrain chunk, now and later, for a glow layer to hide the lava under the hills.
    const seen: Mesh[] = [];
    s.watchTerrain((mesh) => seen.push(mesh));
    expect(seen.length).toBe(s.stats.chunks);
    expect(seen.length).toBeGreaterThan(0);
    s.update(400, 1 / 60);
    expect(seen.length).toBeGreaterThanOrEqual(s.stats.chunks);
  });

  it('P10-R08: a prop’s plumes are drawn with its own instances, one mesh per plume kind', () => {
    scene = new Scene(new NullEngine());
    const materials = {
      structure: new StandardMaterial('s', scene),
      lights: new StandardMaterial('l', scene),
    };
    const kit = createPlainSceneryKit(scene, {
      look: SAMPLE_SCENERY_LOOK,
      sun: undefined as never,
      seaLevel: 0,
      seaSize: { width: 10, length: 10 },
      seed: 1,
    });
    let made = 0;
    const counting: PlumeMaterialFactory = (sc, kind) => {
      made++;
      return kit.plume(sc, kind);
    };
    const field = new PropField(scene, { vent: VENT }, materials, undefined, counting);
    field.setChunk(0, [
      { kind: 'vent', x: 0, y: 0, z: 5, rotation: 0, scale: 1 },
      { kind: 'vent', x: 9, y: 0, z: 5, rotation: 0, scale: 1 },
    ]);
    field.sync();
    const smoke = scene.getMeshByName('prop-vent-plume-smoke') as Mesh | null;
    const steam = scene.getMeshByName('prop-vent-plume-steam') as Mesh | null;
    expect(smoke?.thinInstanceCount).toBe(2);
    expect(steam?.thinInstanceCount).toBe(2);
    expect(field.plumeCount).toBe(2);
    expect(made).toBe(2);
    // Two smoke columns of `puffs` quads each.
    expect(smoke?.getTotalIndices()).toBe(2 * (PLUME_KINDS.smoke?.puffs ?? 0) * 6);
    expect(() => {
      field.updatePlumes({
        time: 1,
        cameraPosition: smoke?.position ?? (undefined as never),
        right: smoke?.position ?? (undefined as never),
        up: smoke?.position ?? (undefined as never),
        light: [1, 1, 1],
        fog: { color: [0, 0, 0], start: 0, end: 1 },
      });
    }).not.toThrow();
  });

  it('P10-R08: plume puffs spread evenly up each column, out of step from one column to the next', () => {
    const kind = PLUME_KINDS.steam;
    if (!kind) throw new Error('steam');
    const geo = plumeGeometry(
      [
        { at: [1, 2, 3], kind: 'steam' },
        { at: [0, 0, 0], kind: 'steam', scale: 2 },
      ],
      kind,
    );
    expect(geo.positions.length / 3).toBe(2 * kind.puffs * 4);
    const phases = (column: number) =>
      Array.from({ length: kind.puffs }, (_, i) => geo.puffs[(column * kind.puffs + i) * 16 + 3]);
    expect(phases(0)[1]).toBeCloseTo(1 / kind.puffs);
    expect(phases(1)[0]).not.toBe(phases(0)[0]);
    expect(geo.puffs.slice(0, 3)).toEqual([1, 2, 3]);
    expect(geo.scales.at(-1)).toBe(2);
  });

  it('P10-R08: plumes are lit by the scene: dim at night, bright by day', () => {
    const day = plumeLight(lookAtmosphere(SAMPLE_SCENERY_LOOK));
    expect(Math.max(...day)).toBeGreaterThan(0.3);
    expect(Math.max(...day)).toBeLessThanOrEqual(1.2);
  });
});
