"""Unit tests of `src/render/scenery/tile_road_geometry.py`."""

import pytest
from helpers.render_geometry import babylon_normal, points_of, triangles

from core.scenery.road_tiles import PieceSide, RoadPiece
from core.scenery.scenery_level import TileRules
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery.tile_road_geometry import (
    LAYER,
    Arm,
    TileRoadLook,
    add_piece,
    arm_lines,
    build_tile_grid,
    build_tile_road_geometry,
    cuts,
    piece_roadway,
)

GREY = (0.5, 0.5, 0.5)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
RED = (1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
TILE = TileRules(10, 2)
LOOK = TileRoadLook(GREY, WHITE, BLACK, 0.5, RED, BLUE, 0.3, 0.1)


def _side(size: int = 1, offset: int = 0) -> PieceSide:
    return PieceSide(size, offset)


def _piece(sides: list[PieceSide | None], size: int = 1, x: int = 0, z: int = 0) -> RoadPiece:
    kind = "cross" if sum(s is not None for s in sides) == 4 else "straight"  # noqa: PLR2004
    return RoadPiece(x, z, size, kind, False, sides)


def _layer_of(color: tuple[float, ...]) -> int:
    """The layer a colour is painted on: sidewalk 0, kerb 1, roadway 2, lines 3."""
    return {WHITE: 0, BLACK: 1, GREY: 2, RED: 3, BLUE: 3}[tuple(color[:3])]


def _colours(geo: ColoredGeometry) -> list[tuple[float, ...]]:
    return [tuple(geo.colors[i : i + 3]) for i in range(0, len(geo.colors), 4)]


def test_cuts_are_the_ends_and_every_multiple_of_the_cell_between_them() -> None:
    assert cuts(0, 10, 4) == [0, 4, 8, 10]
    assert cuts(1, 3, 4) == [1, 3]


def test_a_cut_on_an_exact_multiple_of_the_cell_is_not_repeated() -> None:
    assert cuts(0, 8, 4) == [0, 4, 8]


def test_a_straight_piece_has_its_roadway_across_its_whole_length() -> None:
    roadway, arms = piece_roadway(_piece([_side(), None, _side(), None]), TILE)
    assert len(arms) == 2
    for x0, x1, z0, z1 in roadway:
        assert (x0, x1, z0, z1) == pytest.approx((2, 8, 0, 10))


def test_a_cross_stops_each_arm_at_the_far_side_of_the_road_it_crosses() -> None:
    roadway, arms = piece_roadway(_piece([_side()] * 4), TILE)
    # The +Z arm runs from its edge (z=10) down to the far side of the X road (z=2), its lines
    # stop at the near side (z=8); the -Z arm is the same, mirrored about the middle.
    assert roadway[0] == pytest.approx((2, 8, 2, 10))
    assert arms[0].line == pytest.approx((2, 8, 8, 10))
    assert roadway[2] == pytest.approx((2, 8, 0, 8))
    assert arms[2].line == pytest.approx((2, 8, 0, 2))


def test_the_lines_of_each_arm_lie_within_its_roadway() -> None:
    roadway, arms = piece_roadway(_piece([_side()] * 4), TILE)
    for rect, arm in zip(roadway, arms, strict=True):
        x0, x1, z0, z1 = rect
        lx0, lx1, lz0, lz1 = arm.line
        assert x0 <= lx0 and lx1 <= x1
        assert z0 <= lz0 and lz1 <= z1


def test_a_tee_has_one_arm_per_open_side_and_arms_on_x_run_along_x() -> None:
    _roadway, arms = piece_roadway(_piece([_side(), _side(), None, _side()]), TILE)
    assert [a.along_x for a in arms] == [False, True, True]


def test_an_arm_of_two_lanes_has_a_centre_line_and_a_lane_line_each_side() -> None:
    arm = Arm(2, (2, 8, 8, 10), False)
    centre, lanes = arm_lines(arm, 0.3)
    assert len(centre) == 1
    assert (centre[0][0] + centre[0][1]) / 2 == pytest.approx(5)
    assert len(lanes) == 2
    # The lane lines are symmetric about the centre line, a lane (1.5) away from it.
    left, right = sorted(lanes, key=lambda r: r[0])
    assert (left[0] + left[1]) / 2 == pytest.approx(3.5)
    assert (right[0] + right[1]) / 2 == pytest.approx(6.5)


def test_a_one_lane_arm_has_no_lane_lines() -> None:
    _centre, lanes = arm_lines(Arm(1, (2, 8, 0, 10), True), 0.3)
    assert lanes == []


def test_each_layer_is_the_ground_under_it_plus_the_lift_and_its_layer() -> None:
    geo = ColoredGeometry()

    def ground(x: float, z: float) -> float:
        return 0.1 * x + 0.05 * z

    add_piece(geo, _piece([_side()] * 4), TILE, LOOK, ground)
    points = points_of(geo.positions)
    for point, color in zip(points, _colours(geo), strict=True):
        expected = LOOK.lift + _layer_of(color) * LAYER
        assert point[1] - ground(point[0], point[2]) == pytest.approx(expected)


def test_every_face_of_a_piece_on_flat_ground_faces_up() -> None:
    geo = ColoredGeometry()
    add_piece(geo, _piece([_side()] * 4), TILE, LOOK, lambda x, z: 0.0)
    assert geo.indices
    for tri in triangles(geo.positions, geo.indices):
        assert babylon_normal(tri)[1] > 0


def test_the_sidewalk_is_drawn_first_over_the_whole_piece_in_its_colour() -> None:
    geo = ColoredGeometry()
    add_piece(geo, _piece([_side(), None, None, None]), TILE, LOOK, lambda x, z: 0.0)
    # The piece is cut on half-tile lines: a 3 x 3 grid of sidewalk vertices, drawn first.
    sidewalk = _colours(geo)[:9]
    assert all(c == WHITE for c in sidewalk)


def test_pieces_belong_to_the_chunk_of_their_middle() -> None:
    piece = _piece([_side(2), None, _side(2), None], size=2)
    # Its middle is at z = 10, the edge between the chunks [0, 10) and [10, 20).
    before = build_tile_road_geometry([piece], TILE, LOOK, lambda x, z: 0.0, 0, 10)
    after = build_tile_road_geometry([piece], TILE, LOOK, lambda x, z: 0.0, 10, 20)
    assert before.indices == []
    assert after.indices != []


def test_the_roadway_is_cut_on_the_world_lattice_shared_with_the_sidewalk() -> None:
    # A piece at tile x = 1: its roadway runs over X 12..18, cut at the lattice of half a tile.
    geo = ColoredGeometry()
    piece = _piece([_side(), None, _side(), None], x=1)
    add_piece(geo, piece, TILE, LOOK, lambda x, z: 0.0)
    xs = {
        round(p[0], 6)
        for p, c in zip(points_of(geo.positions), _colours(geo), strict=True)
        if c == GREY
    }
    assert xs == {12, 15, 18}


def test_the_tile_grid_draws_lines_on_the_edges_of_its_tiles_above_the_ground() -> None:
    grid = build_tile_grid([_piece([_side()] * 4)], TILE, lambda x, z: 0.5 * z, 0, 100, WHITE)
    points = points_of(grid.positions)
    assert min(p[0] for p in points) == pytest.approx(-0.25)
    assert max(p[0] for p in points) == pytest.approx(10.25)
    assert min(p[2] for p in points) == pytest.approx(-0.25)
    assert max(p[2] for p in points) == pytest.approx(10.25)
    for p in points:
        assert p[1] == pytest.approx(0.5 * p[2] + 1)
    assert {c for c in _colours(grid)} == {WHITE}


def test_the_tile_grid_is_empty_for_a_chunk_without_pieces() -> None:
    grid = build_tile_grid([_piece([_side()] * 4)], TILE, lambda x, z: 0.0, 50, 60, WHITE)
    assert grid.indices == []
