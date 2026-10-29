import type { Scene } from '@babylonjs/core/scene';
import { RawTexture } from '@babylonjs/core/Materials/Textures/rawTexture';
import { Texture } from '@babylonjs/core/Materials/Textures/texture';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import type { RoadPiece } from '../core/scenery/road-tiles';
import type { TileRules } from '../core/scenery/scenery-level';
import { ATLAS_SIZE, RoadAtlas } from '../render/scenery/road-atlas';
import { buildRoadSurfaces } from '../render/scenery/road-surface';
import type { TileRoadLook } from '../render/scenery/tile-road-geometry';

// The road pieces of the `props/` page (phase 15), drawn as in the levels: one textured surface
// per piece, its markings from the road atlas.

const flat = (): number => 0;
const ALL: readonly [number, number] = [-Infinity, Infinity];

/** Builds meshes of road pieces on flat ground, from one atlas and one material. */
export class ViewerRoads {
  readonly #atlas: RoadAtlas;
  readonly #texture: RawTexture;
  readonly #material: StandardMaterial;

  constructor(
    private readonly scene: Scene,
    private readonly tile: TileRules,
    private readonly look: TileRoadLook,
  ) {
    this.#atlas = new RoadAtlas(tile, look);
    this.#texture = RawTexture.CreateRGBATexture(
      this.#atlas.data,
      ATLAS_SIZE,
      ATLAS_SIZE,
      scene,
      true,
      false,
      Texture.TRILINEAR_SAMPLINGMODE,
    );
    this.#texture.anisotropicFilteringLevel = 8;
    this.#material = new StandardMaterial('props-roads', scene);
    this.#material.diffuseTexture = this.#texture;
    this.#material.specularColor = Color3.Black();
  }

  /** A mesh of `pieces`, or undefined when there are none. */
  mesh(name: string, pieces: readonly RoadPiece[]): Mesh | undefined {
    const { surfaces } = buildRoadSurfaces(pieces, [this.tile, this.look], this.#atlas, flat, ALL);
    if (this.#atlas.dirty) {
      this.#texture.update(this.#atlas.data);
      this.#atlas.dirty = false;
    }
    if (surfaces.indices.length === 0) return undefined;
    const mesh = new Mesh(name, this.scene);
    const data = new VertexData();
    data.positions = surfaces.positions;
    data.indices = surfaces.indices;
    data.uvs = surfaces.uvs;
    const normals: number[] = [];
    VertexData.ComputeNormals(surfaces.positions, surfaces.indices, normals);
    data.normals = normals;
    data.applyToMesh(mesh);
    mesh.material = this.#material;
    return mesh;
  }
}
