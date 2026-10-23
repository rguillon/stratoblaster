import type { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { MenuScreen } from '../core/menu/menu-screen';
import type { BeamSegment } from '../core/systems/beam';
import type { Projectile } from '../core/systems/projectile-motion';
import type { ShotImpact } from '../core/systems/shot-world';
import type { PlayfieldCameraLook, PropModelFactory, SceneryLook } from './scenery/scenery-look';

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

/**
 * What a shot renderer draws on one frame. Shots live in the XY plane at Z = 0, one world unit
 * per logical pixel, Y up, seen from -Z. Ships are drawn around Z = 0: a renderer may draw at
 * Z > 0 to go under them (the playfield background is further back).
 */
export interface ShotFrame {
  /** Projectiles of this renderer's weapon that are in flight. */
  readonly projectiles: readonly Projectile[];
  /** Beam segments of this renderer's weapon (empty when it is not firing). */
  readonly beam: readonly BeamSegment[];
  /** Impacts of this renderer's weapon since the previous frame. */
  readonly impacts: readonly ShotImpact[];
  readonly dtSeconds: number;
}

/** Draws the shots of one weapon, frame after frame. */
export interface ShotRenderer {
  sync(frame: ShotFrame): void;
  dispose(): void;
}

/** Builds the renderer of one weapon's shots in `scene`. */
export type ShotRendererFactory = (scene: Scene) => ShotRenderer;

/** Presentation bindings a game provides to the engine (`GameDefinition.view`). */
export interface GameView {
  /** One model per player ship, keyed by `PlayerShipDefinition.id`. */
  readonly playerShipModels: Readonly<Record<string, ModelFactory>>;
  /** Logical pixels per model unit, to draw the player ships on the playfield. */
  readonly playerShipScale: number;
  /** One shot renderer per player weapon, keyed by `WeaponDefinition.id`. */
  readonly playerShotRenderers: Readonly<Record<string, ShotRendererFactory>>;
  /** 3D scene behind the menu screens (P01-R05). */
  readonly menuBackdrop: MenuBackdropFactory;
  /** How the generated levels look (P04). */
  readonly scenery: SceneryBindings;
}

/** Presentation of the levels with generated ground (`GameDefinition.sceneryLevels`). */
export interface SceneryBindings {
  readonly camera: PlayfieldCameraLook;
  /** One look per scenery level, keyed by `SceneryLevel.id`. */
  readonly looks: Readonly<Record<string, SceneryLook>>;
  /** One model per prop kind, keyed by `PropKindRule.id`. */
  readonly propModels: Readonly<Record<string, PropModelFactory>>;
}
