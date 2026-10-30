"""Unit tests of `src/game/view/bosses/final_boss_shapes.py`."""

import pytest

from game.view.bosses.final_boss_shapes import mirrored, shift, sided


def test_shift_moves_a_point_by_a_vector():
    assert shift([1, 2, 3], [0.5, -1, 2]) == pytest.approx([1.5, 1, 5])


def test_mirrored_builds_a_symmetric_outline_from_its_right_half():
    right = [[0, 1], [2, 0], [0, -1]]
    outline = mirrored(right)
    # The right half, then the left half without its two points on the axis.
    assert outline == [[0, 1], [2, 0], [0, -1], [-2, 0]]


def test_mirrored_outline_is_symmetric_about_the_axis():
    right = [[0, 3], [1, 2], [2, 0], [1, -2], [0, -3]]
    outline = mirrored(right)
    xs = sorted(p[0] for p in outline)
    assert xs == sorted(-p[0] for p in outline)


def test_sided_keeps_the_right_side_and_mirrors_for_the_left():
    outline = [[1, 0], [2, 1]]
    assert sided(outline, 1) == [[1, 0], [2, 1]]
    assert sided(outline, -1) == [[-1, 0], [-2, 1]]
