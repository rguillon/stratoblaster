import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Constants } from '@babylonjs/core/Engines/constants';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Scene } from '@babylonjs/core/scene';
import { addBackgroundVeil } from '../../../../src/render/scenery/background-veil';
import {
  ABOVE_CLOUDS_GROUP,
  BELOW_CLOUDS_GROUP,
} from '../../../../src/render/scenery/cloud-layers';

describe('addBackgroundVeil (P14-R01)', () => {
  it('P14-R01: hangs a see-through veil in front of the camera, over the clouds, under the playfield', () => {
    const scene = new Scene(new NullEngine());
    const camera = new FreeCamera('camera', Vector3.Zero(), scene);
    const veil = addBackgroundVeil(scene, camera, { color: [0.1, 0, 0.2], opacity: 0.4 });
    expect(veil.parent).toBe(camera);
    expect(veil.position.z).toBeGreaterThan(camera.minZ);
    expect(veil.renderingGroupId).toBe(BELOW_CLOUDS_GROUP + 1);
    expect(veil.renderingGroupId).toBeLessThan(ABOVE_CLOUDS_GROUP);
    const material = veil.material;
    expect(material?.alpha).toBe(0.4);
    expect(material?.depthFunction).toBe(Constants.ALWAYS);
    // Wider than what the camera sees at that distance.
    const extent = veil.getBoundingInfo().boundingBox.extendSize.x;
    expect(extent).toBeGreaterThan(veil.position.z * Math.tan(camera.fov / 2));
  });
});
