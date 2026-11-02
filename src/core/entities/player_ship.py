# Copyright (c) 2026 Renaud Guillon
"""Static, data-only description of the ships the player can fly."""


class PlayerShipDefinition:
    """A ship the player can fly."""

    def __init__(self, id_: str, name: str, max_speed_factor: float, max_health: int) -> None:
        """`id` is the stable identifier, also the key of the ship's model in the game view.

        `name` the display name; `max_speed_factor` the maximal speed as a multiple of the roster's
        base speed; `max_health` the maximal (and starting) health points.
        """
        self.id = id_
        self.name = name
        self.max_speed_factor = max_speed_factor
        self.max_health = max_health


class PlayerShipRoster:
    """All the ships a game offers to the player, with the speed they are relative to."""

    def __init__(self, base_speed_px_per_sec: float, ships: list[PlayerShipDefinition]) -> None:
        """`base_speed_px_per_sec` is the speed of a ship whose `max_speed_factor` is 1.

        In logical pixels per second.
        """
        self.base_speed_px_per_sec = base_speed_px_per_sec
        self.ships = ships


def find_player_ship(roster: PlayerShipRoster, item_id: str) -> PlayerShipDefinition:
    """Return the ship with the given id, or raise if the roster has none."""
    for ship in roster.ships:
        if ship.id == item_id:
            return ship
    raise ValueError('Unknown player ship "' + item_id + '"')


def ship_max_speed_px_per_sec(roster: PlayerShipRoster, item_id: str) -> float:
    """Maximal speed of a ship, in logical pixels per second (GAME-SHIP-02)."""
    return roster.base_speed_px_per_sec * find_player_ship(roster, item_id).max_speed_factor
