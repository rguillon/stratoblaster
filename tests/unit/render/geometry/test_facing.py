# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/facing.py`: faces a camera above never sees."""

from typing import Any

from render.geometry.facing import faces_down, seen_from_above
from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.solids import SolidBuilder

# The enemies' limit (`enemy_mesh.UNSEEN_BELOW`): within about 30° of straight down.
LIMIT = -0.85
SIDE = [0.2, 0.3, 0.4]
TOP = [0.9, 0.8, 0.7]
# A box's faces, in the order `SolidBuilder.box` draws them, two triangles each.
TOP_FACE, BOTTOM_FACE, SIDE_FACES = 0, 1, (2, 3, 4, 5)


def _box() -> ColoredGeometry:
    return SolidBuilder().box([2, 1, 3], SIDE, None, TOP).geometry


def _triangle_corners(geo: ColoredGeometry, t: int) -> list[int]:
    return list(geo.indices[3 * t : 3 * t + 3])


def _down(geo: ColoredGeometry, t: int, limit: float = LIMIT) -> bool:
    a, b, c = _triangle_corners(geo, t)
    return faces_down(geo.positions, a, b, c, limit)


def _corner(geo: ColoredGeometry, v: int) -> tuple[list[float], list[float]]:
    """Return a vertex's position and colour."""
    return geo.positions[3 * v : 3 * v + 3], geo.colors[4 * v : 4 * v + 4]


def _drawn(geo: ColoredGeometry) -> list[list[Any]]:
    """Each triangle as its three corners' positions and colours, in order."""
    return [
        [_corner(geo, v) for v in _triangle_corners(geo, t)] for t in range(len(geo.indices) // 3)
    ]


def test_a_box_s_bottom_faces_down() -> None:
    geo = _box()
    assert _down(geo, 2 * BOTTOM_FACE)
    assert _down(geo, 2 * BOTTOM_FACE + 1)


def test_a_box_s_top_and_sides_do_not_face_down() -> None:
    geo = _box()
    for face in (TOP_FACE, *SIDE_FACES):
        assert not _down(geo, 2 * face), face
        assert not _down(geo, 2 * face + 1), face


def test_a_face_tilted_down_faces_down_only_past_the_limit() -> None:
    # A quad turned 45° from straight down (normal Y about -0.71), facing down and towards -Z.
    b = SolidBuilder().face([[0, 0, 0], [0, 1, -1], [1, 1, -1], [1, 0, 0]], SIDE)
    geo = b.geometry
    assert not _down(geo, 0, LIMIT)
    assert _down(geo, 0, -0.5)


def test_a_degenerate_triangle_is_kept() -> None:
    # Three points on a line: no area, no normal. Kept even with a limit that takes everything else.
    positions = [0.0, 0, 0, 1, 0, 0, 2, 0, 0]
    assert not faces_down(positions, 0, 1, 2, 1.0)
    # The same limit takes a real triangle.
    assert faces_down([0.0, 0, 0, 1, 0, 0, 0, 0, 1], 0, 1, 2, 1.0)


def test_seen_from_above_drops_the_box_s_two_bottom_triangles() -> None:
    geo = _box()
    seen = seen_from_above(geo, LIMIT)
    assert len(seen.indices) == len(geo.indices) - 6
    # The kept triangles are the others, in order, each corner where it was in its colour.
    kept = [tri for t, tri in enumerate(_drawn(geo)) if t // 2 != BOTTOM_FACE]
    assert _drawn(seen) == kept
    # Nothing left faces down.
    assert not any(_down(seen, t) for t in range(len(seen.indices) // 3))


def test_seen_from_above_keeps_only_the_vertices_it_uses_renumbered() -> None:
    geo = _box()
    seen = seen_from_above(geo, LIMIT)
    # The bottom face's own four vertices are gone; the others are kept, once each.
    assert len(seen.positions) == len(geo.positions) - 4 * 3
    assert len(seen.colors) == len(geo.colors) - 4 * 4
    count = len(seen.positions) // 3
    assert sorted(set(seen.indices)) == list(range(count))
    # The top keeps its own colour; no vertex is in a colour the box does not have.
    colours = {tuple(seen.colors[4 * v : 4 * v + 3]) for v in range(count)}
    assert colours == {tuple(SIDE), tuple(TOP)}


def test_seen_from_above_shares_a_vertex_between_its_triangles() -> None:
    # A quad facing up: two triangles over four shared vertices, kept as four.
    geo = SolidBuilder().face([[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]], TOP).geometry
    seen = seen_from_above(geo, LIMIT)
    assert len(seen.positions) == 4 * 3
    assert _drawn(seen) == _drawn(geo)


def test_seen_from_above_of_nothing_is_nothing() -> None:
    seen = seen_from_above(ColoredGeometry(), LIMIT)
    assert seen.positions == []
    assert seen.indices == []
    assert seen.colors == []


def test_seen_from_above_leaves_the_geometry_it_is_given_alone() -> None:
    geo = _box()
    before = (list(geo.positions), list(geo.indices), list(geo.colors))
    seen_from_above(geo, LIMIT)
    assert (geo.positions, geo.indices, geo.colors) == before
