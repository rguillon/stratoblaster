import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { NodeAdopter } from '../../../src/render/node-adopter';

function setUp() {
  const scene = new Scene(new NullEngine());
  const root = new TransformNode('layer', scene);
  const seen: AbstractMesh[] = [];
  const adopter = new NodeAdopter(scene, root, 2, (mesh) => seen.push(mesh));
  return { scene, root, seen, adopter };
}

describe('NodeAdopter', () => {
  it('P05-R11: parents what is created during run to the layer, and draws its meshes in its group', () => {
    const { scene, root, seen, adopter } = setUp();
    const before = CreateBox('before', {}, scene);
    const [node, box, child] = adopter.run(() => {
      const n = new TransformNode('node', scene);
      const b = CreateBox('box', {}, scene);
      const c = CreateBox('child', {}, scene);
      c.parent = n;
      return [n, b, c] as const;
    });
    expect(node.parent).toBe(root);
    expect(box.parent).toBe(root);
    expect(child.parent).toBe(node);
    expect([box.renderingGroupId, child.renderingGroupId]).toEqual([2, 2]);
    expect(seen).toEqual([box, child]);
    expect(before.parent).toBeNull();
    expect(before.renderingGroupId).toBe(0);
  });

  it('clones of an adopted template stay in the layer by themselves', () => {
    const { scene, root, adopter } = setUp();
    const template = adopter.run(() => CreateBox('template', {}, scene));
    const clone = template.clone('clone');
    expect(clone.parent).toBe(root);
    expect(clone.renderingGroupId).toBe(2);
  });

  it('adopts even when run throws', () => {
    const { scene, root, adopter } = setUp();
    let made: TransformNode | undefined;
    expect(() =>
      adopter.run(() => {
        made = new TransformNode('half', scene);
        throw new Error('boom');
      }),
    ).toThrow('boom');
    expect(made?.parent).toBe(root);
  });
});
