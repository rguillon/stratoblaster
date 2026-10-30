"""Unit tests of `src/render/geometry/outline.py`."""

import pytest

from render.geometry.outline import (
    hypot2,
    hypot3,
    inset_outline,
    reversed_copy,
    ring_at,
)

SQUARE = [[-1, -1], [1, -1], [1, 1], [-1, 1]]


def test_hypot_matches_the_euclidean_length() -> None:
    assert hypot2(3, 4) == pytest.approx(5)
    assert hypot3(2, 3, 6) == pytest.approx(7)


def test_reversed_copy_does_not_touch_the_input() -> None:
    items = [1, 2, 3]
    assert reversed_copy(items) == [3, 2, 1]
    assert items == [1, 2, 3]


def test_ring_at_wraps_around_both_ways() -> None:
    ring = ["a", "b", "c"]
    assert [ring_at(ring, i) for i in (-1, 0, 2, 3, 4)] == ["c", "a", "c", "a", "b"]


def test_ring_at_refuses_an_empty_ring() -> None:
    with pytest.raises(ValueError, match="Empty ring"):
        ring_at([], 0)


def test_inset_of_a_square_moves_each_corner_diagonally_by_the_distance() -> None:
    inset = inset_outline(SQUARE, 0.1)
    expected = [[-0.9, -0.9], [0.9, -0.9], [0.9, 0.9], [-0.9, 0.9]]
    for got, want in zip(inset, expected, strict=True):
        assert got == pytest.approx(want)


def test_inset_of_a_sharp_corner_is_capped_at_max_miter() -> None:
    # A thin spike: its tip (the point at x = 10) is far from the other corners.
    spike = [[0, -1], [10, 0], [0, 1], [-1, 0]]
    tip_free = inset_outline(spike, 0.5)[1]
    tip_capped = inset_outline(spike, 0.5, max_miter=1)[1]
    # Free, the tip moves 3 × distance inwards; capped at 1 × distance, it stays closer.
    assert tip_free[0] == pytest.approx(10 - 1.5)
    assert tip_capped[0] == pytest.approx(10 - 0.5)


def test_a_corner_with_no_bisector_stays_where_it_is() -> None:
    # The two edges at the middle point fold back on each other: no bisector.
    folded = [[0, 0], [1, 0], [0, 0], [-1, 1]]
    assert inset_outline(folded, 0.2)[1] == [1, 0]
