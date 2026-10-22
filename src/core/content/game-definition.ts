import type { PlayerShipRoster } from '../entities/player-ship';

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
  /** The ships the player can fly (data only). */
  readonly playerShips: PlayerShipRoster;
  /** Presentation bindings for the content above. */
  readonly view: TView;
}
