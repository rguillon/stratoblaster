import type { PlayerShipRoster } from '../entities/player-ship';
import type { WeaponDefinition } from '../entities/weapon';
import type { LevelCatalog } from './level-catalog';
import type { MenuTexts } from './menu-texts';

/** Logical resolution the game is laid out on, scaled to fit the window (GD-02). */
export interface LogicalScreen {
  readonly width: number;
  readonly height: number;
}

/**
 * Contract between the engine and a game built on it (ENG-144).
 * `src/game/index.ts` exports exactly one object of this type; the engine discovers
 * all game content through it. Phases extend this interface with registries
 * (entity factories, levels, view bindings, asset manifest...).
 *
 * `TView` holds the presentation bindings (meshes, materials...). Its shape is defined
 * by the presentation layers, so `core/` stays free of Babylon types.
 */
export interface GameDefinition<TView = unknown> {
  /** Stable identifier, used e.g. as a storage key prefix. */
  readonly id: string;
  /** Human-readable title shown by the engine. */
  readonly title: string;
  /** Logical resolution of the screens (GD-02). */
  readonly screen: LogicalScreen;
  /** The ships the player can fly (data only). The first one is selected by default. */
  readonly playerShips: PlayerShipRoster;
  /** The weapons every player ship can fire (data only). */
  readonly playerWeapons: readonly WeaponDefinition[];
  /** The levels shown on the level select screen, and which ones can be played. */
  readonly levels: LevelCatalog;
  /** Texts of the menu screens. */
  readonly texts: MenuTexts;
  /** Presentation bindings for the content above. */
  readonly view: TView;
}
