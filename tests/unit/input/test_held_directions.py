"""Unit tests of `src/input/held_directions.py`."""

import math

import pytest

from input.held_directions import DIRECTION_KEYS, HeldDirections


def test_p06_r02_movement_keys_are_arrows_and_wasd() -> None:
    assert DIRECTION_KEYS["ArrowUp"] == "up"
    assert DIRECTION_KEYS["KeyA"] == "left"
    assert len(DIRECTION_KEYS) == 8


def test_p06_r02_no_key_held_means_no_movement() -> None:
    held = HeldDirections()
    assert held.direction.x == 0
    assert held.direction.y == 0


def test_p06_r02_a_single_key_flies_at_full_speed() -> None:
    held = HeldDirections()
    assert held.key("ArrowRight", True) is True
    assert held.direction.x == 1
    assert held.direction.y == 0


def test_p06_r02_a_diagonal_is_normalised_to_length_one() -> None:
    held = HeldDirections()
    held.key("KeyW", True)
    held.key("KeyD", True)
    direction = held.direction
    assert direction.x == pytest.approx(1 / math.sqrt(2))
    assert direction.y == pytest.approx(1 / math.sqrt(2))


def test_p06_r02_opposite_keys_cancel_out() -> None:
    held = HeldDirections()
    held.key("ArrowLeft", True)
    held.key("ArrowRight", True)
    assert held.direction.x == 0


def test_p06_r02_non_movement_keys_are_not_claimed() -> None:
    held = HeldDirections()
    assert held.key("Space", True) is False
    assert held.key("Space", False) is False


def test_p06_r02_key_repeat_downs_do_not_double_a_key() -> None:
    held = HeldDirections()
    held.key("ArrowUp", True)
    held.key("ArrowUp", True)
    held.key("ArrowUp", False)
    assert held.direction.y == 0


def test_p06_r02_clear_releases_every_key() -> None:
    held = HeldDirections()
    held.key("ArrowUp", True)
    held.key("KeyA", True)
    held.clear()
    assert held.direction.x == 0
    assert held.direction.y == 0
