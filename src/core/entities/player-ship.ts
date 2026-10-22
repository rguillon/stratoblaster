/** Static, data-only description of a ship the player can fly. */
export interface PlayerShipDefinition {
  /** Stable identifier, also the key of the ship's model in the game view. */
  readonly id: string;
  /** Display name. */
  readonly name: string;
  /** Maximal speed as a multiple of {@link PlayerShipRoster.baseSpeedPxPerSec}. */
  readonly maxSpeedFactor: number;
  /** Maximal (and starting) health points. */
  readonly maxHealth: number;
}

/** All the ships a game offers to the player, with the speed they are relative to. */
export interface PlayerShipRoster {
  /** Speed of a ship whose `maxSpeedFactor` is 1, in logical pixels per second. */
  readonly baseSpeedPxPerSec: number;
  readonly ships: readonly PlayerShipDefinition[];
}

/** Returns the ship with the given id, or throws if the roster has none. */
export function findPlayerShip(roster: PlayerShipRoster, id: string): PlayerShipDefinition {
  const ship = roster.ships.find((s) => s.id === id);
  if (!ship) throw new Error(`Unknown player ship "${id}"`);
  return ship;
}

/** Maximal speed of a ship, in logical pixels per second. */
export function shipMaxSpeedPxPerSec(roster: PlayerShipRoster, id: string): number {
  return roster.baseSpeedPxPerSec * findPlayerShip(roster, id).maxSpeedFactor;
}

/** Throws a descriptive error if the roster is empty, has duplicate ids or invalid stats. */
export function validatePlayerShipRoster(roster: PlayerShipRoster): void {
  if (roster.ships.length === 0) throw new Error('A roster needs at least one player ship');
  if (!(roster.baseSpeedPxPerSec > 0)) throw new Error('The base speed must be positive');
  const ids = new Set<string>();
  for (const ship of roster.ships) {
    if (ids.has(ship.id)) throw new Error(`Duplicate player ship id "${ship.id}"`);
    ids.add(ship.id);
    if (!(ship.maxSpeedFactor > 0)) throw new Error(`Ship "${ship.id}": speed must be positive`);
    if (!Number.isInteger(ship.maxHealth) || ship.maxHealth <= 0) {
      throw new Error(`Ship "${ship.id}": health must be a positive integer`);
    }
  }
}
