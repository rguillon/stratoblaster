import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import type { Road } from '../../core/scenery/road-network';
import { cachedRoadPieces } from '../../core/scenery/road-tiles';
import type { TileRules } from '../../core/scenery/scenery-level';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import { buildRoadGeometry, type RoadLook } from './road-geometry';
import { buildTileGrid, buildTileRoadGeometry, type TileRoadLook } from './tile-road-geometry';

/** Colour of the grid of tiles drawn with `tiles=1` (phase 15). */
const GRID_COLOR = [0, 0.9, 1] as const;
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
    /** Whether the ribbons fade with their vertex alpha (else they are drawn opaque). */
    private readonly seeThrough = true,
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
    mesh.hasVertexAlpha = this.seeThrough;
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

/** The paths and the other roads of a list of roads, and whether all are streets. */
interface SplitRoads {
  readonly paths: readonly Road[];
  readonly roads: readonly Road[];
  readonly streetsOnly: boolean;
}

/** The winding roads of a list, without its streets on tiles (phase 15). */
const winding = new WeakMap<readonly Road[], readonly Road[]>();

/** The roads split once per list (P13-R04). */
const splits = new WeakMap<readonly Road[], SplitRoads>();

function splitRoads(roads: readonly Road[]): SplitRoads {
  let split = splits.get(roads);
  if (!split) {
    split = {
      paths: roads.filter((r) => r.kind === 'cross'),
      roads: roads.filter((r) => r.kind !== 'cross'),
      streetsOnly: roads.every((r) => r.kind === 'street'),
    };
    splits.set(roads, split);
  }
  return split;
}

/**
 * Depth offset of the opaque middles of the streets: pulled towards the camera less than the
 * see-through ribbons and lane markings (-2), which stay on top of them.
 */
const STREET_Z_OFFSET = -1;

/** The road material, opaque: written in depth, so the terrain under it is not shaded. */
function opaqueOf(material: Material): Material {
  const opaque = material.clone(`${material.name}-opaque`) ?? material;
  opaque.disableDepthWrite = false;
  opaque.zOffset = STREET_Z_OFFSET;
  return opaque;
}

/** Draw order of the see-through road ribbons: before the sea (0) and the clouds. */
const DRAW_ORDER = { paths: -2, roads: -1 } as const;

/**
 * The ribbons of the paths and of the main roads, in two fields: the paths are drawn first, so
 * the roads stay on top where they meet (phase 4 review). Where all the roads are streets, the
 * even middles of the streets are a third field, drawn opaque before the see-through ones and
 * hiding the terrain under them (reviewer, 2026-10-28); their soft edges and markings stay in
 * the roads' field, drawn over them. Elsewhere a street drawn before a road or a path would end
 * up under it.
 */
export class RoadLayers {
  readonly #paths: RoadField;
  readonly #roads: RoadField;
  readonly #streets: RoadField;

  #grid: RoadField | undefined;
  readonly #scene: Scene;
  readonly #material: Material;

  constructor(scene: Scene, material: Material) {
    this.#scene = scene;
    this.#material = material;
    this.#paths = new RoadField(scene, material, 'paths', DRAW_ORDER.paths);
    this.#roads = new RoadField(scene, material, 'roads', DRAW_ORDER.roads);
    this.#streets = new RoadField(scene, opaqueOf(material), 'streets', 0, false);
  }

  /** Number of chunks with road ribbons. */
  get count(): number {
    return Math.max(this.#roads.count, this.#paths.count);
  }

  /** The opaque middles of the streets of a chunk, if drawn apart. */
  streetsOf(index: number): Mesh | undefined {
    return this.#streets.mesh(index);
  }

  /**
   * Ribbons of the segments of `roads` that start in the chunk's Z range; with `tiles` (phase
   * 15), the streets are road pieces on the grid instead, opaque.
   */
  setChunk(
    index: number,
    roads: readonly Road[],
    ground: HeightSource,
    span: { readonly zMin: number; readonly zMax: number },
    look: RoadLook,
    tiles?: TileRules,
  ): void {
    if (tiles && look.tiles) {
      this.#setTileChunk(index, roads, ground, span, look, [tiles, look.tiles]);
      return;
    }
    const split = splitRoads(roads);
    const { zMin, zMax } = span;
    this.#paths.setChunk(index, buildRoadGeometry(split.paths, ground, zMin, zMax, look));
    // Main roads and streets, the middles of the streets apart if they are all there is.
    const middles = split.streetsOnly ? { positions: [], indices: [], colors: [] } : undefined;
    this.#roads.setChunk(index, buildRoadGeometry(split.roads, ground, zMin, zMax, look, middles));
    if (middles) this.#streets.setChunk(index, middles);
    else this.#streets.removeChunk(index);
  }

  #setTileChunk(
    index: number,
    roads: readonly Road[],
    ground: HeightSource,
    { zMin, zMax }: { readonly zMin: number; readonly zMax: number },
    look: RoadLook,
    [tiles, tileLook]: readonly [TileRules, TileRoadLook],
  ): void {
    const split = splitRoads(roads);
    const others = winding.get(roads) ?? split.roads.filter((r) => r.kind !== 'street');
    winding.set(roads, others);
    this.#paths.setChunk(index, buildRoadGeometry(split.paths, ground, zMin, zMax, look));
    this.#roads.setChunk(index, buildRoadGeometry(others, ground, zMin, zMax, look));
    const pieces = cachedRoadPieces(roads, tiles);
    const height = (x: number, z: number): number => ground.height(x, z);
    this.#streets.setChunk(
      index,
      buildTileRoadGeometry(pieces, tiles, tileLook, height, [zMin, zMax]),
    );
    if (this.#grid) {
      this.#grid.setChunk(index, buildTileGrid(pieces, tiles, height, [zMin, zMax], GRID_COLOR));
    }
  }

  /** Phase 15 (P15-R10, `tiles=1`): draws the grid of tiles over the districts from now on. */
  showTileGrid(): void {
    this.#grid ??= new RoadField(this.#scene, this.#gridMaterial(), 'tile-grid', 0, false);
  }

  #gridMaterial(): Material {
    const material = this.#material.clone('tile-grid') ?? this.#material;
    material.disableDepthWrite = false;
    material.zOffset = -3;
    return material;
  }

  removeChunk(index: number): void {
    this.#grid?.removeChunk(index);
    this.#paths.removeChunk(index);
    this.#roads.removeChunk(index);
    this.#streets.removeChunk(index);
  }

  clear(): void {
    this.#grid?.clear();
    this.#paths.clear();
    this.#roads.clear();
    this.#streets.clear();
  }
}
