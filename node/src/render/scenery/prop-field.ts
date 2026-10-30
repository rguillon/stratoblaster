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
import type { PropGeometry, PropModelFactory } from './scenery-look';

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

/**
 * The props of one kind in a chunk, with their instance matrices, made on their first upload and
 * kept while the chunk is (reviewer, 2026-10-28: not made again each time the window moves).
 */
interface KindProps {
  readonly placements: PropPlacement[];
  matrices: Float32Array | undefined;
}

/** The props of a kind to draw: each placement, and the chunk's props it comes from, at `at`. */
interface Drawn {
  readonly placements: PropPlacement[];
  readonly from: KindProps[];
  readonly at: number[];
}

/**
 * Each prop model's geometry, made once and kept for the next levels (reviewer, 2026-10-28): the
 * models are the same every time. Nothing changes a geometry once made.
 */
const GEOMETRIES = new WeakMap<PropModelFactory, PropGeometry>();

/** The geometry of `factory`, made on first use. */
function geometryOf(factory: PropModelFactory): PropGeometry {
  let geometry = GEOMETRIES.get(factory);
  if (!geometry) {
    geometry = factory();
    GEOMETRIES.set(factory, geometry);
  }
  return geometry;
}

/** The normals of each geometry, worked out once. */
const NORMALS = new WeakMap<ColoredGeometry, number[]>();

function normalsOf(geo: ColoredGeometry): number[] {
  let normals = NORMALS.get(geo);
  if (!normals) {
    normals = [];
    VertexData.ComputeNormals(geo.positions, geo.indices, normals);
    NORMALS.set(geo, normals);
  }
  return normals;
}

/**
 * Draws `mesh` without checking whether it is in view, so its bounds are never fitted to its
 * instances (reviewer, 2026-10-28): for the cars, placed again every frame, that was the largest
 * single cost of a frame in Worlds 3 and 4, and for the other props half of each upload. Their
 * instances are near the view anyway, and the sun's shadows have a fixed frustum
 * (`shadowFrustumSize`), which no bounds change.
 */
function drawAlways(mesh: Mesh): void {
  mesh.alwaysSelectAsActiveMesh = true;
  mesh.doNotSyncBoundingInfo = true;
}

/** A disabled, unpickable mesh of `geo`, drawn with `material`. */
export function meshOf(name: string, geo: ColoredGeometry, material: Material, scene: Scene): Mesh {
  const mesh = new Mesh(name, scene);
  const data = new VertexData();
  data.positions = geo.positions;
  data.indices = geo.indices;
  data.colors = geo.colors;
  data.normals = normalsOf(geo);
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
 * sections allow, its floating props, lines, podiums, set pieces and lots.
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
    // Phase 15: the lots of the districts on tiles.
    ...(props.lots?.map((k) => k.id) ?? []),
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
  /** The placements of each chunk, by kind. */
  readonly #chunks = new Map<number, ReadonlyMap<string, KindProps>>();
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
      const geometry = geometryOf(factory);
      const structure = meshOf(`prop-${kind}`, geometry.structure, materials.structure, scene);
      structure.receiveShadows = true;
      onStructure(structure);
      const lights =
        geometry.lights && geometry.lights.indices.length > 0
          ? meshOf(`prop-${kind}-lights`, geometry.lights, materials.lights, scene)
          : undefined;
      const plumes = buildPlumeMeshes(scene, `prop-${kind}`, geometry.plumes ?? [], plumeMaterial);
      for (const mesh of [structure, lights, ...plumes]) if (mesh) drawAlways(mesh);
      this.#meshes.set(kind, { structure, lights, plumes });
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
    for (const kinds of this.#chunks.values()) {
      for (const { placements } of kinds.values()) count += placements.length;
    }
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
    const kinds = new Map<string, KindProps>();
    for (const p of placements) {
      if (!this.#meshes.has(p.kind)) throw new Error(`No model for prop "${p.kind}"`);
      const props = kinds.get(p.kind);
      if (props) props.placements.push(p);
      else kinds.set(p.kind, { placements: [p], matrices: undefined });
    }
    this.#chunks.set(index, kinds);
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
      const drawn = byKind.get(kind);
      const placements = drawn?.placements ?? [];
      if (samePlacements(this.#drawn.get(kind), placements)) continue;
      this.#drawn.set(kind, placements);
      const matrices = drawn ? matricesOf(drawn) : new Float32Array(0);
      for (const mesh of [meshes.structure, meshes.lights, ...meshes.plumes]) {
        if (!mesh) continue;
        mesh.setEnabled(matrices.length > 0);
        if (matrices.length === 0) continue;
        mesh.thinInstanceSetBuffer('matrix', matrices, MATRIX_FLOATS, false);
      }
    }
  }

  /** The props to draw (in the window, if any), by kind, in the order of the chunks. */
  #byKind(): Map<string, Drawn> {
    const window = this.#window;
    const byKind = new Map<string, Drawn>();
    for (const kinds of this.#chunks.values()) {
      for (const [kind, props] of kinds) {
        props.placements.forEach((p, i) => {
          if (window && (p.z < window.zMin || p.z > window.zMax)) return;
          let drawn = byKind.get(kind);
          if (!drawn) byKind.set(kind, (drawn = { placements: [], from: [], at: [] }));
          drawn.placements.push(p);
          drawn.from.push(props);
          drawn.at.push(i);
        });
      }
    }
    return byKind;
  }
}

/** The instance matrices of `drawn`, copied from those of their chunks (made on first use). */
function matricesOf({ from, at }: Drawn): Float32Array {
  const buffer = new Float32Array(at.length * MATRIX_FLOATS);
  at.forEach((i, j) => {
    const props = from[j];
    if (!props) return;
    props.matrices ??= instanceMatrices(props.placements);
    const start = i * MATRIX_FLOATS;
    buffer.set(props.matrices.subarray(start, start + MATRIX_FLOATS), j * MATRIX_FLOATS);
  });
  return buffer;
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
