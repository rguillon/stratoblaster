"""Unit tests of `src/render/geometry/triangulate.py`."""

import pytest

from render.geometry.triangulate import triangulate_polygon

SQUARE = [[0, 0], [2, 0], [2, 2], [0, 2]]
# An L: concave at (1, 1).
L_SHAPE = [[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]]


def _area(points: list[list[float]], tri: list[int]) -> float:
    (ax, az), (bx, bz), (cx, cz) = (points[i] for i in tri)
    return ((bx - ax) * (cz - az) - (bz - az) * (cx - ax)) / 2


def test_a_square_gives_two_counter_clockwise_triangles() -> None:
    tris = triangulate_polygon(SQUARE)
    assert len(tris) == 2
    assert all(_area(SQUARE, t) > 0 for t in tris)
    assert sum(_area(SQUARE, t) for t in tris) == pytest.approx(4)


def test_a_concave_l_shape_is_covered_exactly_by_n_minus_two_triangles() -> None:
    tris = triangulate_polygon(L_SHAPE)
    assert len(tris) == len(L_SHAPE) - 2
    assert all(_area(L_SHAPE, t) > 0 for t in tris)
    assert sum(_area(L_SHAPE, t) for t in tris) == pytest.approx(3)


def test_fewer_than_three_points_give_no_triangle() -> None:
    assert triangulate_polygon([[0, 0], [1, 0]]) == []


def test_a_self_crossing_outline_is_refused() -> None:
    bowtie = [[0, 0], [2, 2], [2, 0], [0, 2]]
    with pytest.raises(ValueError, match="not a simple polygon"):
        triangulate_polygon(bowtie)
