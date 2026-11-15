# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/player_ships.py`."""

from game.config.player_ships import PLAYER_SHIPS


def test_game_ship_01_the_player_flies_one_ship_the_player_ship() -> None:
    ids = [ship.id for ship in PLAYER_SHIPS.ships]
    assert ids == ["player"]


def test_game_ship_02_its_top_speed_is_the_base_speed() -> None:
    """Also GAME-SHIP-03 (health)."""
    (ship,) = PLAYER_SHIPS.ships
    assert ship.maxSpeedFactor * PLAYER_SHIPS.baseSpeedPxPerSec == 225
    assert ship.maxHealth == 100


def test_game_ship_02_base_speed_is_positive() -> None:
    assert PLAYER_SHIPS.baseSpeedPxPerSec > 0
