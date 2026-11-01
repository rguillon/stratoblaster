# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/input/held_directions.py`."""

import math

import pytest

from input.held_directions import DIRECTION_KEYS, HeldDirections


def test_game_ctrl_01_movement_keys_are_arrows_and_wasd() -> None:
    assert DIRECTION_KEYS["ArrowUp"] == "up"
    assert DIRECTION_KEYS["KeyA"] == "left"
    assert len(DIRECTION_KEYS) == 8


def test_game_ctrl_03_no_key_held_means_no_movement() -> None:
    held = HeldDirections()
    assert held.direction.x == 0
    assert held.direction.y == 0


def test_game_ctrl_03_a_single_key_flies_at_full_speed() -> None:
    held = HeldDirections()
    assert held.key("ArrowRight", down=True) is True
    assert held.direction.x == 1
    assert held.direction.y == 0


def test_game_ctrl_03_a_diagonal_is_normalised_to_length_one() -> None:
    held = HeldDirections()
    held.key("KeyW", down=True)
    held.key("KeyD", down=True)
    direction = held.direction
    assert direction.x == pytest.approx(1 / math.sqrt(2))
    assert direction.y == pytest.approx(1 / math.sqrt(2))


def test_game_ctrl_03_opposite_keys_cancel_out() -> None:
    held = HeldDirections()
    held.key("ArrowLeft", down=True)
    held.key("ArrowRight", down=True)
    assert held.direction.x == 0


def test_game_ctrl_01_non_movement_keys_are_not_claimed() -> None:
    held = HeldDirections()
    assert held.key("Space", down=True) is False
    assert held.key("Space", down=False) is False


def test_game_ctrl_03_key_repeat_downs_do_not_double_a_key() -> None:
    held = HeldDirections()
    held.key("ArrowUp", down=True)
    held.key("ArrowUp", down=True)
    held.key("ArrowUp", down=False)
    assert held.direction.y == 0


def test_game_ctrl_07_clear_releases_every_key() -> None:
    held = HeldDirections()
    held.key("ArrowUp", down=True)
    held.key("KeyA", down=True)
    held.clear()
    assert held.direction.x == 0
    assert held.direction.y == 0
