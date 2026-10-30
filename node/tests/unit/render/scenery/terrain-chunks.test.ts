import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TerrainChunks } from '../../../../src/render/scenery/terrain-chunks';

const OPTIONS = { length: 100, cell: 10, xMin: -50, columns: 10 };

describe('TerrainChunks', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
  });

  function chunks(height = 5, onMesh?: (mesh: Mesh) => void) {
    scene = new Scene(new NullEngine());
    const material = new StandardMaterial('ground', scene);
    return new TerrainChunks(scene, material, OPTIONS, { height: () => height }, onMesh);
  }

  it('P04-R01: keeps only the chunks under the given Z range', () => {
    const terrain = chunks();
    const first = terrain.cover(-20, 250);
    expect(first.added.map((s) => s.index)).toEqual([-1, 0, 1, 2]);
    expect(first.removed).toEqual([]);
    expect(terrain.count).toBe(4);
    const next = terrain.cover(120, 330);
    expect([...next.removed].sort()).toEqual([-1, 0]);
    expect(next.added.map((s) => s.index)).toEqual([3]);
    expect(terrain.span(3)).toEqual({ index: 3, zMin: 300, zMax: 400 });
  });

  it('ENG-19: reuses the meshes of chunks that scrolled away', () => {
    const created: Mesh[] = [];
    const terrain = chunks(5, (m) => created.push(m));
    terrain.cover(0, 150);
    terrain.cover(1000, 1150);
    expect(created).toHaveLength(2);
    const mesh = terrain.meshes.get(10);
    const positions = mesh?.getVerticesData('position') ?? [];
    expect(positions[2]).toBe(1000);
    expect(positions[1]).toBe(5);
    expect(mesh?.receiveShadows).toBe(true);
    expect(mesh?.getTotalIndices()).toBe(10 * 10 * 6);
  });

  it('P04-R01: rebuilds the live chunks from a new height source', () => {
    const terrain = chunks();
    terrain.cover(0, 50);
    terrain.rebuild({ height: () => 42 });
    expect(terrain.meshes.get(0)?.getVerticesData('position')?.[1]).toBe(42);
  });
});
