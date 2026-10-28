import type { Scene } from '@babylonjs/core/scene';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { Enemy } from '../core/entities/enemy';
import type { MenuScreen } from '../core/menu/menu-screen';
import type { EnemyBullet, EnemyLaser, EnemyMissile } from '../core/systems/enemy-shots';
import type { Bonus } from '../core/systems/bonus-world';
import type { ActiveBomb } from '../core/systems/player-bombs';
import type { EnemyBlast } from '../core/systems/enemy-world';
import type { BeamSegment } from '../core/systems/beam';
import type { Projectile } from '../core/systems/projectile-motion';
import type { ShotImpact } from '../core/systems/shot-world';
import type { AudioBindings } from '../audio/audio-bindings';
import type { OutlineLook } from './outline';
import type { TileRules } from '../core/scenery/scenery-level';
import type { TileRoadLook } from './scenery/tile-road-geometry';
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
  /** How the enemies, their shots and their explosions look (P05). */
  readonly enemies: EnemyBindings;
  /** How the weapon bonuses look (phase 6 review). */
  readonly bonuses: (scene: Scene) => BonusRenderer;
  /** Draws the player's bombs going off (P11-R05). None drawn when omitted. */
  readonly bombs?: (scene: Scene) => BombRenderer;
  /** The game's generated music and sound effects (P12-R05..R10). Silent when omitted. */
  readonly audio?: AudioBindings;
  /**
   * Phase 14 (P14-R03, R04): how the rim glows round the playfield meshes that ask for one
   * (`setOutline`) look. No rim glows when omitted.
   */
  readonly outline?: OutlineLook;
  /**
   * Phase 14 (P14-R03): a marker on the player ship's hitbox centre, `radius` the hitbox's,
   * drawn over the ship. None when omitted.
   */
  readonly hitboxMarker?: ModelFactoryOf<number>;
}

/** Builds a model in the scene from a value (e.g. a size) and returns its root node. */
export type ModelFactoryOf<T> = (scene: Scene, value: T) => TransformNode;

/** What the bomb renderer draws on one frame, in playfield space (P11-R05). */
export interface BombFrame {
  /** The bomb going off, if any. */
  readonly bomb: ActiveBomb | undefined;
  readonly dtSeconds: number;
}

/** Draws a bomb going off: a shockwave from the ship over the playfield, and a flash. */
export interface BombRenderer {
  sync(frame: BombFrame): void;
  dispose(): void;
}

/** What the bonus renderer draws on one frame, in playfield space (see {@link ShotFrame}). */
export interface BonusFrame {
  readonly bonuses: readonly Bonus[];
  /** Bonuses picked up since the previous frame, where they were. */
  readonly picked: readonly Bonus[];
  readonly dtSeconds: number;
}

/** Draws the bonuses falling (each kind its own look, P11-R07), and a flash where the ship picks one up. */
export interface BonusRenderer {
  sync(frame: BonusFrame): void;
  dispose(): void;
}

/**
 * The model of one enemy. It is built facing +Z with +Y up, centred on the origin, in logical
 * pixels; the engine turns it onto the playfield and along the enemy's heading.
 */
export interface EnemyModel {
  readonly root: TransformNode;
  /** Shows the enemy's state (e.g. `charge`) and steps the model's animations. */
  sync(enemy: Enemy, dtSeconds: number): void;
}

/** Builds one enemy model in `scene`. */
export type EnemyModelFactory = (scene: Scene) => EnemyModel;

/** What the enemy shot renderer draws on one frame, in playfield space (see {@link ShotFrame}). */
export interface EnemyShotFrame {
  /** Bullets and missiles in flight. */
  readonly bullets: readonly EnemyBullet[];
  readonly missiles: readonly EnemyMissile[];
  /** Lasers, in their warning or firing phase. */
  readonly lasers: readonly EnemyLaser[];
  readonly dtSeconds: number;
}

/** Draws the enemies' shots, frame after frame. */
export interface EnemyShotRenderer {
  sync(frame: EnemyShotFrame): void;
  dispose(): void;
}

/** Draws explosions where enemies and missiles were destroyed (GD-62), frame after frame. */
export interface BlastRenderer {
  /** `blasts` are the new ones since the previous frame. */
  sync(blasts: readonly EnemyBlast[], dtSeconds: number): void;
  dispose(): void;
}

/** Presentation of the enemies (`GameDefinition.enemyKinds`). */
export interface EnemyBindings {
  /** One model per `EnemyStats.model` key. */
  readonly models: Readonly<Record<string, EnemyModelFactory>>;
  /**
   * The enemy shot renderer, drawing in the level's `style` if any (phase 10: a style a level's
   * look names, `SceneryLook.shotStyle`).
   */
  readonly shots: (scene: Scene, style?: string) => EnemyShotRenderer;
  readonly blasts: (scene: Scene) => BlastRenderer;
  /** Glow of the self-lit parts drawn on the playfield (neon, shots). */
  readonly glow: { readonly intensity: number; readonly blurKernelSize: number };
}

/** Presentation of the levels with generated ground (`GameDefinition.sceneryLevels`). */
export interface SceneryBindings {
  readonly camera: PlayfieldCameraLook;
  /** One look per scenery level, keyed by `SceneryLevel.id`. */
  readonly looks: Readonly<Record<string, SceneryLook>>;
  /** One model per prop kind, keyed by `PropKindRule.id`. */
  readonly propModels: Readonly<Record<string, PropModelFactory>>;
  /** How the `props/` page groups the prop models (all in one group when omitted). */
  readonly propGroups?: readonly PropGroup[];
  /** The grid of tiles of the `props/` page's ground, and how its road tiles look. */
  readonly propTiles?: { readonly tile: TileRules; readonly look: TileRoadLook };
}

/** A named group of prop model ids, shown together on the `props/` page. */
export interface PropGroup {
  readonly label: string;
  readonly ids: readonly string[];
  /** Phase 15: a note shown after some ids' names, e.g. the tiles they stand on (`3×4`). */
  readonly notes?: Readonly<Record<string, string>>;
  /** Whether the props stand in blocks ringed by road tiles (the models made for the grid). */
  readonly streets?: boolean;
}
