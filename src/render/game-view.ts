import type { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { MenuScreen } from '../core/menu/menu-screen';

/**
 * Builds a model in the scene and returns its root node. Models face +Z (nose),
 * with +Y up, and are centred on the origin.
 */
export type ModelFactory = (scene: Scene) => TransformNode;

/** The animated 3D scene behind the menus, built by the game. */
export interface MenuBackdrop {
  /** Advances the animation by `dtSeconds`. */
  update(dtSeconds: number): void;
  /** Called when the menu screen changes, e.g. to hide parts that a screen draws itself. */
  showScreen(screen: MenuScreen): void;
  /** Self-lit meshes (sky, sun...) that must not bloom in the glow layer. */
  readonly glowExcludedMeshes: readonly Mesh[];
}

/** Fills `scene` (meshes, camera, fog, clear colour) with the game's menu backdrop. */
export type MenuBackdropFactory = (scene: Scene) => MenuBackdrop;

/** Presentation bindings a game provides to the engine (`GameDefinition.view`). */
export interface GameView {
  /** One model per player ship, keyed by `PlayerShipDefinition.id`. */
  readonly playerShipModels: Readonly<Record<string, ModelFactory>>;
  /** 3D scene behind the menu screens (P01-R05). */
  readonly menuBackdrop: MenuBackdropFactory;
}
