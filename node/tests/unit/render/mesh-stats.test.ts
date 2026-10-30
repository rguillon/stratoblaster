import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { countTriangles } from '../../../src/render/mesh-stats';

describe('countTriangles', () => {
  it('counts the triangles of a mesh and of all the meshes under it', () => {
    const scene = new Scene(new NullEngine());
    const box = CreateBox('box', { size: 1 }, scene);
    expect(countTriangles(box)).toBe(12);

    const root = new TransformNode('root', scene);
    const group = new TransformNode('group', scene);
    group.parent = root;
    box.parent = group;
    CreateBox('other', { size: 1 }, scene).parent = root;
    expect(countTriangles(root)).toBe(24);
    scene.dispose();
  });

  it('counts unindexed meshes from their vertices', () => {
    const scene = new Scene(new NullEngine());
    const mesh = new Mesh('raw', scene);
    // Two triangles, no index buffer.
    mesh.setVerticesData('position', [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1]);
    expect(mesh.getTotalIndices()).toBe(0);
    expect(countTriangles(mesh)).toBe(2);
    scene.dispose();
  });
});
