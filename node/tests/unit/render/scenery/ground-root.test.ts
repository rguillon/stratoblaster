import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { GroundRoot } from '../../../../src/render/scenery/ground-root';
import { createPlainSceneryKit } from '../../../../src/render/scenery/scenery-kit';
import { SceneryStage } from '../../../../src/render/scenery/scenery-stage';
import {
  SAMPLE_SCENERY,
  SAMPLE_SCENERY_LEVEL,
  SAMPLE_SCENERY_LOOK,
} from '../../../fixtures/sample-scenery';
import { SCENERY_STAGE_CONFIG } from '../../../../src/config/scenery-stage';

describe('ground drawn bigger, as if flying lower (reviewer, 2026-10-28)', () => {
  it('hangs what it makes from a node twice as big, the ground under the view still `distance` in', () => {
    const scene = new Scene(new NullEngine());
    const ground = new GroundRoot(scene, 2);
    const parented = CreateBox('kept', {}, scene);
    const box = ground.adopt(() => {
      const made = CreateBox('made', {}, scene);
      parented.parent = made;
      return made;
    });
    expect(box.parent).toBe(ground.node);
    expect(parented.parent).toBe(box);
    expect(ground.node.scaling.x).toBe(2);
    ground.moveTo(1000);
    // A view at world Z 1000 sees ground Z 1000; ground 10 further is drawn 20 further.
    expect(ground.toGround(1000)).toBe(1000);
    expect(ground.toWorld(1010)).toBe(1020);
    expect(ground.transform).toEqual({ scale: 2, offsetZ: -1000 });
    scene.dispose();
  });

  it('a stage with `groundScale` hangs its terrain, roads, props and sea from the ground, not its clouds', () => {
    const make = (groundScale: number) => {
      const scene = new Scene(new NullEngine());
      const stage = new SceneryStage(scene, {
        screen: { width: 300, height: 400 },
        camera: { ...SAMPLE_SCENERY.camera, groundScale },
        level: SAMPLE_SCENERY_LEVEL,
        look: SAMPLE_SCENERY_LOOK,
        propModels: SAMPLE_SCENERY.propModels,
        kit: createPlainSceneryKit,
        config: SCENERY_STAGE_CONFIG,
      });
      stage.update(500, 1 / 60);
      return { scene, stage };
    };
    const { scene, stage } = make(2);
    const root = scene.getTransformNodeByName('ground-root');
    const terrain = scene.meshes.filter((m) => m.name.startsWith('terrain-chunk'));
    expect(terrain.length).toBeGreaterThan(0);
    for (const mesh of terrain) expect(mesh.parent, mesh.name).toBe(root);
    for (const mesh of scene.meshes.filter((m) => m.name.startsWith('cloud-layer')))
      expect(mesh.parent, mesh.name).toBeNull();
    // Half as much ground in view, so fewer chunks than with the ground at its size.
    const plain = make(1);
    expect(stage.stats.chunks).toBeLessThanOrEqual(plain.stage.stats.chunks);
    scene.dispose();
    plain.scene.dispose();
  });
});
