import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Enemy } from '../core/entities/enemy';
import type { EnemyModel, EnemyModelFactory } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { ENEMY_VIEWER_CONFIG } from '../config/enemy-viewer';
import { SHIP_VIEWER_CONFIG } from '../config/ship-viewer';

const CFG = ENEMY_VIEWER_CONFIG.closeUp;

/**
 * The model view of the enemies page (P05-R11, phase 5 review): like `player_ship/`, one enemy
 * model alone on a dark background, turning, with the camera close up on it. Drag to orbit,
 * wheel to zoom; the arrow keys are left to the page (they switch the enemy).
 */
export class EnemyCloseUp {
  readonly scene: Scene;
  readonly camera: ArcRotateCamera;
  /** Turns the model around its vertical axis. */
  readonly pivot: TransformNode;
  #model: EnemyModel | undefined;
  #enemy: Enemy | undefined;

  constructor(
    engine: AbstractEngine,
    environment: boolean,
    glow: { readonly intensity: number; readonly blurKernelSize: number },
  ) {
    const look = SHIP_VIEWER_CONFIG;
    this.scene = new Scene(engine);
    this.scene.clearColor = new Color4(...look.clearColor);
    const { horizontalFov } = look.camera;
    this.camera = new ArcRotateCamera(
      'close-up-camera',
      CFG.alpha,
      CFG.beta,
      1,
      Vector3.Zero(),
      this.scene,
    );
    this.camera.fovMode = Camera.FOVMODE_HORIZONTAL_FIXED;
    this.camera.fov = horizontalFov;
    this.camera.inputs.removeByType('ArcRotateCameraKeyboardMoveInput');
    if (engine.getRenderingCanvas()) this.camera.attachControl(true);
    const { lights } = look;
    new HemisphericLight('close-up-ambient', Vector3.Up(), this.scene).intensity =
      lights.ambientIntensity;
    const key = new DirectionalLight(
      'close-up-key',
      new Vector3(...lights.keyDirection),
      this.scene,
    );
    key.intensity = lights.keyIntensity;
    const rim = new DirectionalLight(
      'close-up-rim',
      new Vector3(...lights.rimDirection),
      this.scene,
    );
    rim.intensity = lights.rimIntensity;
    if (environment) applyShowcaseEnvironment(this.scene, { ...look.environment, glow });
    this.pivot = new TransformNode('close-up-pivot', this.scene);
  }

  /** Replaces the model with `build`'s, its lights fully charged, and frames it. */
  show(build: EnemyModelFactory, enemy: Enemy): void {
    this.#model?.root.dispose();
    this.#model = build(this.scene);
    // Measured before it joins the turning pivot, in its own axes.
    this.#frame(this.#model.root);
    this.#model.root.parent = this.pivot;
    this.#enemy = enemy;
    enemy.charge = 1;
    this.#model.sync(enemy, 0);
  }

  /** Puts the camera at the distance where the model fills `CFG.fill` of the screen width. */
  #frame(root: TransformNode): void {
    root.computeWorldMatrix(true);
    const { min, max } = root.getHierarchyBoundingVectors(true);
    const size = Math.max(max.x - min.x, max.z - min.z, 1);
    const radius = size / 2 / CFG.fill / Math.tan(this.camera.fov / 2);
    // Keeps the camera's angles (and radius, set right after) when moving its target.
    this.camera.setTarget(new Vector3(0, (min.y + max.y) / 2, 0), false, false, true);
    this.camera.lowerRadiusLimit = radius * CFG.zoom[0];
    this.camera.upperRadiusLimit = radius * CFG.zoom[1];
    this.camera.radius = radius;
    this.camera.minZ = radius / 100;
  }

  update(dt: number): void {
    this.pivot.rotation.y += CFG.spinRadPerSec * dt;
    if (this.#model && this.#enemy) this.#model.sync(this.#enemy, dt);
  }

  dispose(): void {
    this.scene.dispose();
  }
}
