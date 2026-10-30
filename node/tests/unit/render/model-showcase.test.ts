import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { ModelShowcase } from '../../../src/render/model-showcase';
import { addModelAnimation } from '../../../src/render/model-animation';

function setup(count: number): { scene: Scene; showcase: ModelShowcase } {
  const scene = new Scene(new NullEngine());
  const factories = Array.from(
    { length: count },
    (_, i) => (s: Scene) => new TransformNode(`model-${String(i)}`, s),
  );
  const showcase = new ModelShowcase(scene, factories, { spacing: 4, rotationSpeedRadPerSec: 2 });
  return { scene, showcase };
}

describe('ModelShowcase', () => {
  it('lays models out side by side, centred on the origin', () => {
    const { scene, showcase } = setup(3);
    expect(showcase.pivots.map((p) => p.position.x)).toEqual([-4, 0, 4]);
    expect(showcase.pivots.map((p) => p.getChildren()[0]?.name)).toEqual([
      'model-0',
      'model-1',
      'model-2',
    ]);
    expect(showcase.width).toBe(12);
    scene.dispose();
  });

  it('rotates every model around the vertical axis at the configured speed', () => {
    const { scene, showcase } = setup(2);
    showcase.update(0.25);
    showcase.update(0.25);
    for (const pivot of showcase.pivots) expect(pivot.rotation.y).toBeCloseTo(1);
    scene.dispose();
  });

  it('steps the animations of every model with the rotation', () => {
    const scene = new Scene(new NullEngine());
    const steps: string[] = [];
    const factories = ['a', 'b'].map((name) => (s: Scene) => {
      const model = new TransformNode(name, s);
      addModelAnimation(model, (dt) => steps.push(`${name} ${String(dt)}`));
      return model;
    });
    const showcase = new ModelShowcase(scene, factories, { spacing: 4, rotationSpeedRadPerSec: 1 });
    showcase.update(0.1);
    expect(steps).toEqual(['a 0.1', 'b 0.1']);
    scene.dispose();
  });

  it('disposes its nodes', () => {
    const { scene, showcase } = setup(1);
    showcase.dispose();
    expect(scene.transformNodes).toHaveLength(0);
    scene.dispose();
  });
});
