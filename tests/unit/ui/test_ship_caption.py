# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/ship_caption.py`."""

import pytest

from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from ui.ship_caption import ship_caption, speed_word

ROSTER = PlayerShipRoster(
    100,
    [
        PlayerShipDefinition("alpha", "Alpha", 1.25, 5),
        PlayerShipDefinition("beta", "Beta", 0.8, 9),
    ],
)


def test_ui_ship_02_the_caption_names_the_ship_with_its_speed_and_health() -> None:
    caption = ship_caption(ROSTER, "alpha")
    assert caption.title == "Alpha"
    assert caption.lines == ["Speed: fast", "HP 5"]


@pytest.mark.parametrize(("factor", "word"), [(0.8, "slow"), (1, "normal"), (1.4, "fast")])
def test_ui_ship_02_the_speed_is_a_plain_word(factor: float, word: str) -> None:
    """D-323: slow under the base speed, normal at it, fast over it."""
    assert speed_word(factor) == word


def test_ui_ship_02_the_caption_gives_the_model_polygon_count_when_known() -> None:
    caption = ship_caption(ROSTER, "beta", 12345)
    assert caption.lines[-1] == "12,345 polygons"
    assert len(caption.lines) == 3


def test_ui_ship_02_an_unknown_ship_is_an_error() -> None:
    with pytest.raises(ValueError, match="Unknown player ship"):
        ship_caption(ROSTER, "gamma")
