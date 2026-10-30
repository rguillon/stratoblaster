import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { CreateLines } from '@babylonjs/core/Meshes/Builders/linesBuilder';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { GlowLayer } from '@babylonjs/core/Layers/glowLayer';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Enemy } from '../core/entities/enemy';
import type { EnemyModel, EnemyModelFactory } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { ENEMY_VIEWER_CONFIG } from '../config/enemy-viewer';
import { SHIP_VIEWER_CONFIG } from '../config/ship-viewer';

const CFG = ENEMY_VIEWER_CONFIG.closeUp;

/**
 * A hit circle drawn in the wireframe view: its centre as an offset from the enemy's centre on
 * the playfield (X right, Y up), its radius and colour. For a boss, one per part and its core.
 */
export interface HitCircle {
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  readonly color: readonly [number, number, number];
}

/**
 * The model view of the enemies page (P05-R11, phase 5 review): like `player_ship/`, one enemy
 * model alone on a dark background, turning, with the camera close up on it. Drag to orbit,
 * wheel to zoom; the arrow keys are left to the page (they switch the enemy). In the wireframe
 * view (phase 5 review) it draws the model's edges, the hull's in a light unlit colour so they
 * show, and the enemy's hit circle.
 */
export class EnemyCloseUp {
  readonly scene: Scene;
  readonly camera: ArcRotateCamera;
  /** Turns the model around its vertical axis. */
  readonly pivot: TransformNode;
  #model: EnemyModel | undefined;
  #enemy: Enemy | undefined;
  #circles: readonly HitCircle[] | undefined;
  #warmed = false;
  #build: EnemyModelFactory | undefined;
  #wireframe = false;
  #hitbox = false;
  readonly #glow: GlowLayer | undefined;
  /** The hull's wireframe colour: light and unlit, as the dark lit metal is hard to see. */
  readonly #wire: StandardMaterial;

  constructor(
    engine: AbstractEngine,
    environment: boolean,
    glow: { readonly intensity: number; readonly blurKernelSize: number },
  ) {
    const look = SHIP_VIEWER_CONFIG;
    this.scene = new Scene(engine);
    this.scene.clearColor = new Color4(...CFG.clearColor);
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
    if (environment)
      this.#glow = applyShowcaseEnvironment(this.scene, { ...look.environment, glow });
    this.pivot = new TransformNode('close-up-pivot', this.scene);
    this.#wire = new StandardMaterial('close-up-wire', this.scene);
    this.#wire.emissiveColor = new Color3(...CFG.wireColor);
    this.#wire.disableLighting = true;
  }

  /** P16-R10: whether the hit circles are drawn over the model in the model view too. */
  get hitbox(): boolean {
    return this.#hitbox;
  }

  set hitbox(on: boolean) {
    if (on === this.#hitbox) return;
    this.#hitbox = on;
    if (this.#build && this.#enemy) this.show(this.#build, this.#enemy, this.#circles);
  }

  get wireframe(): boolean {
    return this.#wireframe;
  }

  /** Switches the wireframe view on or off, building the model again for it. */
  set wireframe(on: boolean) {
    if (on === this.#wireframe) return;
    this.#wireframe = on;
    this.scene.forceWireframe = on;
    if (this.#build && this.#enemy) this.show(this.#build, this.#enemy, this.#circles);
  }

  /**
   * Replaces the model with `build`'s, its lights fully charged, and frames it. The wireframe
   * view draws `circles`; when omitted, the circles of what can be hit of the enemy (its own,
   * and those of its moving parts, P05-R24), from its centre.
   */
  show(build: EnemyModelFactory, enemy: Enemy, circles?: readonly HitCircle[]): void {
    this.#model?.root.dispose();
    this.#model = build(this.scene);
    this.#build = build;
    this.#circles = circles;
    const own = enemy.hitTargets.map((t): HitCircle => ({
      x: t.x - enemy.x,
      y: t.y - enemy.y,
      radius: t.radius,
      color: CFG.hitboxColor,
    }));
    if (this.#wireframe) this.#showWires(this.#model.root);
    if (this.#wireframe || this.#hitbox) this.#showCircles(this.#model.root, circles ?? own);
    // Measured before it joins the turning pivot, in its own axes.
    this.#frame(this.#model.root);
    this.#model.root.parent = this.pivot;
    this.#enemy = enemy;
    enemy.charge = 1;
    this.#model.sync(enemy, 0);
    if (!this.#warmed) {
      this.#warmed = true;
      // Compiles the scene's shaders in the background, before it is first drawn: entering the
      // model view would otherwise stall for as long as they take (seconds on a software GPU).
      void this.scene.whenReadyAsync();
    }
  }

  /** Hull edges in the light wire colour, without glow. */
  #showWires(root: TransformNode): void {
    for (const mesh of root.getChildMeshes<Mesh>()) {
      if (!CFG.bodyMaterials.includes(mesh.material?.name ?? '')) continue;
      mesh.material = this.#wire;
      mesh.useVertexColors = false;
      this.#glow?.addExcludedMesh(mesh);
    }
  }

  /** The hit circles around the model. */
  #showCircles(root: TransformNode, circles: readonly HitCircle[]): void {
    const n = CFG.hitboxSegments;
    circles.forEach(({ x, y, radius, color }, k) => {
      // Model space: the nose (+Z) points down the screen, so the playfield's (x, y) is (-x, -y).
      const points = Array.from({ length: n + 1 }, (_, i) => {
        const a = (2 * Math.PI * i) / n;
        return new Vector3(-x + Math.sin(a) * radius, 0, -y + Math.cos(a) * radius);
      });
      const hitbox = CreateLines(`close-up-hitbox-${String(k)}`, { points }, this.scene);
      hitbox.color = new Color3(...color);
      hitbox.parent = root;
    });
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
