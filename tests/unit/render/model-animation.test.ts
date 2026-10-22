import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { addModelAnimation, stepModelAnimations } from '../../../src/render/model-animation';

describe('model animations', () => {
  it('steps the animations of a node and of all its descendants', () => {
    const scene = new Scene(new NullEngine());
    const root = new TransformNode('root', scene);
    const child = new TransformNode('child', scene);
    child.parent = root;
    const grandChild = new TransformNode('grand-child', scene);
    grandChild.parent = child;
    const steps: string[] = [];
    addModelAnimation(root, (dt) => steps.push(`root ${String(dt)}`));
    addModelAnimation(grandChild, (dt) => steps.push(`grand-child ${String(dt)}`));
    addModelAnimation(grandChild, () => steps.push('grand-child again'));

    stepModelAnimations(root, 0.5);
    expect(steps).toEqual(['root 0.5', 'grand-child 0.5', 'grand-child again']);

    steps.length = 0;
    stepModelAnimations(child, 0.25);
    expect(steps).toEqual(['grand-child 0.25', 'grand-child again']);
    scene.dispose();
  });

  it('ignores animations of nodes outside the stepped model', () => {
    const scene = new Scene(new NullEngine());
    const steps: number[] = [];
    addModelAnimation(new TransformNode('other', scene), (dt) => steps.push(dt));
    stepModelAnimations(new TransformNode('root', scene), 1);
    expect(steps).toEqual([]);
    scene.dispose();
  });
});
