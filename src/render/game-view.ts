import type { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';

/**
 * Builds a model in the scene and returns its root node. Models face +Z (nose),
 * with +Y up, and are centred on the origin.
 */
export type ModelFactory = (scene: Scene) => TransformNode;

/** Presentation bindings a game provides to the engine (`GameDefinition.view`). */
export interface GameView {
  /** One model per player ship, keyed by `PlayerShipDefinition.id`. */
  readonly playerShipModels: Readonly<Record<string, ModelFactory>>;
}
