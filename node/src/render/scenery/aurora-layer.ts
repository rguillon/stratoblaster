import type { Scene } from '@babylonjs/core/scene';
import type { Material } from '@babylonjs/core/Materials/material';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Atmosphere } from '../../core/scenery/atmosphere';
import { BELOW_CLOUDS_GROUP } from './cloud-layers';
import type { GroundWindow } from './playfield-framing';

/** What the aurora shows on one frame. */
export interface AuroraFrame {
  readonly time: number;
  readonly strength: number;
  readonly cameraPosition: Vector3;
  readonly fog: { readonly start: number; readonly end: number };
}

/** The aurora's material, driven frame by frame. */
export interface AuroraMaterial {
  readonly material: Material;
  set(frame: AuroraFrame): void;
}

/** Draw order: after the clouds and the weather. */
const AURORA_ALPHA_INDEX = 5;

/**
 * An aurora (P08-R04, 2-5 at night): slow green and violet curtains added over the scene from
 * a sheet high above the ground, faint near the camera and strongest in the far haze at the top
 * of the screen. Shown only while the atmosphere has one; it never flashes.
 */
export class AuroraLayer {
  readonly mesh: Mesh;
  readonly #middle: number;

  constructor(
    scene: Scene,
    private readonly material: AuroraMaterial,
    [seen, altitude, margin]: readonly [GroundWindow, number, number],
  ) {
    this.mesh = CreateGround(
      'aurora',
      {
        width: 2 * (seen.halfWidth + margin),
        height: seen.zFar - seen.zNear + 2 * margin,
        subdivisions: 1,
      },
      scene,
    );
    this.mesh.position.y = altitude;
    this.mesh.material = material.material;
    this.mesh.isPickable = false;
    this.mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1;
    this.mesh.alphaIndex = AURORA_ALPHA_INDEX;
    this.mesh.setEnabled(false);
    this.#middle = (seen.zNear + seen.zFar) / 2;
  }

  /** Follows the camera and shows the aurora of `atmosphere`, if any. */
  update(atmosphere: Atmosphere, time: number, cameraPosition: Vector3): void {
    const strength = atmosphere.aurora;
    this.mesh.setEnabled(strength > 0);
    if (strength <= 0) return;
    this.mesh.position.z = cameraPosition.z + this.#middle;
    this.material.set({ time, strength, cameraPosition, fog: atmosphere.fog });
  }
}
