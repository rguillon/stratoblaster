import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { Matrix, Quaternion, Vector3 } from '@babylonjs/core/Maths/math.vector';
import '@babylonjs/core/Meshes/thinInstanceMesh';
import type { PropPlacement } from '../../core/scenery/prop-placement';
import type { ColoredGeometry } from '../geometry/gradient-shapes';
import { allowed } from '../../core/scenery/draws';
import type { PropKindRule, SceneryLevel } from '../../core/scenery/scenery-level';
import { PLUME_KINDS } from '../../config/plumes';
import {
  buildPlumeMeshes,
  type PlumeFrame,
  type PlumeMaterial,
  type PlumeMaterialFactory,
} from './plume-layer';
import type { PropModelFactory } from './scenery-look';

/** Materials of the props: the lit structure, and the self-lit accents. */
export interface PropMaterials {
  readonly structure: Material;
  readonly lights: Material;
}

interface PropMeshes {
  readonly structure: Mesh;
  readonly lights: Mesh | undefined;
  /** Phase 10: its smoke or steam, drawn with the same instances. */
  readonly plumes: readonly Mesh[];
}

const MATRIX_FLOATS = 16;

/** A disabled, unpickable mesh of `geo`, drawn with `material`. */
export function meshOf(name: string, geo: ColoredGeometry, material: Material, scene: Scene): Mesh {
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

/** How a kind of prop drifts (`PropKindRule.drift`). */
export type PropDrift = NonNullable<PropKindRule['drift']>;

/** The kinds of `level` that drift, and how (phase 8: floating ice; phase 10: wagons on lines). */
export function propDrifts(level: SceneryLevel): Record<string, PropDrift> {
  const kinds = level.props.floating?.kinds ?? [];
  const lines = level.props.lines ?? [];
  return Object.fromEntries([
    ...kinds.flatMap((k) => (k.drift ? [[k.id, k.drift] as const] : [])),
    ...lines.flatMap((l) => (l.drift ? [[l.kind, l.drift] as const] : [])),
  ]);
}

/**
 * The kinds of prop `level` can stand on its ground (not its cars): the buildings and trees its
 * sections allow, its floating props, lines, podiums and set pieces.
 */
export function levelPropKinds(level: SceneryLevel): Set<string> {
  const { props, sections } = level;
  const groups = sections.flatMap((s) => allowed(props.groups, s.groups));
  return new Set([
    ...groups.flatMap((g) => g.kinds.map((k) => k.id)),
    ...sections.flatMap((s) => allowed(props.trees, s.trees).map((t) => t.id)),
    ...(props.floating?.kinds.map((k) => k.id) ?? []),
    ...(props.lines?.map((l) => l.kind) ?? []),
    ...sections.flatMap((s) => s.blocks?.podiums ?? []),
    ...(props.landmarks?.map((l) => l.kind) ?? []),
  ]);
}

/**
 * The models of the props of `level` (`levelPropKinds`): only those are built (reviewer,
 * 2026-10-28: building all the game's took about 36 ms and 841 meshes per level). Throws if one
 * of them, or one of its cars, has no model.
 */
export function levelPropModels(
  level: SceneryLevel,
  models: Readonly<Record<string, PropModelFactory>>,
): Record<string, PropModelFactory> {
  checkPropModels(level, models);
  const kinds = levelPropKinds(level);
  return Object.fromEntries(Object.entries(models).filter(([id]) => kinds.has(id)));
}

/** Throws if a prop kind of `level`, or one of its cars, has no model. */
export function checkPropModels(
  level: SceneryLevel,
  models: Readonly<Record<string, PropModelFactory>>,
): void {
  for (const id of [...levelPropKinds(level), ...(level.props.cars?.kinds ?? [])]) {
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
  /** Phase 10: one material per kind of plume, driven every frame. */
  readonly #plumeMaterials = new Map<string, PlumeMaterial>();
  readonly #chunks = new Map<number, readonly PropPlacement[]>();
  /** The placements uploaded last for each kind (P13-R04: unchanged kinds are not uploaded). */
  readonly #drawn = new Map<string, readonly PropPlacement[]>();
  #dirty = false;
  /** Only the props whose Z is in this range are drawn, if set (see {@link setWindow}). */
  #window: { readonly zMin: number; readonly zMax: number } | undefined;

  constructor(
    scene: Scene,
    models: Readonly<Record<string, PropModelFactory>>,
    materials: PropMaterials,
    onStructure: (mesh: Mesh) => void = () => undefined,
    plumeMaterials?: PlumeMaterialFactory,
  ) {
    const plumeMaterial = (id: string) => {
      const kind = PLUME_KINDS[id];
      if (!plumeMaterials || !kind) return undefined;
      let material = this.#plumeMaterials.get(id);
      if (!material) {
        material = plumeMaterials(scene, kind);
        this.#plumeMaterials.set(id, material);
      }
      return material.material;
    };
    for (const [kind, factory] of Object.entries(models)) {
      const geometry = factory();
      const structure = meshOf(`prop-${kind}`, geometry.structure, materials.structure, scene);
      structure.receiveShadows = true;
      onStructure(structure);
      const lights =
        geometry.lights && geometry.lights.indices.length > 0
          ? meshOf(`prop-${kind}-lights`, geometry.lights, materials.lights, scene)
          : undefined;
      const plumes = buildPlumeMeshes(scene, `prop-${kind}`, geometry.plumes ?? [], plumeMaterial);
      this.#meshes.set(kind, { structure, lights, plumes });
    }
  }

  /**
   * Draws the meshes without checking whether they are in view, so their bounds are never fitted
   * to their instances (reviewer, 2026-10-28: for the cars, placed again every frame, that was the
   * largest cost of a frame in Worlds 3 and 4; some cars are always in view anyway). Not for the
   * meshes that cast shadows: the light fits its shadows to their bounds.
   */
  drawAlways(): void {
    for (const { structure, lights, plumes } of this.#meshes.values()) {
      for (const mesh of [structure, lights, ...plumes]) {
        if (!mesh) continue;
        mesh.alwaysSelectAsActiveMesh = true;
        mesh.doNotSyncBoundingInfo = true;
      }
    }
  }

  /** Phase 10: moves the smoke and steam of the props on to this frame. */
  updatePlumes(frame: PlumeFrame): void {
    for (const material of this.#plumeMaterials.values()) material.set(frame);
  }

  /** Plume meshes drawn (phase 10). */
  get plumeCount(): number {
    let count = 0;
    for (const m of this.#meshes.values()) count += m.plumes.filter((p) => p.isEnabled()).length;
    return count;
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

  /** Meshes of the lit structures (e.g. to hide the lights behind them in a glow layer). */
  get structureMeshes(): Mesh[] {
    return [...this.#meshes.values()].map((m) => m.structure);
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

  /**
   * Moves the kinds that drift (phase 8: ice floes on the sea) to where they are `time` seconds
   * in: to and fro around where they were placed, each kind on its own course.
   */
  drift(drifts: Readonly<Record<string, PropDrift>>, time: number): void {
    for (const [kind, { x, z, period }] of Object.entries(drifts)) {
      const meshes = this.#meshes.get(kind);
      if (!meshes) continue;
      const phase = (2 * Math.PI * time) / period;
      for (const mesh of [meshes.structure, meshes.lights, ...meshes.plumes]) {
        mesh?.position.set(x * Math.sin(phase), 0, z * Math.sin(phase * 0.7 + 1));
      }
    }
  }

  /** Uploads the instance matrices if the placements or the window changed since the last call. */
  sync(): void {
    if (!this.#dirty) return;
    this.#dirty = false;
    const byKind = this.#byKind();
    for (const [kind, meshes] of this.#meshes) {
      const placements = byKind.get(kind) ?? [];
      if (samePlacements(this.#drawn.get(kind), placements)) continue;
      this.#drawn.set(kind, placements);
      const matrices = instanceMatrices(placements);
      for (const mesh of [meshes.structure, meshes.lights, ...meshes.plumes]) {
        if (!mesh) continue;
        mesh.setEnabled(matrices.length > 0);
        if (matrices.length === 0) continue;
        // Also fits the mesh's bounds to its instances, unless `drawAlways` turned that off.
        mesh.thinInstanceSetBuffer('matrix', matrices, MATRIX_FLOATS, false);
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

/** Whether `a` and `b` hold the same placements in the same order (or none in both). */
function samePlacements(
  a: readonly PropPlacement[] | undefined,
  b: readonly PropPlacement[],
): boolean {
  if (a === undefined) return false;
  return a.length === b.length && a.every((p, i) => p === b[i]);
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
