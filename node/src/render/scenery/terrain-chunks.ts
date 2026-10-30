import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexBuffer } from '@babylonjs/core/Buffers/buffer';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { buildGridIndices, buildTerrainGeometry, type HeightSource } from './terrain-geometry';

/** Size of the terrain chunks. */
export interface TerrainChunkOptions {
  /** Length of a chunk along Z. */
  readonly length: number;
  /** Grid cell size. */
  readonly cell: number;
  /** Chunks span X from `xMin` over `columns` cells. */
  readonly xMin: number;
  readonly columns: number;
}

/** Index and Z range of one chunk. */
export interface ChunkSpan {
  readonly index: number;
  readonly zMin: number;
  readonly zMax: number;
}

/** What {@link TerrainChunks.cover} changed. */
export interface ChunkChanges {
  readonly added: readonly ChunkSpan[];
  readonly removed: readonly number[];
}

/**
 * The terrain as a row of chunks along Z (P04-R01): only the chunks under the camera exist, and
 * the meshes of chunks that scroll out of view are reused for new ones (ENG-19).
 */
export class TerrainChunks {
  readonly #live = new Map<number, Mesh>();
  readonly #free: Mesh[] = [];
  readonly #rows: number;
  readonly #indices: Uint32Array;
  #created = 0;

  constructor(
    private readonly scene: Scene,
    private readonly material: Material,
    private readonly options: TerrainChunkOptions,
    private source: HeightSource,
    /** Called once for each new mesh (e.g. to make it cast shadows). */
    private readonly onMesh: (mesh: Mesh) => void = () => undefined,
  ) {
    this.#rows = Math.max(1, Math.round(options.length / options.cell));
    this.#indices = buildGridIndices(options.columns, this.#rows);
  }

  /** Number of chunks in the scene. */
  get count(): number {
    return this.#live.size;
  }

  /** The chunk meshes in use, by chunk index. */
  get meshes(): ReadonlyMap<number, Mesh> {
    return this.#live;
  }

  span(index: number): ChunkSpan {
    const zMin = index * this.options.length;
    return { index, zMin, zMax: zMin + this.options.length };
  }

  /** Keeps exactly the chunks that overlap [zMin, zMax]. */
  cover(zMin: number, zMax: number): ChunkChanges {
    const first = Math.floor(zMin / this.options.length);
    const last = Math.floor(zMax / this.options.length);
    const removed: number[] = [];
    for (const [index, mesh] of this.#live) {
      if (index < first || index > last) {
        mesh.setEnabled(false);
        this.#free.push(mesh);
        this.#live.delete(index);
        removed.push(index);
      }
    }
    const added: ChunkSpan[] = [];
    for (let index = first; index <= last; index++) {
      if (!this.#live.has(index)) {
        this.#live.set(index, this.#fill(this.#free.pop() ?? this.#newMesh(), index));
        added.push(this.span(index));
      }
    }
    return { added, removed };
  }

  /** Rebuilds every chunk from a new height source (e.g. a new seed). */
  rebuild(source: HeightSource): void {
    this.source = source;
    for (const [index, mesh] of this.#live) this.#fill(mesh, index);
  }

  #grid(index: number) {
    const { xMin, columns, cell } = this.options;
    return { xMin, zMin: this.span(index).zMin, columns, rows: this.#rows, cell };
  }

  #newMesh(): Mesh {
    const mesh = new Mesh(`terrain-chunk-${String(this.#created++)}`, this.scene);
    const { positions, normals, colors } = buildTerrainGeometry(this.source, this.#grid(0));
    const data = new VertexData();
    data.positions = positions;
    data.normals = normals;
    data.colors = colors;
    data.indices = this.#indices;
    data.applyToMesh(mesh, true);
    mesh.material = this.material;
    mesh.isPickable = false;
    mesh.receiveShadows = true;
    this.onMesh(mesh);
    return mesh;
  }

  #fill(mesh: Mesh, index: number): Mesh {
    const { positions, normals, colors } = buildTerrainGeometry(this.source, this.#grid(index));
    mesh.updateVerticesData(VertexBuffer.PositionKind, positions);
    mesh.updateVerticesData(VertexBuffer.NormalKind, normals);
    mesh.updateVerticesData(VertexBuffer.ColorKind, colors);
    mesh.refreshBoundingInfo();
    mesh.setEnabled(true);
    return mesh;
  }
}
