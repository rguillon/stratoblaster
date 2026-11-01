"""How a moving region's piece is posed in a boss model (BOSS-45, D-230)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.moving_regions import motion_value, moving_region, slide, swing
from game.view.bosses.region_motion import (
    moved_triangles,
    node_pose,
    posed,
    progress,
    relative_value,
    to_config,
    to_model,
)
from render.geometry.shatter import Vertex

MOTIONS = [
    swing([12, -5, 3], "up", [0, 50]),
    swing([12, -5, 3], "along", [-80, 10]),
    swing([12, -5, 3], "across", [20, -35]),
    slide([[0, 0, 0], [9, -4, 2]]),
]


def _babylon(point: list[float], pose: list[Any]) -> list[float]:
    """`point` placed by a node at `pose` (Babylon's rotation matrices, X then Y then Z turns:
    only one is ever set)."""
    x, y, z = point
    rx, ry, rz = pose[1]
    c, s = math.cos(rx), math.sin(rx)
    y, z = y * c - z * s, y * s + z * c
    c, s = math.cos(ry), math.sin(ry)
    x, z = x * c + z * s, -x * s + z * c
    c, s = math.cos(rz), math.sin(rz)
    x, y = x * c - y * s, x * s + y * c
    p = pose[0]
    return [x + p[0], y + p[1], z + p[2]]


def test_config_and_model_axes_convert_both_ways() -> None:
    assert to_model([3, 4, 5]) == [-3, 5, -4]
    assert to_config(to_model([3, 4, 5])) == [3, 4, 5]


@pytest.mark.parametrize("motion", MOTIONS)
def test_a_node_at_its_pose_moves_what_it_holds_as_the_motion_moves_points(motion: Any) -> None:
    value = motion_value(motion, 0.7)
    point = to_model([20, 8, 6])
    [[moved, _, _]] = moved_triangles([[Vertex(point, [1, 1, 1])] * 3], motion, value)
    assert _babylon(point, node_pose(motion, value)) == pytest.approx(moved.position, abs=1e-9)


@pytest.mark.parametrize("motion", MOTIONS)
def test_what_rides_a_piece_is_where_it_is_drawn_once_the_piece_has_moved(motion: Any) -> None:
    pose = node_pose(motion, relative_value(motion, motion_value(motion, 1)))
    assert pose[0] == pytest.approx([0, 0, 0], abs=1e-9)
    assert pose[1] == pytest.approx([0, 0, 0], abs=1e-9)


def _boss(form: int, into: int, transform: float) -> Any:
    return SimpleNamespace(form=form, transforming_into=into, transform=transform)


def test_a_piece_rests_until_its_transformation_then_moves_and_stays_moved() -> None:
    [region] = moving_region(
        "arm", 2, [[0, 0], [9, 0], [9, 9]], slide([[0, 0, 0], [5, 0, 0]]), None, None, False
    )
    assert progress(region, None) == 0
    assert progress(region, _boss(0, 1, 0.5)) == 0
    move = BOSS_LOOK.reveal.move
    assert progress(region, _boss(1, 2, move[0])) == 0
    assert 0 < progress(region, _boss(1, 2, (move[0] + move[1]) / 2)) < 1
    assert progress(region, _boss(1, 2, move[1])) == 1
    assert progress(region, _boss(2, 0, 0)) == 1


def test_a_piece_s_triangles_are_at_rest_before_its_transformation_and_moved_after() -> None:
    [region] = moving_region(
        "arm", 1, [[0, 0], [9, 0], [9, 9]], slide([[1, 0, 0], [5, 0, 0]]), None, None, False
    )
    tri = [Vertex([0, 0, 0], [1, 1, 1])] * 3
    assert posed([tri], region, 0)[0][0].position == [-1, 0, 0]
    assert posed([tri], region, 1)[0][0].position == [-5, 0, 0]
