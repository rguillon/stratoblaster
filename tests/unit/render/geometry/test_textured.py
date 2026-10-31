"""Unit tests of `src/render/geometry/textured.py` (D-210)."""

from helpers.geometry_checks import check_colored

from render.geometry.textured import QuadBuilder


def test_d210_a_quad_has_four_corners_two_triangles_and_its_uvs():
    quads = QuadBuilder()
    quads.quad([[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]], [0.1, 0.2, 0.3, 0.4], [1, 0.5, 0])
    geo = quads.geometry
    assert check_colored(geo) == 4
    assert geo.indices == [0, 2, 1, 0, 3, 2]
    # u1 on the first edge, v0 along the bottom.
    assert geo.uvs == [0.3, 0.2, 0.3, 0.4, 0.1, 0.4, 0.1, 0.2]
    assert geo.colors[:4] == [1, 0.5, 0, 1]


def test_d210_quads_follow_each_other():
    quads = QuadBuilder()
    corners = [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]]
    quads.quad(corners, [0, 0, 1, 1], [1, 1, 1])
    quads.quad(corners, [0, 0, 1, 1], [1, 1, 1])
    assert quads.geometry.indices[6:] == [4, 6, 5, 4, 7, 6]
