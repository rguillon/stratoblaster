import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import type { Road } from '../../core/scenery/road-network';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import { buildRoadGeometry, type RoadLook } from './road-geometry';
import type { HeightSource } from './terrain-geometry';

/**
 * Road ribbons of the terrain chunks in view, one mesh per chunk (P04-R07). See-through meshes
 * are drawn by increasing `alphaIndex`: a field of paths with a lower one than the field of
 * roads keeps the roads on top where they meet.
 */
export class RoadField {
  readonly #meshes = new Map<number, Mesh>();

  constructor(
    private readonly scene: Scene,
    private readonly material: Material,
    private readonly name: string,
    /** Draw order among the see-through meshes (the sea is 0, clouds above). */
    private readonly alphaIndex: number,
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
    const mesh = new Mesh(`${this.name}-${String(index)}`, this.scene);
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
    // The roads fade into the ground with their vertex alpha.
    mesh.hasVertexAlpha = true;
    mesh.alphaIndex = this.alphaIndex;
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

/** Draw order of the see-through road ribbons: before the sea (0) and the clouds. */
const DRAW_ORDER = { paths: -2, roads: -1 } as const;

/**
 * The ribbons of the paths and of the main roads, in two fields: the paths are drawn first, so
 * the roads stay on top where they meet (phase 4 review).
 */
export class RoadLayers {
  readonly #paths: RoadField;
  readonly #roads: RoadField;

  constructor(scene: Scene, material: Material) {
    this.#paths = new RoadField(scene, material, 'paths', DRAW_ORDER.paths);
    this.#roads = new RoadField(scene, material, 'roads', DRAW_ORDER.roads);
  }

  /** Number of chunks with road ribbons. */
  get count(): number {
    return Math.max(this.#roads.count, this.#paths.count);
  }

  /** Ribbons of the segments of `roads` that start in the chunk's Z range. */
  setChunk(
    index: number,
    roads: readonly Road[],
    ground: HeightSource,
    span: { readonly zMin: number; readonly zMax: number },
    look: RoadLook,
  ): void {
    const ribbons = (paths: boolean): ColoredGeometry =>
      buildRoadGeometry(
        roads.filter((r) => (r.kind === 'cross') === paths),
        ground,
        span.zMin,
        span.zMax,
        look,
      );
    this.#paths.setChunk(index, ribbons(true));
    // Main roads and streets.
    this.#roads.setChunk(index, ribbons(false));
  }

  removeChunk(index: number): void {
    this.#paths.removeChunk(index);
    this.#roads.removeChunk(index);
  }

  clear(): void {
    this.#paths.clear();
    this.#roads.clear();
  }
}
