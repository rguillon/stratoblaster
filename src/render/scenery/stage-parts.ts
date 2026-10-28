import type { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import type { Material } from '@babylonjs/core/Materials/material';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { SubMesh } from '@babylonjs/core/Meshes/subMesh';
import { RenderingGroup } from '@babylonjs/core/Rendering/renderingGroup';
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { RainRings } from './rain-rings';
import type { SceneryKit } from './scenery-kit';

// Pieces of a `SceneryStage` that need nothing else of it.

/** Lowest ground of a level: its sea, or the lowest relief. */
export function lowestGround(level: SceneryLevel): number {
  const lows = level.sections.map((s) => s.relief.base - s.relief.amplitude);
  return level.sea ? level.sea.level : Math.min(...lows);
}

/**
 * The order of the opaque meshes (reviewer, 2026-10-28): the terrain last, so its costly shading
 * is skipped where the props and cars in front of it were drawn first; the others by material, as
 * Babylon does.
 */
export function terrainLast(terrain: Material): (a: SubMesh, b: SubMesh) => number {
  const last = (s: SubMesh): number => (s.getMaterial() === terrain ? 1 : 0);
  return (a, b) => last(a) - last(b) || RenderingGroup.PainterSortCompare(a, b);
}

/** The stage's camera, `halfFov` up and down, seeing up to `farClip`; made the active one. */
export function stageCamera(scene: Scene, halfFov: number, farClip: number): FreeCamera {
  const camera = new FreeCamera('scenery-camera', Vector3.Zero(), scene);
  camera.fov = halfFov * 2;
  camera.minZ = 1;
  camera.maxZ = farClip;
  scene.activeCamera = camera;
  return camera;
}

/**
 * The sea plane of `level` (P04-R02; phase 10: or lava) and the rain rings on it (P09-R05),
 * `width` × `length`, if it has a sea.
 */
export function seaParts(
  scene: Scene,
  level: SceneryLevel,
  [width, length]: readonly [number, number],
  kit: Pick<SceneryKit, 'sea' | 'rings'>,
): { readonly sea: Mesh; readonly rings: RainRings } | undefined {
  if (!level.sea) return undefined;
  const height = level.sea.level;
  return {
    sea: seaPlane(scene, [width, length, height], kit.sea),
    rings: new RainRings(scene, kit.rings, [height, width, length]),
  };
}

/** The sea plane (P04-R02; phase 10: or lava), `width` × `length`, at `level`. */
export function seaPlane(
  scene: Scene,
  [width, length, level]: readonly [number, number, number],
  material: Material,
): Mesh {
  const sea = CreateGround('sea', { width, height: length, subdivisions: 1 }, scene);
  sea.position.y = level;
  sea.material = material;
  sea.isPickable = false;
  sea.receiveShadows = true;
  sea.alphaIndex = 0;
  return sea;
}

/**
 * The terrain chunk meshes made so far, and who wants to know about each new one (phase 10: a
 * glow layer hiding the lava under the hills).
 */
export class TerrainWatch {
  readonly #meshes: Mesh[] = [];
  readonly #watchers: ((mesh: Mesh) => void)[] = [];

  /** A new terrain chunk mesh. */
  add(mesh: Mesh): void {
    this.#meshes.push(mesh);
    for (const watch of this.#watchers) watch(mesh);
  }

  /** Calls `watch` with every mesh, now and as new ones are made. */
  watch(watch: (mesh: Mesh) => void): void {
    for (const mesh of this.#meshes) watch(mesh);
    this.#watchers.push(watch);
  }
}
