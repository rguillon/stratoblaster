"""Unit tests of `src/render/geometry/islands.py`: which pieces of a model hold together (D-227)."""

from render.geometry.islands import bounds_of, holding, loose_triangles, pieces, touch
from render.geometry.shatter import triangles
from render.geometry.solids import Placement, SolidBuilder

WHITE = [1.0, 1.0, 1.0]


def _boxes(*places: list[float]) -> list:
    b = SolidBuilder()
    for at in places:
        b.box([4, 2, 4], WHITE, Placement(at))
    return triangles(b.geometry)


def test_a_box_is_one_piece_and_two_apart_are_two() -> None:
    assert len(pieces(_boxes([0, 0, 0]))) == 1
    assert len(pieces(_boxes([0, 0, 0], [20, 0, 0]))) == 2


def test_bounds_and_touch() -> None:
    b = bounds_of(_boxes([0, 0, 0]))
    assert b == [-2, 0, -2, 2, 2, 2]
    assert touch(b, [2.3, 0, 0, 5, 1, 1], 0.5)
    assert not touch(b, [3, 0, 0, 5, 1, 1], 0.5)


def test_holding_groups_boxes_touching_through_others() -> None:
    boxes = [[0, 0, 0, 1, 1, 1], [1, 0, 0, 2, 1, 1], [2, 0, 0, 3, 1, 1], [9, 9, 9, 10, 10, 10]]
    assert holding(boxes, 0.1) == [0, 0, 0, 1]


def test_loose_triangles_are_those_off_the_object_at_the_centre() -> None:
    # Two stacked boxes (touching) and one floating above them.
    tris = _boxes([0, 0, 0], [0, 2, 0], [0, 10, 0])
    loose = loose_triangles(tris, 0.3)
    assert sum(loose) == len(tris) // 3
    assert all(tris[i][0].position[1] >= 10 for i in range(len(tris)) if loose[i])
    assert loose_triangles([], 0.3) == []


def test_the_main_object_is_the_one_at_the_centre_not_the_biggest() -> None:
    # A small box at the centre, and three stacked far off.
    tris = _boxes([0, 0, 0], [40, 0, 0], [40, 2, 0], [40, 4, 0])
    loose = loose_triangles(tris, 0.3)
    assert all(loose[i] == (tris[i][0].position[0] > 20) for i in range(len(tris)))
