import type { Scene } from '@babylonjs/core/scene';
import type { Camera } from '@babylonjs/core/Cameras/camera';
import { Constants } from '@babylonjs/core/Engines/constants';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { CreatePlane } from '@babylonjs/core/Meshes/Builders/planeBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { BELOW_CLOUDS_GROUP } from './cloud-layers';

type Rgb = readonly [number, number, number];

/** A veil over the background: its colour, and how much of what is behind it it covers (0..1). */
export interface VeilLook {
  readonly color: Rgb;
  readonly opacity: number;
}

/** How far in front of the camera the veil hangs, as a multiple of its near plane. */
const DISTANCE = 2;
/** Margin round the view, so no edge shows whatever the aspect ratio. */
const MARGIN = 4;

/**
 * A screen-wide veil laid over the ground, the sky and the clouds, under the playfield (phase
 * 14, P14-R01): it darkens the background and pulls its colours towards `look.color`, so the
 * ships and shots drawn above it stand out. It hangs in front of `camera` and moves with it.
 */
export function addBackgroundVeil(scene: Scene, camera: Camera, look: VeilLook): Mesh {
  const distance = camera.minZ * DISTANCE;
  const size = 2 * distance * Math.tan(camera.fov / 2) * MARGIN;
  const veil = CreatePlane('background-veil', { size }, scene);
  veil.parent = camera;
  veil.position.set(0, 0, distance);
  const material = new StandardMaterial('background-veil', scene);
  material.emissiveColor = new Color3(...look.color);
  material.diffuseColor = Color3.Black();
  material.specularColor = Color3.Black();
  material.disableLighting = true;
  material.alpha = look.opacity;
  material.disableDepthWrite = true;
  material.depthFunction = Constants.ALWAYS;
  material.backFaceCulling = false;
  veil.material = material;
  // After the clouds, the weather and the lightning (the last group under the playfield).
  veil.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
  veil.alphaIndex = Number.MAX_SAFE_INTEGER;
  veil.isPickable = false;
  veil.alwaysSelectAsActiveMesh = true;
  return veil;
}
