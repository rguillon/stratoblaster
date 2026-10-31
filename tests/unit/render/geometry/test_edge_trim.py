"""Unit tests of `src/render/geometry/edge_trim.py`: the self-lit trim along a model's top-view
silhouette (replaces the rim outline, see docs/superpowers/specs/2026-10-31-ship-glow-and-boss-
transform-design.md)."""

from helpers.render_geometry import babylon_normal, triangles

from render.geometry.edge_trim import (
    TrimOptions,
    silhouette_edges,
    trim_ribbons,
    up_triangles,
)
from render.geometry.solids import Placement, SolidBuilder

WHITE = [1.0, 1.0, 1.0]


def _box(size: list[float], at: list[float] | None = None) -> SolidBuilder:
    return SolidBuilder().box(size, WHITE, Placement(at))


def _edges(builder: SolidBuilder, cover: list | None = None) -> list:
    geo = builder.geometry
    return silhouette_edges(geo.positions, geo.indices, cover, 0.2)


def test_a_box_has_its_four_top_edges_as_silhouette_pointing_outward() -> None:
    edges = _edges(_box([2, 1, 2]))
    assert len(edges) == 4
    for edge in edges:
        mid = [(edge.a[i] + edge.b[i]) / 2 for i in range(3)]
        # Outward: away from the box's centre, horizontal, unit length.
        assert mid[0] * edge.out[0] + mid[2] * edge.out[2] > 0
        assert edge.out[1] == 0
        assert abs(edge.out[0] ** 2 + edge.out[2] ** 2 - 1) < 1e-9
        assert edge.a[1] > 0


def test_shared_vertices_give_the_same_edges_as_per_face_vertices() -> None:
    # A square of two triangles sharing two vertices, facing up.
    positions = [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
    indices = [0, 1, 2, 0, 2, 3]
    assert all(babylon_normal(t)[1] > 0 for t in triangles(positions, indices))
    edges = silhouette_edges(positions, indices, None, 0.2)
    assert len(edges) == 4


def test_a_flat_open_face_is_traced_all_round() -> None:
    b = SolidBuilder().face([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]], WHITE)
    assert len(_edges(b)) == 4


def test_edges_covered_by_another_part_of_the_model_are_left_out() -> None:
    # A small box on a large one: the small box's top edges stand inside the large one's outline.
    big = _box([4, 1, 4])
    small = _box([1, 1, 1], [0, 1, 0])
    cover = up_triangles(big.geometry.positions, big.geometry.indices, 0.2)
    cover.extend(up_triangles(small.geometry.positions, small.geometry.indices, 0.2))
    assert _edges(small, cover) == []
    assert len(_edges(big, cover)) == 4


def test_two_boxes_side_by_side_lose_the_edges_they_share() -> None:
    left = _box([1, 1, 1], [-0.5, 0, 0])
    right = _box([1, 1, 1], [0.5, 0, 0])
    cover = up_triangles(left.geometry.positions, left.geometry.indices, 0.2)
    cover.extend(up_triangles(right.geometry.positions, right.geometry.indices, 0.2))
    assert len(_edges(left, cover)) == 3
    assert len(_edges(right, cover)) == 3


def test_ribbons_lie_outside_the_edges_and_face_up() -> None:
    edges = _edges(_box([2, 1, 2]))
    geo = trim_ribbons(edges, TrimOptions(0.1, 0.02))
    tris = triangles(geo.positions, geo.indices)
    # 2 triangles per edge, 2 per corner.
    assert len(tris) == 4 * 2 + 4 * 2
    for tri in tris:
        assert babylon_normal(tri)[1] > 0
        for p in tri:
            assert max(abs(p[0]), abs(p[2])) >= 1 + 0.02 - 1e-9
            assert max(abs(p[0]), abs(p[2])) <= 1 + 0.12 + 1e-9
    assert geo.colors == [1, 1, 1, 1] * (len(geo.positions) // 3)


def test_straight_runs_get_no_corner() -> None:
    # Two squares in a row: the long sides are two collinear edges each, joined without a corner.
    b = SolidBuilder().face([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]], WHITE)
    b.face([[1, 0, 0], [1, 0, 1], [2, 0, 1], [2, 0, 0]], WHITE)
    edges = _edges(b)
    assert len(edges) == 6
    geo = trim_ribbons(edges, TrimOptions(0.1, 0))
    assert len(geo.indices) // 3 == 6 * 2 + 4 * 2


def test_no_geometry_no_trim() -> None:
    assert silhouette_edges([], [], None, 0.2) == []
    assert trim_ribbons([], TrimOptions(0.1, 0)).indices == []
