# Copyright (c) 2026 Renaud Guillon
"""Caption of a player ship's stats (UI-SHIP-02)."""

from org.transcrypt.stubs.browser import window

from core.entities.player_ship import PlayerShipRoster, find_player_ship
from ui.caption_row import Caption


def speed_word(factor: float) -> str:
    """Return the ship's speed in a plain word, from its factor of the base speed (UI-SHIP-02)."""
    if factor < 1:
        return "slow"
    if factor > 1:
        return "fast"
    return "normal"


def ship_caption(roster: PlayerShipRoster, ship_id: str, polygons: int | None = None) -> Caption:
    """Caption showing a player ship's name and stats, and its model's polygon count if given."""
    ship = find_player_ship(roster, ship_id)
    lines = [
        "Speed: " + speed_word(ship.max_speed_factor),
        "HP " + str(ship.max_health),
    ]
    if polygons is not None:
        lines.append(window.Number(polygons).toLocaleString("en-US") + " polygons")
    return Caption(ship.name, lines)
