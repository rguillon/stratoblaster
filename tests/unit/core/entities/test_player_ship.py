"""Unit tests of `src/core/entities/player_ship.py`."""

import pytest

from core.entities.player_ship import (
    PlayerShipDefinition,
    PlayerShipRoster,
    find_player_ship,
    ship_max_speed_px_per_sec,
    validate_player_ship_roster,
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


def test_a_valid_roster_passes() -> None:
    validate_player_ship_roster(roster(FAST, TOUGH))


def test_a_roster_needs_a_ship() -> None:
    with pytest.raises(ValueError, match="at least one"):
        validate_player_ship_roster(roster())


@pytest.mark.parametrize("base", [0, -1, float("nan")])
def test_the_base_speed_must_be_positive(base: float) -> None:
    with pytest.raises(ValueError, match="base speed"):
        validate_player_ship_roster(roster(FAST, base=base))


def test_ship_ids_must_be_unique() -> None:
    with pytest.raises(ValueError, match='Duplicate player ship id "fast"'):
        validate_player_ship_roster(roster(FAST, FAST))


def test_a_ship_speed_must_be_positive() -> None:
    slow = PlayerShipDefinition("slow", "Slow", 0, 3)
    with pytest.raises(ValueError, match="speed must be positive"):
        validate_player_ship_roster(roster(slow))


@pytest.mark.parametrize("health", [0, -2, 1.5, float("nan")])
def test_a_ship_health_must_be_a_positive_whole_number(health: float) -> None:
    ship = PlayerShipDefinition("bad", "Bad", 1, health)
    with pytest.raises(ValueError, match="positive integer"):
        validate_player_ship_roster(roster(ship))


def test_a_whole_number_health_given_as_a_float_is_accepted() -> None:
    validate_player_ship_roster(roster(PlayerShipDefinition("ok", "Ok", 1, 4.0)))
