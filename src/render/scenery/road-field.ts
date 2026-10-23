import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import type { ColoredGeometry } from '../geometry/gradient-shapes';

/** The road ribbons of the terrain chunks in view, one mesh per chunk (P04-R07). */
export class RoadField {
  readonly #meshes = new Map<number, Mesh>();

  constructor(
    private readonly scene: Scene,
    private readonly material: Material,
  ) {}

  /** Number of chunks with roads. */
  get count(): number {
    return this.#meshes.size;
  }

  mesh(index: number): Mesh | undefined {
    return this.#meshes.get(index);
  }

  setChunk(index: number, geometry: ColoredGeometry): void {
    this.removeChunk(index);
    if (geometry.indices.length === 0) return;
    const mesh = new Mesh(`roads-${String(index)}`, this.scene);
    const data = new VertexData();
    data.positions = geometry.positions;
    data.indices = geometry.indices;
    data.colors = geometry.colors;
    const normals: number[] = [];
    VertexData.ComputeNormals(geometry.positions, geometry.indices, normals);
    data.normals = normals;
    data.applyToMesh(mesh);
    mesh.material = this.material;
    mesh.isPickable = false;
    mesh.receiveShadows = true;
    // The roads fade into the ground with their vertex alpha; drawn first of the see-through
    // meshes, before the sea and the clouds.
    mesh.hasVertexAlpha = true;
    mesh.alphaIndex = -1;
    this.#meshes.set(index, mesh);
  }

  removeChunk(index: number): void {
    this.#meshes.get(index)?.dispose();
    this.#meshes.delete(index);
  }

  clear(): void {
    for (const index of [...this.#meshes.keys()]) this.removeChunk(index);
  }
}
