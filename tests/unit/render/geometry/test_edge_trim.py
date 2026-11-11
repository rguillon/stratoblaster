# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/edge_trim.py`.

The self-lit trim along a model's top-view silhouette (replaces the rim outline, see
docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-design.md): GFX-TRIM-02, GFX-TRIM-03,
GFX-TRIM-10.
"""

import pytest
from helpers.render_geometry import babylon_normal, triangles

from render.geometry.edge_trim import (
    IDENTITY,
    TrimOptions,
    TrimShape,
    inverse,
    merged_edges,
    multiply,
    silhouette_edges,
    transformed,
    trim_model,
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
    # 2 triangles per edge, 1 per corner.
    assert len(tris) == 4 * 2 + 4
    for tri in tris:
        assert babylon_normal(tri)[1] > 0
        for p in tri:
            assert max(abs(p[0]), abs(p[2])) >= 1 - 1e-9
            assert max(abs(p[0]), abs(p[2])) <= 1 + 0.12 + 1e-9
    assert geo.colors == [1, 1, 1, 1] * (len(geo.positions) // 3)


def test_straight_runs_are_one_ribbon_without_a_corner() -> None:
    # Two squares in a row: the long sides are two collinear edges each, drawn as one ribbon.
    b = SolidBuilder().face([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]], WHITE)
    b.face([[1, 0, 0], [1, 0, 1], [2, 0, 1], [2, 0, 0]], WHITE)
    edges = _edges(b)
    assert len(edges) == 6
    geo = trim_ribbons(edges, TrimOptions(0.1, 0))
    assert len(geo.indices) // 3 == 4 * 2 + 4


def test_no_geometry_no_trim() -> None:
    assert silhouette_edges([], [], None, 0.2) == []
    assert trim_ribbons([], TrimOptions(0.1, 0)).indices == []


def test_matrices_compose_and_invert() -> None:
    # Scale 2, turn 90° about Y, then move by (1, 2, 3).
    m = [0, 0, -2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 1, 2, 3, 1]
    p = transformed([1, 1, 1], m)
    assert p == [3, 4, 1]
    back = transformed(p, inverse(m))
    assert [round(v, 9) for v in back] == [1, 1, 1]
    assert [round(v, 9) for v in multiply(m, inverse(m))] == IDENTITY


def test_a_model_trims_each_mesh_in_its_own_space_with_the_others_as_cover() -> None:
    big = _box([4, 1, 4]).geometry
    small = _box([1, 1, 1]).geometry
    # The small box sits on the big one, moved up by 1 in the model.
    up = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1]
    shapes = [
        TrimShape(big.positions, big.indices, IDENTITY),
        TrimShape(small.positions, small.indices, up),
    ]
    trims = trim_model(shapes, TrimOptions(0.1, 0))
    assert len(trims[0].indices) // 3 == 4 * 2 + 4
    assert trims[1].indices == []


def test_a_mirrored_mesh_still_gets_its_trim_outside() -> None:
    box = _box([2, 1, 2]).geometry
    mirror = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 5, 0, 0, 1]
    (trim,) = trim_model([TrimShape(box.positions, box.indices, mirror)], TrimOptions(0.1, 0.02))
    for i in range(0, len(trim.positions), 3):
        assert max(abs(trim.positions[i]), abs(trim.positions[i + 2])) >= 1 - 1e-9


def test_a_curved_outline_is_drawn_with_fewer_ribbons_on_its_outside() -> None:
    # A 32-sided disc: its rim turns 11.25° per edge, so runs of 2 edges merge.
    b = SolidBuilder().cylinder(10, 1, 32, WHITE)
    edges = _edges(b)
    assert len(edges) == 32
    merged = merged_edges(edges)
    assert len(merged) <= 16
    for edge in merged:
        mid = [(edge.a[i] + edge.b[i]) / 2 for i in range(3)]
        assert mid[0] * edge.out[0] + mid[2] * edge.out[2] > 0
    geo = trim_ribbons(edges, TrimOptions(0.5, 0))
    assert len(geo.indices) // 3 <= 16 * 3


def test_a_square_keeps_its_four_sides() -> None:
    assert len(merged_edges(_edges(_box([2, 1, 2])))) == 4


def test_gfx_trim_10_a_flat_triangle_faces_neither_up_nor_down() -> None:
    # Three points in a row: the triangle has no normal, so it counts as facing sideways.
    positions = [0, 0, 0, 1, 0, 0, 2, 0, 0]
    assert up_triangles(positions, [0, 1, 2], 0.2) == []
    assert len(up_triangles(positions, [0, 1, 2], 0.0)) == 1


def test_gfx_trim_02_a_standing_edge_has_no_outline_seen_from_above() -> None:
    # A wall, counted as facing up (min_up 0): its upright edge is not traced, the other two are.
    positions = [0, 0, 0, 0, 1, 0, 1, 0, 0]
    edges = silhouette_edges(positions, [0, 1, 2], None, 0.0)
    assert len(edges) == 2
    for edge in edges:
        assert abs(edge.b[0] - edge.a[0]) + abs(edge.b[2] - edge.a[2]) > 0
        assert edge.out[1] == 0


def test_gfx_trim_02_vertices_at_the_same_place_make_no_edge() -> None:
    # A sliver facing up whose last vertex is within a thousandth of its first: that side is no
    # edge, and the two others are one segment met twice, so it has no outline.
    positions = [0, 0, 0, 1, 0, 0, 0.0001, 0, 0.0001]
    assert len(up_triangles(positions, [0, 1, 2], 0.2)) == 1
    assert silhouette_edges(positions, [0, 1, 2], None, 0.2) == []


def test_gfx_trim_03_a_run_that_doubles_back_keeps_its_outward_side() -> None:
    # A unit box in a box twice as long, in one mesh: along each long side, both boxes' edges leave
    # the corner they share the same way and merge, so the run's chord runs back against its first
    # edge; its outward side is turned round to stay out.
    b = SolidBuilder().box([1, 1, 1], WHITE, Placement([0.5, 0, 0.5]))
    b.box([2, 1, 1], WHITE, Placement([1, 0, 0.5]))
    edges = _edges(b)
    merged = merged_edges(edges)
    assert len(merged) == 3
    for edge in merged:
        mid = [(edge.a[i] + edge.b[i]) / 2 for i in range(3)]
        # Away from the middle of the footprint, (1, 0.5).
        assert (mid[0] - 1) * edge.out[0] + (mid[2] - 0.5) * edge.out[2] > 0
    geo = trim_ribbons(edges, TrimOptions(0.1, 0.02))
    for tri in triangles(geo.positions, geo.indices):
        assert babylon_normal(tri)[1] > 0
        assert all(not (0 < p[0] < 2 and 0 < p[2] < 1) for p in tri)


def test_gfx_trim_03_a_run_that_comes_back_to_its_end_has_no_length_and_gets_no_ribbon() -> None:
    # Two unit boxes under one covering both, in one mesh: along each long side, the three edges
    # meet two by two in line, so the run goes round to the end of its first edge.
    b = SolidBuilder().box([1, 1, 1], WHITE, Placement([0.5, 0, 0.5]))
    b.box([1, 1, 1], WHITE, Placement([1.5, 0, 0.5]))
    b.box([2, 1, 1], WHITE, Placement([1, 0, 0.5]))
    edges = _edges(b)
    assert len(edges) == 6
    assert merged_edges(edges) == []
    assert trim_ribbons(edges, TrimOptions(1, 0)).indices == []


def test_a_flat_matrix_has_no_inverse_and_gives_the_identity() -> None:
    flat = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 4, 5, 1]
    result = inverse(flat)
    assert result == IDENTITY
    assert result is not IDENTITY


def test_gfx_trim_02_an_edge_partly_covered_keeps_its_trim_where_it_shows() -> None:
    """D-330: a fin across half a hull's edge hides only that half of the edge's trim."""
    hull = _box([2, 1, 4])
    # A plate standing out past the hull's right side (x = 1) over its back half (z < 0).
    fin = _box([1, 0.2, 2], [1.4, 0.7, -1])
    cover = up_triangles(hull.geometry.positions, hull.geometry.indices, 0.2)
    cover.extend(up_triangles(fin.geometry.positions, fin.geometry.indices, 0.2))
    right = [e for e in _edges(hull, cover) if e.out[0] > 0.5]
    assert len(right) == 1
    zs = sorted([right[0].a[2], right[0].b[2]])
    # The front half (z from 0 to 2) keeps its trim; the back half, under the fin, has none.
    assert zs[0] == pytest.approx(0, abs=0.01)
    assert zs[1] == pytest.approx(2)
