# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/entities/player_ship.py`."""

import pytest

from core.entities.player_ship import (
    PlayerShipDefinition,
    PlayerShipRoster,
    find_player_ship,
    ship_max_speed_px_per_sec,
)


def roster(*ships: PlayerShipDefinition, base: float = 200.0) -> PlayerShipRoster:
    return PlayerShipRoster(base, list(ships))


FAST = PlayerShipDefinition("fast", "Fast", 1.5, 3)

TOUGH = PlayerShipDefinition("tough", "Tough", 0.8, 6)


def test_a_ship_definition_keeps_its_stats() -> None:
    assert (FAST.id, FAST.name, FAST.max_speed_factor, FAST.max_health) == ("fast", "Fast", 1.5, 3)


def test_find_player_ship_returns_the_ship_with_the_id() -> None:
    assert find_player_ship(roster(FAST, TOUGH), "tough") is TOUGH


def test_find_player_ship_raises_for_an_unknown_id() -> None:
    with pytest.raises(ValueError, match="Unknown player ship"):
        find_player_ship(roster(FAST), "nope")


def test_max_speed_is_the_base_speed_times_the_factor() -> None:
    assert ship_max_speed_px_per_sec(roster(FAST, TOUGH), "fast") == pytest.approx(300)
    assert ship_max_speed_px_per_sec(roster(FAST, TOUGH), "tough") == pytest.approx(160)
