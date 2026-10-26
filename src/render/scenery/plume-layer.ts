import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { PLUME_KINDS, type PlumeKind } from '../../config/plumes';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import type { PropPlume } from './scenery-look';

type Rgb = readonly [number, number, number];

/** What the plumes show on one frame. */
export interface PlumeFrame {
  readonly time: number;
  readonly cameraPosition: Vector3;
  /** The camera's right and up directions, to face the puffs to it. */
  readonly right: Vector3;
  readonly up: Vector3;
  /** How lit the puffs are (the scene's light), and the haze they fade into. */
  readonly light: Rgb;
  readonly fog: { readonly color: Rgb; readonly start: number; readonly end: number };
}

/** The material of one kind of plume, driven frame by frame. */
export interface PlumeMaterial {
  readonly material: Material;
  set(frame: PlumeFrame): void;
}

/** Builds the material of the plumes of `kind`. */
export type PlumeMaterialFactory = (scene: Scene, kind: PlumeKind) => PlumeMaterial;

/** Share of the sun's light the puffs take, and the most light they show. */
const PLUME_LIGHT = { sun: 0.35, most: 1.2 } as const;

/** Draw order among the see-through meshes of the ground: after the water. */
const PLUME_ALPHA_INDEX = 2;

/** One puff's quad: its corners, as `position` (x, y) around the puff's centre. */
const CORNERS = [
  [-0.5, -0.5],
  [0.5, -0.5],
  [0.5, 0.5],
  [-0.5, 0.5],
] as const;

/** The geometry of a prop's plumes of one kind: positions, `puff` attributes and indices. */
export interface PlumeGeometry {
  readonly positions: number[];
  /** Per vertex: where its column starts (model space) and its puff's phase (0..1). */
  readonly puffs: number[];
  /** Per vertex: its column's scale. */
  readonly scales: number[];
  readonly indices: number[];
}

/**
 * The quads of `plumes` (phase 10): `kind.puffs` per column, each puff a quad around the column's
 * foot whose `phase` spreads the puffs evenly up the column; the material lifts, grows and fades
 * them.
 */
export function plumeGeometry(plumes: readonly PropPlume[], kind: PlumeKind): PlumeGeometry {
  const positions: number[] = [];
  const puffs: number[] = [];
  const scales: number[] = [];
  const indices: number[] = [];
  plumes.forEach((plume, column) => {
    for (let i = 0; i < kind.puffs; i++) {
      // Columns start out of step, so neighbouring chimneys do not puff together.
      const phase = (i + ((column * 0.37) % 1)) / kind.puffs;
      const v = positions.length / 3;
      for (const [x, y] of CORNERS) {
        positions.push(x, y, 0);
        puffs.push(...plume.at, phase);
        scales.push(plume.scale ?? 1);
      }
      indices.push(v, v + 1, v + 2, v, v + 2, v + 3);
    }
  });
  return { positions, puffs, scales, indices };
}

/** How lit a plume is under `atmosphere`: its ambient light plus some of the sun's. */
export function plumeLight(atmosphere: Atmosphere): Rgb {
  const { ambient, sun } = atmosphere;
  const lit = (sky: number, color: number) =>
    Math.min(PLUME_LIGHT.most, sky * ambient.intensity + color * PLUME_LIGHT.sun * sun.intensity);
  return [
    lit(ambient.sky[0], sun.color[0]),
    lit(ambient.sky[1], sun.color[1]),
    lit(ambient.sky[2], sun.color[2]),
  ];
}

/**
 * The plume meshes of a prop kind (phase 10, P10-R08): one per plume kind it has, drawn with the
 * prop's own thin instances (so every placed prop smokes), always selected (the puffs rise far
 * above the prop's bounds), see-through and never writing depth.
 */
export function buildPlumeMeshes(
  scene: Scene,
  name: string,
  plumes: readonly PropPlume[],
  material: (kind: string) => Material | undefined,
  kinds: Readonly<Record<string, PlumeKind>> = PLUME_KINDS,
): Mesh[] {
  const ids = [...new Set(plumes.map((p) => p.kind))];
  return ids.flatMap((id) => {
    const kind = kinds[id];
    const mat = material(id);
    if (!kind || !mat) return [];
    const geometry = plumeGeometry(
      plumes.filter((p) => p.kind === id),
      kind,
    );
    const mesh = new Mesh(`${name}-plume-${id}`, scene);
    const data = new VertexData();
    data.positions = geometry.positions;
    data.indices = geometry.indices;
    data.applyToMesh(mesh);
    mesh.setVerticesData('puff', geometry.puffs, false, 4);
    mesh.setVerticesData('puffScale', geometry.scales, false, 1);
    mesh.material = mat;
    mesh.isPickable = false;
    mesh.alwaysSelectAsActiveMesh = true;
    mesh.alphaIndex = PLUME_ALPHA_INDEX;
    mesh.setEnabled(false);
    return [mesh];
  });
}
