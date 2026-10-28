import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { newer } from '../node-adopter';
import { visibleGround, type GroundWindow, type PlayfieldFraming } from './playfield-framing';
import type { SceneryStageOptions } from './scenery-stage-options';
import { lowestGround } from './stage-parts';
import type { GroundTransform } from './scenery-kit';

/**
 * The node the ground hangs from, drawn `scale` times as big as it is, as if flying lower
 * (`PlayfieldCameraLook.groundScale`). As the view moves `distance` along the level, the node is
 * moved so the ground point under the view is still `distance` in: the level covers the same
 * ground a second, which passes `scale` times as fast.
 */
export class GroundRoot {
  readonly node: TransformNode;

  constructor(
    private readonly scene: Scene,
    readonly scale: number,
  ) {
    this.node = new TransformNode('ground-root', scene);
    this.node.scaling.setAll(scale);
  }

  /** Runs `create`, then hangs what it made from the ground (but what has a parent already). */
  adopt<T>(create: () => T): T {
    const before = this.scene.getUniqueId();
    try {
      return create();
    } finally {
      for (const node of newer(this.scene.transformNodes, before)) this.#hang(node);
      for (const mesh of newer(this.scene.meshes, before)) this.#hang(mesh);
    }
  }

  /** Moves the ground for the view `distance` along the level. */
  moveTo(distance: number): void {
    this.node.position.z = (1 - this.scale) * distance;
  }

  /** The ground Z drawn at world Z `z`. */
  toGround(z: number): number {
    return (z - this.node.position.z) / this.scale;
  }

  /** The world Z where ground Z `z` is drawn. */
  toWorld(z: number): number {
    return z * this.scale + this.node.position.z;
  }

  /** What the terrain's material needs to know (`SceneryKitFrame.ground`). */
  get transform(): GroundTransform {
    return { scale: this.scale, offsetZ: this.node.position.z };
  }

  #hang(node: TransformNode): void {
    if (node.parent === null && node !== this.node) node.parent = this.node;
  }
}

/**
 * The ground the camera sees over a level (relative to the camera's ground Z, in ground units)
 * when the ground is drawn `scale` times as big.
 */
export function groundWindowOf(
  { screen, camera, level }: Pick<SceneryStageOptions, 'screen' | 'camera' | 'level'>,
  framing: PlayfieldFraming,
  scale: number,
): GroundWindow {
  const world = visibleGround(
    framing,
    screen.width / screen.height,
    camera.flightAltitude + framing.height,
    lowestGround(level) * scale,
    camera.flightAltitude,
  );
  return {
    zNear: world.zNear / scale,
    zFar: world.zFar / scale,
    halfWidth: world.halfWidth / scale,
  };
}
