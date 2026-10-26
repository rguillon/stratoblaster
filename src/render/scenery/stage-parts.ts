import type { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import type { Material } from '@babylonjs/core/Materials/material';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { SceneryLevel } from '../../core/scenery/scenery-level';

// Pieces of a `SceneryStage` that need nothing else of it.

/** Lowest ground of a level: its sea, or the lowest relief. */
export function lowestGround(level: SceneryLevel): number {
  const lows = level.sections.map((s) => s.relief.base - s.relief.amplitude);
  return level.sea ? level.sea.level : Math.min(...lows);
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
