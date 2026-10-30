"""Unit tests of `src/core/systems/enemy_motion.py`."""

import math

import pytest

from core.systems.enemy_motion import (
    MIN_CONTROLS,
    Path,
    PathPose,
    _at_or,
    _at_or_point,
    _catmull_rom,
    approach,
    fan_headings,
)


def test_gd45_a_path_needs_at_least_two_control_points() -> None:
    assert MIN_CONTROLS == 2
    with pytest.raises(ValueError, match="at least 2 points"):
        Path([(0, 0)])


def test_gd45_a_straight_path_has_its_distance_as_length() -> None:
    path = Path([(0, 0), (10, 0)])
    assert path.length == pytest.approx(10)


def test_gd45_the_path_is_followed_by_distance_travelled() -> None:
    path = Path([(0, 0), (10, 0)], samples_per_span=4)
    pose = path.at(5)
    assert isinstance(pose, PathPose)
    assert pose.x == pytest.approx(5)
    assert pose.y == pytest.approx(0)
    # Heading from +Y, positive to the right: along +X is a quarter turn.
    assert pose.heading == pytest.approx(math.pi / 2)


def test_gd45_the_path_is_clamped_to_its_ends() -> None:
    path = Path([(0, 0), (10, 0), (10, 10)])
    start = path.at(-5)
    end = path.at(1000)
    assert (start.x, start.y) == pytest.approx((0, 0))
    assert (end.x, end.y) == pytest.approx((10, 10))


def test_gd45_a_curve_passes_through_its_control_points_and_is_longer_than_the_chord() -> None:
    controls = [(0, 0), (10, 10), (20, 0)]
    path = Path(controls)
    assert path.at(0).x == pytest.approx(0)
    assert path.at(path.length).x == pytest.approx(20)
    assert path.at(path.length).y == pytest.approx(0)
    assert path.length > 20


def test_gd45_a_path_of_coincident_points_has_no_length() -> None:
    path = Path([(3, 4), (3, 4)])
    assert path.length == 0
    pose = path.at(0)
    assert (pose.x, pose.y, pose.heading) == (3, 4, 0)


def test_gd45_catmull_rom_interpolates_between_the_middle_points() -> None:
    assert _catmull_rom(0, 1, 2, 3, 0) == pytest.approx(1)
    assert _catmull_rom(0, 1, 2, 3, 1) == pytest.approx(2)


def test_gd45_out_of_range_lookups_take_the_default() -> None:
    assert _at_or([1.0, 2.0], 1, 9) == 2
    assert _at_or([1.0, 2.0], 2, 9) == 9
    assert _at_or([1.0, 2.0], -1, 9) == 9
    assert _at_or_point([[1, 2]], 0) == [1, 2]
    assert _at_or_point([[1, 2]], 5) == [0, 0]


def test_gd45_fan_headings_spread_around_the_centre() -> None:
    headings = fan_headings(0, 3, 0.2)
    assert headings == pytest.approx([-0.2, 0, 0.2])
    assert fan_headings(1.5, 1, 0.2) == pytest.approx([1.5])
    assert fan_headings(0, 0, 0.2) == []


def test_gd45_approach_moves_by_at_most_the_step() -> None:
    assert approach(0, 10, 3) == 3
    assert approach(0, -10, 3) == -3
    assert approach(9, 10, 3) == 10
    assert approach(10, 10, 3) == 10
    assert approach(5, 2, 0.5) == pytest.approx(4.5)


def test_gd45_approach_with_a_negative_step_does_not_move() -> None:
    # Only reached with a nonsensical step: the sign of a zero difference is zero.
    assert approach(1, 1, -1) == 1
