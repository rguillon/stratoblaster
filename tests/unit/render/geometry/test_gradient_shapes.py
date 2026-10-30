"""Unit tests of `src/render/geometry/gradient_shapes.py`."""

import pytest

from render.environment.gradient_cube import GradientStop
from render.geometry.gradient_shapes import ColoredGeometry, build_gradient_rect


def test_two_stops_make_one_quad_from_bottom_to_top() -> None:
    geo = build_gradient_rect(2, 4, [GradientStop(-1, [0, 0, 0]), GradientStop(1, [1, 0.5, 0.25])])
    assert geo.positions == [-1, -2, 0, 1, -2, 0, -1, 2, 0, 1, 2, 0]
    assert geo.indices == [0, 1, 3, 0, 3, 2]
    assert geo.colors == [0, 0, 0, 1, 0, 0, 0, 1, 1, 0.5, 0.25, 1, 1, 0.5, 0.25, 1]


def test_one_row_per_stop_and_two_triangles_between_rows() -> None:
    stops = [GradientStop(-1, [0, 0, 0]), GradientStop(0, [1, 0, 0]), GradientStop(1, [0, 0, 1])]
    geo = build_gradient_rect(2, 2, stops)
    assert len(geo.positions) == 3 * 2 * 3
    assert len(geo.indices) == 2 * 6
    assert geo.positions[1::3] == [-1, -1, 0, 0, 1, 1]


def test_stops_are_sorted_by_height_and_equal_ones_keep_their_order() -> None:
    stops = [
        GradientStop(1, [1, 1, 1]),
        GradientStop(-1, [0, 0, 0]),
        GradientStop(0, [0.2, 0.2, 0.2]),
        GradientStop(0, [0.9, 0.9, 0.9]),
    ]
    geo = build_gradient_rect(2, 2, stops)
    assert geo.positions[1::3] == [-1, -1, 0, 0, 0, 0, 1, 1]  # Two vertices per row.
    # Each row holds 2 vertices of 4 colour values: the rows are the sorted stops.
    assert geo.colors[0:3] == [0, 0, 0]
    assert geo.colors[8:11] == [0.2, 0.2, 0.2]
    assert geo.colors[16:19] == [0.9, 0.9, 0.9]
    assert geo.colors[24:27] == [1, 1, 1]


def test_fewer_than_two_stops_is_an_error() -> None:
    with pytest.raises(ValueError, match="at least 2 stops"):
        build_gradient_rect(1, 1, [GradientStop(0, [0, 0, 0])])


def test_coloured_geometry_starts_empty() -> None:
    geo = ColoredGeometry()
    assert geo.positions == [] and geo.indices == [] and geo.colors == []
