import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { LogicalScreen } from '../core/content/game-definition';
import type { ModelFactory } from '../render/game-view';
import { stepModelAnimations } from '../render/model-animation';
import { SHOT_VIEWER_CONFIG as CFG } from '../config/shot-viewer';

const CAMERA_DISTANCE = 500;

/**
 * A scene looking straight down on a `screen`-sized playfield: an orthographic camera shows
 * X in [0, width] and Y in [0, height] (one unit per logical pixel), from -Z.
 */
export function createPlayfieldScene(engine: AbstractEngine, screen: LogicalScreen): Scene {
  const scene = new Scene(engine);
  scene.clearColor = new Color4(...CFG.clearColor);
  const { width, height } = screen;
  const camera = new FreeCamera(
    'playfield-camera',
    new Vector3(width / 2, height / 2, -CAMERA_DISTANCE),
    scene,
  );
  camera.setTarget(new Vector3(width / 2, height / 2, 0));
  camera.mode = Camera.ORTHOGRAPHIC_CAMERA;
  camera.orthoLeft = -width / 2;
  camera.orthoRight = width / 2;
  camera.orthoBottom = -height / 2;
  camera.orthoTop = height / 2;
  camera.minZ = 1;
  camera.maxZ = CAMERA_DISTANCE * 2;
  const ambient = new HemisphericLight('playfield-ambient', new Vector3(0, 0, -1), scene);
  ambient.intensity = CFG.lights.ambientIntensity;
  const key = new DirectionalLight('playfield-key', new Vector3(...CFG.lights.keyDirection), scene);
  key.intensity = CFG.lights.keyIntensity;
  return scene;
}

/** A player ship lying on the playfield, nose up (+Y), top towards the camera. */
export class PlayfieldShip {
  readonly pivot: TransformNode;
  #model: TransformNode | undefined;

  constructor(
    private readonly scene: Scene,
    private readonly scale: number,
    x: number,
    y: number,
  ) {
    this.pivot = new TransformNode('playfield-ship', scene);
    this.pivot.position.set(x, y, 0);
  }

  /** Replaces the ship model and returns the height (Y) of its nose tip on the playfield. */
  show(factory: ModelFactory): number {
    this.#model?.dispose();
    // Models face +Z with +Y up: a holder turns the nose to +Y and the top to -Z (the camera).
    const holder = new TransformNode('playfield-ship-model', this.scene);
    holder.parent = this.pivot;
    holder.rotation.x = -Math.PI / 2;
    holder.scaling.setAll(this.scale);
    factory(this.scene).parent = holder;
    this.#model = holder;
    return this.#noseY(holder);
  }

  /** Highest point of the model's meshes, i.e. its nose tip (the pivot when it has none). */
  #noseY(holder: TransformNode): number {
    const nodes = [this.pivot, holder, ...holder.getDescendants(false)];
    // Parents come before their children, so each world matrix uses an up-to-date parent.
    for (const node of nodes) {
      if (node instanceof TransformNode) node.computeWorldMatrix(true);
    }
    let top = this.pivot.position.y;
    for (const mesh of holder.getChildMeshes(false)) {
      if (mesh.getTotalVertices() > 0) {
        top = Math.max(top, mesh.getBoundingInfo().boundingBox.maximumWorld.y);
      }
    }
    return top;
  }

  update(dt: number): void {
    if (this.#model) stepModelAnimations(this.#model, dt);
  }
}
