import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { createPropMaterials, LIGHTS_Z_OFFSET } from '../../../../src/render/scenery/scenery-kit';
import { SAMPLE_SCENERY_LOOK } from '../../../fixtures/sample-scenery';

describe('prop lights (reviewer, 2026-10-28)', () => {
  it('are pulled towards the camera, so they do not flicker against the walls they lie on', () => {
    const scene = new Scene(new NullEngine());
    const { structure, lights } = createPropMaterials(scene, SAMPLE_SCENERY_LOOK);
    expect(LIGHTS_Z_OFFSET).toBeLessThan(0);
    expect(lights.zOffset).toBe(LIGHTS_Z_OFFSET);
    expect(structure.zOffset).toBe(0);
    scene.dispose();
  });
});
