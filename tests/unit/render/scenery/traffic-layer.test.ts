import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { Road } from '../../../../src/core/scenery/road-network';
import { TrafficLayer } from '../../../../src/render/scenery/traffic-layer';
import { SAMPLE_SCENERY } from '../../../fixtures/sample-scenery';

const RULES = {
  kinds: ['block'],
  density: 1,
  lift: 0,
  scale: 1,
  length: 4,
  speed: [10, 20] as const,
};

/** A street along Z from 0 to 400, points every 8. */
const STREET: Road = {
  index: 0,
  kind: 'street',
  width: 6,
  lanes: 1,
  points: Array.from({ length: 51 }, (_, i) => ({ x: 0, z: i * 8, width: 6 })),
};

describe('TrafficLayer', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  it('draws the cars always, without fitting bounds to them every frame (reviewer, 2026-10-28)', () => {
    scene = new Scene(new NullEngine());
    const materials = {
      structure: new StandardMaterial('s', scene),
      lights: new StandardMaterial('l', scene),
    };
    const layer = new TrafficLayer(scene, SAMPLE_SCENERY.propModels, materials, RULES);
    const area = { xMin: -100, xMax: 100, zMin: 0, zMax: 400 };
    layer.update(1, area, { roads: [STREET], height: () => 0, seed: 1 });
    expect(layer.count).toBeGreaterThan(10);
    const meshes = [...layer.structureMeshes, ...layer.lightMeshes];
    expect(meshes.map((m) => m.name).sort()).toEqual(['prop-block', 'prop-block-lights']);
    for (const mesh of meshes) {
      expect(mesh.alwaysSelectAsActiveMesh).toBe(true);
      // The box of one car: not fitted to the cars along the street.
      expect(mesh.getBoundingInfo().boundingBox.maximum.z).toBeLessThan(10);
    }
  });
});
