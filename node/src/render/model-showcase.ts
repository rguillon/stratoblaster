import type { Scene } from '@babylonjs/core/scene';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { ModelFactory } from './game-view';
import { stepModelAnimations } from './model-animation';

/** Layout and animation settings of a {@link ModelShowcase}. */
export interface ShowcaseOptions {
  /** Distance between the centres of two neighbouring models, in world units. */
  readonly spacing: number;
  readonly rotationSpeedRadPerSec: number;
}

/**
 * Shows models side by side along X, each one spinning around its vertical axis. Model
 * animations (`addModelAnimation`) are stepped with the rotation.
 */
export class ModelShowcase {
  /** One pivot per model, left to right; each model is the only child of its pivot. */
  readonly pivots: readonly TransformNode[];
  /** Distance from the leftmost to the rightmost model edge slot, in world units. */
  readonly width: number;
  readonly #rotationSpeed: number;

  constructor(scene: Scene, factories: readonly ModelFactory[], options: ShowcaseOptions) {
    this.#rotationSpeed = options.rotationSpeedRadPerSec;
    this.width = factories.length * options.spacing;
    const offset = ((factories.length - 1) * options.spacing) / 2;
    this.pivots = factories.map((build, i) => {
      const pivot = new TransformNode(`showcase-pivot-${String(i)}`, scene);
      pivot.position.x = i * options.spacing - offset;
      build(scene).parent = pivot;
      return pivot;
    });
  }

  /** Advances the rotation and the model animations by `dtSeconds`. */
  update(dtSeconds: number): void {
    for (const pivot of this.pivots) {
      pivot.rotation.y += this.#rotationSpeed * dtSeconds;
      stepModelAnimations(pivot, dtSeconds);
    }
  }

  dispose(): void {
    for (const pivot of this.pivots) pivot.dispose();
  }
}
