/**
 * Contract between the engine and a game built on it (ENG-144).
 * `src/game/index.ts` exports exactly one object of this type; the engine discovers
 * all game content through it. Phases extend this interface with registries
 * (entity factories, levels, view bindings, asset manifest...).
 */
export interface GameDefinition {
  /** Stable identifier, used e.g. as a storage key prefix. */
  readonly id: string;
  /** Human-readable title shown by the engine. */
  readonly title: string;
}
