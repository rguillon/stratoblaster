import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { SubMesh } from '@babylonjs/core/Meshes/subMesh';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { WEATHER_KINDS, type WeatherKind } from '../../config/weather';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import { createRng } from '../../core/math/rng';
import { weatherParticles } from '../../core/scenery/sky-look';
import { BELOW_CLOUDS_GROUP } from './cloud-layers';

type Rgb = readonly [number, number, number];

/** What the particles of a weather show on one frame (P08-R05). */
export interface WeatherFrame {
  readonly time: number;
  /** 0..1: sets the wind and how much the particles streak. */
  readonly strength: number;
  readonly cameraPosition: Vector3;
  /** The camera's right and up directions, to face the particles to it. */
  readonly right: Vector3;
  readonly up: Vector3;
  /** Z where the box of air they fill starts (it follows the view, they stay put). */
  readonly start: number;
  readonly fog: { readonly color: Rgb; readonly start: number; readonly end: number };
}

/** The material of a weather's particles, driven frame by frame. */
export interface WeatherMaterial {
  readonly material: Material;
  set(frame: WeatherFrame): void;
}

/** Builds the material of the particles of `kind`. */
export type WeatherMaterialFactory = (scene: Scene, kind: WeatherKind) => WeatherMaterial;

/** Draw order among the see-through meshes above the ground: after both cloud layers. */
const WEATHER_ALPHA_INDEX = 4;
/** Indices of one particle's quad. */
const QUAD_INDICES = 6;

/** Draws only the first `count` particles of `mesh` (one sub-mesh over their quads). */
function drawFirst(mesh: Mesh, count: number): void {
  const sub = mesh.subMeshes[0];
  if (sub?.indexCount === count * QUAD_INDICES) return;
  mesh.releaseSubMeshes();
  SubMesh.AddToMesh(0, 0, mesh.getTotalVertices(), 0, count * QUAD_INDICES, mesh);
}

/**
 * The particles of a weather kind (P08-R05): one mesh of `maxParticles` small quads, each with
 * its own random place in the box of air, depth, size and fall speed (the `flake` attribute);
 * the material moves them on the GPU, so nothing is uploaded per frame. Only the first
 * `weatherParticles` of them are drawn.
 */
function buildParticles(scene: Scene, id: string, kind: WeatherKind, material: Material): Mesh {
  const count = kind.maxParticles;
  const random = createRng(id.length * 7919 + count);
  const positions: number[] = [];
  const flakes: number[] = [];
  const indices: number[] = [];
  for (let i = 0; i < count; i++) {
    const flake = [random(), random(), random(), random()];
    for (const [x, y] of [
      [-0.5, -0.5],
      [0.5, -0.5],
      [0.5, 0.5],
      [-0.5, 0.5],
    ] as const) {
      positions.push(x, y, 0);
      flakes.push(...flake);
    }
    const v = i * 4;
    indices.push(v, v + 1, v + 2, v, v + 2, v + 3);
  }
  const mesh = new Mesh(`weather-${id}`, scene);
  const data = new VertexData();
  data.positions = positions;
  data.indices = indices;
  data.applyToMesh(mesh);
  mesh.setVerticesData('flake', flakes, false, 4);
  mesh.material = material;
  mesh.isPickable = false;
  // The quads are placed by the material: the mesh's own bounds mean nothing.
  mesh.alwaysSelectAsActiveMesh = true;
  mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
  mesh.alphaIndex = WEATHER_ALPHA_INDEX;
  mesh.setEnabled(false);
  return mesh;
}

/**
 * The weather of a level (P08-R05): the particles of its kind, as many as its strength asks,
 * falling through the air between the ground and the flight altitude, behind everything on the
 * playfield. It is only a look: nothing in the simulation reads it.
 */
export class WeatherLayer {
  readonly #layers = new Map<string, { mesh: Mesh; material: WeatherMaterial }>();
  #drawn = 0;

  constructor(
    private readonly scene: Scene,
    private readonly materials: WeatherMaterialFactory,
    private readonly kinds: Readonly<Record<string, WeatherKind>> = WEATHER_KINDS,
  ) {}

  /** Particles drawn on the last frame. */
  get drawn(): number {
    return this.#drawn;
  }

  /** Shows the weather of `atmosphere` for this frame. */
  update(atmosphere: Atmosphere, frame: Omit<WeatherFrame, 'strength' | 'fog'>): void {
    const { weather } = atmosphere;
    const count = weatherParticles(weather);
    for (const [id, layer] of this.#layers) layer.mesh.setEnabled(id === weather.kind && count > 0);
    this.#drawn = 0;
    const kind = this.kinds[weather.kind];
    if (count === 0 || !kind) return;
    const layer = this.#layer(weather.kind, kind);
    drawFirst(layer.mesh, count);
    layer.material.set({
      ...frame,
      strength: weather.strength,
      fog: { color: atmosphere.sky.haze, ...atmosphere.fog },
    });
    this.#drawn = count;
  }

  #layer(id: string, kind: WeatherKind): { mesh: Mesh; material: WeatherMaterial } {
    let layer = this.#layers.get(id);
    if (!layer) {
      const material = this.materials(this.scene, kind);
      layer = { mesh: buildParticles(this.scene, id, kind, material.material), material };
      this.#layers.set(id, layer);
    }
    layer.mesh.setEnabled(true);
    return layer;
  }
}
