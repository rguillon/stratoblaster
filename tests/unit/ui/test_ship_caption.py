"""Unit tests of `src/ui/ship_caption.py`."""

import pytest

from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from ui.ship_caption import ship_caption

ROSTER = PlayerShipRoster(
    100,
    [
        PlayerShipDefinition("alpha", "Alpha", 1.25, 5),
        PlayerShipDefinition("beta", "Beta", 0.8, 9),
    ],
)


def test_p01_r06_the_caption_names_the_ship_with_its_speed_and_health() -> None:
    caption = ship_caption(ROSTER, "alpha")
    assert caption.title == "Alpha"
    assert caption.lines == ["Speed ×1.25 (125 px/s)", "HP 5"]


def test_p01_r06_the_caption_gives_the_model_polygon_count_when_known() -> None:
    caption = ship_caption(ROSTER, "beta", 12345)
    assert caption.lines[-1] == "12,345 polygons"
    assert len(caption.lines) == 3


def test_p01_r06_an_unknown_ship_is_an_error() -> None:
    with pytest.raises(ValueError):
        ship_caption(ROSTER, "gamma")
