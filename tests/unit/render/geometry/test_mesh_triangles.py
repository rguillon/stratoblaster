# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/mesh_triangles.py`: geometry read and written as triangles."""

from types import SimpleNamespace

from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.mesh_triangles import (
    Vertex,
    append_triangles,
    bounds_of,
    centroid,
    mean_color,
    triangles,
)
from render.geometry.solids import Placement, SolidBuilder

WHITE = [1.0, 1.0, 1.0]
GREY = [0.5, 0.5, 0.5]


def _slab(size: float = 40.0) -> list:
    return triangles(SolidBuilder().box([size, 2, size], WHITE, Placement([0, 0, 0])).geometry)


def _area(tris: list) -> float:
    total = 0.0
    for t in tris:
        a, b, c = (v.position for v in t)
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        total += (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 / 2
    return total


def test_triangles_gives_each_index_triple_as_its_three_vertices_in_index_order() -> None:
    geo = SimpleNamespace(
        positions=[0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
        colors=[1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0.5],
        indices=[0, 1, 2, 2, 1, 3],
    )
    tris = triangles(geo)
    assert [[v.position for v in t] for t in tris] == [
        [[0, 0, 0], [1, 0, 0], [0, 0, 1]],
        [[0, 0, 1], [1, 0, 0], [1, 0, 1]],
    ]
    assert [v.color for v in tris[1]] == [[0, 0, 1, 1], [0, 1, 0, 1], [1, 1, 1, 0.5]]


def test_append_triangles_adds_each_triangle_after_what_the_geometry_holds() -> None:
    tris = _slab()
    geo = ColoredGeometry()
    append_triangles(geo, tris)
    append_triangles(geo, tris)
    assert len(geo.indices) == 6 * len(tris)
    assert len(geo.colors) == 4 * len(geo.positions) // 3
    assert geo.indices[3 * len(tris)] == 3 * len(tris)
    assert _area(triangles(geo)) == 2 * _area(tris)


def test_append_triangles_moves_the_triangles_by_the_shift() -> None:
    geo = ColoredGeometry()
    append_triangles(geo, _slab(), [1, 2, 3])
    xs = geo.positions[0::3]
    assert min(xs) == -19
    assert max(xs) == 21


def test_centroid_is_the_middle_of_the_three_corners() -> None:
    tri = [Vertex([0, 0, 0], WHITE), Vertex([3, 0, 0], WHITE), Vertex([0, 3, 6], WHITE)]
    assert centroid(tri) == [1, 1, 2]


def test_bounds_of_span_every_corner_and_are_infinite_for_nothing() -> None:
    assert bounds_of(_slab()) == [-20, 0, -20, 20, 2, 20]
    b = bounds_of([])
    assert b[0] == float("inf")
    assert b[3] == float("-inf")


def test_mean_color_averages_the_corners_and_falls_back_for_nothing() -> None:
    tris = [
        [
            Vertex([0, 0, 0], [1, 0, 0, 1]),
            Vertex([0, 0, 0], [0, 1, 0, 1]),
            Vertex([0, 0, 0], [0, 0, 1, 1]),
        ]
    ]
    assert mean_color(tris, GREY) == [1 / 3, 1 / 3, 1 / 3]
    assert mean_color([], GREY) == GREY
