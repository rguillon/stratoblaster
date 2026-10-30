import type { Scene } from '@babylonjs/core/scene';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera';
import { Camera } from '@babylonjs/core/Cameras/camera';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { CreateTorus } from '@babylonjs/core/Meshes/Builders/torusBuilder';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { ModelFactory } from './game-view';
import { ModelShowcase } from './model-showcase';

type Vec3 = readonly [number, number, number];

/** Layout and look of a {@link ShipSelectStage}. */
export interface ShipSelectStageOptions {
  readonly spacing: number;
  readonly rotationSpeedRadPerSec: number;
  readonly highlightScale: number;
  readonly dimScale: number;
  readonly scaleEasePerSec: number;
  readonly camera: {
    readonly alpha: number;
    readonly beta: number;
    readonly horizontalFov: number;
    readonly framingMargin: number;
    readonly targetY: number;
  };
  readonly lights: {
    readonly ambientIntensity: number;
    readonly spotIntensity: number;
    readonly spotDirection: Vec3;
    readonly rimIntensity: number;
    readonly rimDirection: Vec3;
  };
  readonly ring: {
    readonly diameter: number;
    readonly thickness: number;
    readonly y: number;
    readonly color: Vec3;
  };
}

/**
 * The 3D part of the ship select screen (P01-R06): the ships side by side, rotating. The
 * highlighted ship is scaled up, lit by its own key light and sits on a neon ring; the
 * others are smaller and only get the ambient light.
 */
export class ShipSelectStage {
  readonly showcase: ModelShowcase;
  readonly camera: ArcRotateCamera;
  /** Each ship's key light, lighting only that ship; only the highlighted one is on. */
  readonly #spots: DirectionalLight[];
  readonly ring: Mesh;
  #selected = 0;

  constructor(
    readonly scene: Scene,
    factories: readonly ModelFactory[],
    private readonly options: ShipSelectStageOptions,
  ) {
    this.showcase = new ModelShowcase(scene, factories, options);
    this.camera = this.#createCamera();
    const { lights } = options;
    new HemisphericLight('ship-select-ambient', Vector3.Up(), scene).intensity =
      lights.ambientIntensity;
    const rim = new DirectionalLight('ship-select-rim', new Vector3(...lights.rimDirection), scene);
    rim.intensity = lights.rimIntensity;
    // P13-R02: one light per ship, so highlighting another ship only turns lights on and off:
    // no mesh's lights change, and no shader is compiled again.
    this.#spots = this.showcase.pivots.map((pivot, i) => {
      const spot = new DirectionalLight(
        `ship-select-spot-${String(i)}`,
        new Vector3(...lights.spotDirection),
        scene,
      );
      spot.includedOnlyMeshes = pivot.getChildMeshes(false);
      spot.intensity = 0;
      return spot;
    });
    this.ring = this.#createRing();
    this.select(0);
    for (const pivot of this.showcase.pivots) pivot.scaling.setAll(this.#targetScale(pivot));
  }

  /** The key light of the highlighted ship. */
  get spot(): DirectionalLight {
    const spot = this.#spots[this.#selected];
    if (!spot) throw new Error('The ship select stage has no ship');
    return spot;
  }

  /** Index of the highlighted ship. */
  get selected(): number {
    return this.#selected;
  }

  /** Highlights ship `index` (clamped to the available ships). */
  select(index: number): void {
    const pivots = this.showcase.pivots;
    this.#selected = Math.min(Math.max(0, index), pivots.length - 1);
    const pivot = pivots[this.#selected];
    if (!pivot) return;
    this.#spots.forEach((spot, i) => {
      spot.intensity = i === this.#selected ? this.options.lights.spotIntensity : 0;
    });
    this.ring.position.x = pivot.position.x;
  }

  /** Rotates the ships and eases their scales towards the highlight state. */
  update(dtSeconds: number): void {
    this.showcase.update(dtSeconds);
    const ease = 1 - Math.exp(-this.options.scaleEasePerSec * dtSeconds);
    for (const pivot of this.showcase.pivots) {
      const current = pivot.scaling.x;
      pivot.scaling.setAll(current + (this.#targetScale(pivot) - current) * ease);
    }
  }

  #targetScale(pivot: TransformNode): number {
    const isSelected = this.showcase.pivots[this.#selected] === pivot;
    return isSelected ? this.options.highlightScale : this.options.dimScale;
  }

  #createCamera(): ArcRotateCamera {
    const { alpha, beta, horizontalFov, framingMargin, targetY } = this.options.camera;
    const radius = ((this.showcase.width / 2) * framingMargin) / Math.tan(horizontalFov / 2);
    const target = new Vector3(0, targetY, 0);
    const camera = new ArcRotateCamera(
      'ship-select-camera',
      alpha,
      beta,
      radius,
      target,
      this.scene,
    );
    camera.fovMode = Camera.FOVMODE_HORIZONTAL_FIXED;
    camera.fov = horizontalFov;
    return camera;
  }

  #createRing(): Mesh {
    const { diameter, thickness, y, color } = this.options.ring;
    const ring = CreateTorus(
      'ship-select-ring',
      { diameter, thickness, tessellation: 48 },
      this.scene,
    );
    ring.position.y = y;
    const mat = new StandardMaterial('ship-select-ring', this.scene);
    mat.emissiveColor = new Color3(...color);
    mat.diffuseColor = Color3.Black();
    mat.specularColor = Color3.Black();
    mat.disableLighting = true;
    ring.material = mat;
    return ring;
  }
}
