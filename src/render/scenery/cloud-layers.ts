import type { Scene } from '@babylonjs/core/scene';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { Atmosphere, CloudCover } from '../../core/scenery/atmosphere';
import type { GroundWindow } from './playfield-framing';
import type { CloudMaterial } from './scenery-kit';
import type { CloudLayerLook } from './scenery-look';

/** Group of all but the clouds, drawn next: a glow composed after it stays under them. */
export const BELOW_CLOUDS_GROUP = 0;
/**
 * Group of what flies above the clouds (the ships), drawn last and keeping the depth: neither the
 * clouds nor a glow composed after the ground draw over it (phase 4 review).
 */
export const ABOVE_CLOUDS_GROUP = BELOW_CLOUDS_GROUP + 2;

/** A cloud layer's live settings (P04-R03). */
export interface CloudLayerState {
  enabled: boolean;
  coverage: number;
  opacity: number;
}

export interface CloudLayer {
  readonly look: CloudLayerLook;
  /** Z of the middle of what the camera sees at the layer's altitude, relative to the camera. */
  readonly middle: number;
  readonly mesh: Mesh;
  readonly material: CloudMaterial;
  readonly state: CloudLayerState;
}

/**
 * Cloud layer number `index` (P04-R03): a plane at `altitude` covering what the camera sees
 * there (`seen`) and `margin` more, drawn after everything else.
 */
export function buildCloudLayer(
  scene: Scene,
  look: CloudLayerLook,
  material: CloudMaterial,
  index: number,
  [seen, altitude, margin]: readonly [GroundWindow, number, number],
): CloudLayer {
  const mesh = CreateGround(
    `cloud-layer-${String(index)}`,
    {
      width: 2 * (seen.halfWidth + margin),
      height: seen.zFar - seen.zNear + 2 * margin,
      subdivisions: 1,
    },
    scene,
  );
  mesh.position.y = altitude;
  mesh.material = material.material;
  mesh.isPickable = false;
  mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
  // Lower layers are drawn first, after the sea.
  mesh.alphaIndex = index + 1;
  return {
    look,
    middle: (seen.zNear + seen.zFar) / 2,
    mesh,
    material,
    state: { enabled: true, coverage: look.coverage, opacity: look.opacity },
  };
}

/**
 * Follows the camera at `cameraZ`, drifts with `time`, and takes the colours of `cover` and the
 * haze of `atmosphere` (P08-R04); its coverage and opacity too when `follow` (a level whose look
 * changes), otherwise they stay as set on its state (set by code).
 */
export function updateCloudLayer(
  layer: CloudLayer,
  [cameraZ, time]: readonly [number, number],
  [atmosphere, cover, follow]: readonly [Atmosphere, CloudCover | undefined, boolean],
): void {
  const { look, mesh, material, state } = layer;
  if (follow && cover) {
    state.coverage = cover.coverage;
    state.opacity = cover.opacity;
  }
  mesh.position.z = cameraZ + layer.middle;
  const visible = state.enabled && state.coverage > 0 && state.opacity > 0;
  mesh.setEnabled(visible);
  material.set({
    coverage: state.coverage,
    opacity: state.opacity,
    offsetX: look.drift[0] * time,
    offsetZ: look.drift[1] * time,
    color: cover?.color ?? look.color,
    shade: cover?.shade ?? look.shade,
    fog: { color: atmosphere.sky.haze, ...atmosphere.fog },
  });
}
