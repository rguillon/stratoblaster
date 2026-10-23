import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { Matrix, Quaternion, Vector3 } from '@babylonjs/core/Maths/math.vector';
import '@babylonjs/core/Meshes/thinInstanceMesh';
import type { PropPlacement } from '../../core/scenery/prop-placement';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import type { PropModelFactory } from './scenery-look';

/** Materials of the props: the lit structure, and the self-lit accents. */
export interface PropMaterials {
  readonly structure: Material;
  readonly lights: Material;
}

interface PropMeshes {
  readonly structure: Mesh;
  readonly lights: Mesh | undefined;
}

const MATRIX_FLOATS = 16;

function meshOf(name: string, geo: ColoredGeometry, material: Material, scene: Scene): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  const normals: number[] = [];
  VertexData.ComputeNormals(geo.positions, geo.indices, normals);
  data.normals = normals;
  data.applyToMesh(mesh);
  mesh.material = material;
  mesh.isPickable = false;
  mesh.setEnabled(false);
  return mesh;
}

/** Throws if a prop kind of `level` has no model. */
export function checkPropModels(
  level: SceneryLevel,
  models: Readonly<Record<string, PropModelFactory>>,
): void {
  const ids = [
    ...level.props.groups.flatMap((g) => g.kinds.map((k) => k.id)),
    ...level.props.trees.map((t) => t.id),
    ...(level.props.cars?.kinds ?? []),
    ...level.sections.flatMap((s) => s.blocks?.podiums ?? []),
  ];
  for (const id of ids) {
    if (!(id in models)) throw new Error(`No model for prop "${id}"`);
  }
}

/**
 * The props standing on the terrain (P04-R04). Each kind of prop is one mesh (plus one for its
 * self-lit accents) drawn once per placement with thin instances (ENG-104). Placements are
 * grouped by terrain chunk, so they come and go with the chunks.
 */
export class PropField {
  readonly #meshes = new Map<string, PropMeshes>();
  readonly #chunks = new Map<number, readonly PropPlacement[]>();
  #dirty = false;
  /** Only the props whose Z is in this range are drawn, if set (see {@link setWindow}). */
  #window: { readonly zMin: number; readonly zMax: number } | undefined;

  constructor(
    scene: Scene,
    models: Readonly<Record<string, PropModelFactory>>,
    materials: PropMaterials,
    onStructure: (mesh: Mesh) => void = () => undefined,
  ) {
    for (const [kind, factory] of Object.entries(models)) {
      const geometry = factory();
      const structure = meshOf(`prop-${kind}`, geometry.structure, materials.structure, scene);
      structure.receiveShadows = true;
      onStructure(structure);
      const lights =
        geometry.lights && geometry.lights.indices.length > 0
          ? meshOf(`prop-${kind}-lights`, geometry.lights, materials.lights, scene)
          : undefined;
      this.#meshes.set(kind, { structure, lights });
    }
  }

  /** Number of props in the scene. */
  get count(): number {
    let count = 0;
    for (const placements of this.#chunks.values()) count += placements.length;
    return count;
  }

  /** Meshes of the self-lit accents (e.g. for a glow layer). */
  get lightMeshes(): Mesh[] {
    return [...this.#meshes.values()].flatMap((m) => (m.lights ? [m.lights] : []));
  }

  /** The structure mesh of a kind of prop. */
  structureOf(kind: string): Mesh | undefined {
    return this.#meshes.get(kind)?.structure;
  }

  setChunk(index: number, placements: readonly PropPlacement[]): void {
    for (const p of placements) {
      if (!this.#meshes.has(p.kind)) throw new Error(`No model for prop "${p.kind}"`);
    }
    this.#chunks.set(index, placements);
    this.#dirty = true;
  }

  removeChunk(index: number): void {
    this.#dirty = this.#chunks.delete(index) || this.#dirty;
  }

  clear(): void {
    this.#chunks.clear();
    this.#dirty = true;
  }

  /**
   * Draws only the props whose Z is in [zMin, zMax] (phase 4 review): the terrain chunks reach
   * well past the view, and their props would be drawn for nothing. The instances are uploaded
   * again only when the window leaves the range drawn, which is `step` wider on both sides.
   */
  setWindow(zMin: number, zMax: number, step: number): void {
    const drawn = this.#window;
    if (drawn && zMin >= drawn.zMin && zMax <= drawn.zMax) return;
    // A step wider than asked, so the view can move by a step before the next upload.
    this.#window = { zMin: zMin - step, zMax: zMax + step };
    this.#dirty = true;
  }

  /** Uploads the instance matrices if the placements or the window changed since the last call. */
  sync(): void {
    if (!this.#dirty) return;
    this.#dirty = false;
    const byKind = this.#byKind();
    for (const [kind, meshes] of this.#meshes) {
      const matrices = instanceMatrices(byKind.get(kind) ?? []);
      for (const mesh of [meshes.structure, meshes.lights]) {
        if (!mesh) continue;
        mesh.setEnabled(matrices.length > 0);
        if (matrices.length === 0) continue;
        mesh.thinInstanceSetBuffer('matrix', matrices, MATRIX_FLOATS, false);
        mesh.thinInstanceRefreshBoundingInfo(false);
      }
    }
  }

  /** The placements to draw (in the window, if any), by kind. */
  #byKind(): Map<string, PropPlacement[]> {
    const window = this.#window;
    const byKind = new Map<string, PropPlacement[]>();
    for (const placements of this.#chunks.values()) {
      for (const p of placements) {
        if (window && (p.z < window.zMin || p.z > window.zMax)) continue;
        const list = byKind.get(p.kind);
        if (list) list.push(p);
        else byKind.set(p.kind, [p]);
      }
    }
    return byKind;
  }
}

/**
 * One world matrix per placement (scale, or per-axis size, then turn around Y and position),
 * packed for thin instances.
 */
export function instanceMatrices(placements: readonly PropPlacement[]): Float32Array {
  const buffer = new Float32Array(placements.length * MATRIX_FLOATS);
  const scale = new Vector3();
  const position = new Vector3();
  const turn = new Quaternion();
  const matrix = new Matrix();
  placements.forEach((p, i) => {
    if (p.size) scale.set(...p.size);
    else scale.setAll(p.scale);
    position.set(p.x, p.y, p.z);
    Quaternion.RotationYawPitchRollToRef(p.rotation, 0, 0, turn);
    Matrix.ComposeToRef(scale, turn, position, matrix);
    matrix.copyToArray(buffer, i * MATRIX_FLOATS);
  });
  return buffer;
}
