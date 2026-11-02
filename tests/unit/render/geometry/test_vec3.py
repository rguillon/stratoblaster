# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/vec3.py`: vector maths on lists of 3 numbers."""

import math

import pytest

from render.geometry.vec3 import cross, norm, plus


def test_norm_scales_a_vector_to_length_one() -> None:
    v = norm([3, 0, 4])
    assert v == pytest.approx([0.6, 0, 0.8])
    assert math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) == pytest.approx(1)


def test_the_norm_of_a_zero_vector_is_straight_up() -> None:
    assert norm([0, 0, 0]) == [0, 1, 0]


def test_cross_follows_the_right_hand_rule() -> None:
    assert cross([1, 0, 0], [0, 1, 0]) == [0, 0, 1]
    assert cross([0, 1, 0], [1, 0, 0]) == [0, 0, -1]
    assert cross([2, 3, 4], [2, 3, 4]) == [0, 0, 0]


def test_plus_adds_a_scaled_vector() -> None:
    assert plus([1, 2, 3], [1, 0, -1], 2) == [3, 2, 1]
    assert plus([1, 2, 3], [5, 5, 5], 0) == [1, 2, 3]
