"""Unit tests of `src/game/config/player_ships.py`."""

from game.config.player_ships import PLAYER_SHIPS


def test_p02_r01_the_player_can_fly_three_ships_with_distinct_ids() -> None:
    ids = [ship.id for ship in PLAYER_SHIPS.ships]
    assert ids == ["balanced", "heavy", "light"]


def test_p02_r01_ships_trade_speed_for_health() -> None:
    by_id = {ship.id: ship for ship in PLAYER_SHIPS.ships}
    assert by_id["heavy"].maxHealth > by_id["balanced"].maxHealth > by_id["light"].maxHealth
    assert by_id["light"].maxSpeedFactor > by_id["balanced"].maxSpeedFactor
    assert by_id["heavy"].maxSpeedFactor < by_id["balanced"].maxSpeedFactor


def test_p02_r01_base_speed_is_positive() -> None:
    assert PLAYER_SHIPS.baseSpeedPxPerSec > 0
