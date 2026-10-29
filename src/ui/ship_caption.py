"""Caption of a player ship's stats, ported from `ui/ship-caption.ts`."""

from org.transcrypt.stubs.browser import window

from core.entities.player_ship import (
    PlayerShipRoster,
    find_player_ship,
    ship_max_speed_px_per_sec,
)
from ui.caption_row import Caption


def ship_caption(roster: PlayerShipRoster, id: str, polygons: int | None = None) -> Caption:
    """Caption showing a player ship's name and stats, and its model's polygon count if given."""
    ship = find_player_ship(roster, id)
    px_per_sec = window.Math.round(ship_max_speed_px_per_sec(roster, id))
    lines = [
        "Speed ×" + str(ship.max_speed_factor) + " (" + str(px_per_sec) + " px/s)",
        "HP " + str(ship.max_health),
    ]
    if polygons is not None:
        lines.append(window.Number(polygons).toLocaleString("en-US") + " polygons")
    return Caption(ship.name, lines)
