"""Unit tests of `src/game/view/bosses/mini_boss_shapes.py`."""

import math

import pytest

from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    offset,
    put,
    radius_of,
    scaled,
    sign_of,
    turned,
    yawed,
)


def _flat(points):
    return [v for point in points for v in point]


def test_offset_moves_a_point_by_a_vector():
    assert offset([1, 2, 3], 1, -1, 0.5) == pytest.approx([2, 1, 3.5])


def test_scaled_scales_an_outline_about_the_origin_then_moves_it():
    outline = [[1, 2], [-3, 0]]
    assert _flat(scaled(outline, 2)) == pytest.approx([2, 4, -6, 0])
    assert _flat(scaled(outline, 0.5, dx=1, dz=-1)) == pytest.approx([1.5, 0, -0.5, -1])


def test_yawed_turns_a_point_about_y_from_plus_z_towards_plus_x():
    # A quarter turn takes the nose (+Z) to +X and leaves the height alone.
    x, y, z = yawed([0, 5, 2], math.pi / 2)
    assert (x, y, z) == pytest.approx((2, 5, 0), abs=1e-12)
    assert yawed([1, 2, 3], 0) == pytest.approx([1, 2, 3])


def test_put_turns_a_point_by_the_yaw_then_places_it_at_the_centre():
    assert put([10, 0, 0], 0, 1, 1, 0) == pytest.approx([10, 1, 1])
    x, y, z = put([0, 0, 0], 0, 0, 2, math.pi / 2)
    assert (x, y, z) == pytest.approx((2, 0, 0), abs=1e-12)


def test_turned_runs_a_barrel_from_its_foot_along_its_pitched_yawed_axis():
    at = [0, 0, 0]
    foot = [1, 0, 0]
    # At its base (along 0) the barrel stands on its foot.
    assert turned(at, foot, 0, 0, 0) == pytest.approx([1, 0, 0])
    # Level (no pitch) the barrel points up, its muzzle 4 above the foot.
    assert turned(at, foot, 4, 0, 0) == pytest.approx([1, 4, 0], abs=1e-12)
    # Pitched a quarter turn, it points forward (+Z) from the foot instead.
    assert turned(at, foot, 4, QUARTER, 0) == pytest.approx([1, 0, 4], abs=1e-12)


def test_sign_of_is_minus_one_zero_or_one():
    assert [sign_of(v) for v in (-3, 0, 2.5)] == [-1, 0, 1]


def test_radius_of_reads_a_part_radius_or_falls_back():
    part = type("P", (), {"radius": 4.0})()
    assert radius_of([part], 0, 9) == 4.0
    assert radius_of([], 0, 9) == 9
    assert radius_of([None], 0, 9) == 9
    assert radius_of([type("Q", (), {"radius": None})()], 0, 9) == 9


def test_the_shades_are_dark_greys_with_a_soot_darker_than_the_edge():
    assert all(0 <= c <= 1 for color in SHADE.values() for c in color)
    assert sum(SHADE["soot"]) < sum(SHADE["edge"])
    assert WHITE == [1, 1, 1]
