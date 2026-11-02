# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/final_boss_shapes.py`."""

import pytest
from helpers.view_probes import drawn

from game.view.bosses.final_boss_shapes import mirrored, shift, sided, turret


def test_shift_moves_a_point_by_a_vector() -> None:
    assert shift([1, 2, 3], [0.5, -1, 2]) == pytest.approx([1.5, 1, 5])


def test_mirrored_builds_a_symmetric_outline_from_its_right_half() -> None:
    right = [[0, 1], [2, 0], [0, -1]]
    outline = mirrored(right)
    # The right half, then the left half without its two points on the axis.
    assert outline == [[0, 1], [2, 0], [0, -1], [-2, 0]]


def test_mirrored_outline_is_symmetric_about_the_axis() -> None:
    right = [[0, 3], [1, 2], [2, 0], [1, -2], [0, -3]]
    outline = mirrored(right)
    xs = sorted(p[0] for p in outline)
    assert xs == sorted(-p[0] for p in outline)


def test_sided_keeps_the_right_side_and_mirrors_for_the_left() -> None:
    outline = [[1, 0], [2, 1]]
    assert sided(outline, 1) == [[1, 0], [2, 1]]
    assert sided(outline, -1) == [[-1, 0], [-2, 1]]


@pytest.mark.parametrize("fires", ["gun", "laser"])
def test_a_turret_aims_its_barrels_forward_firing_its_kind(fires: str) -> None:
    neon = [0.0, 1.0, 0.0]
    at = [4.0, 2.0, -6.0]
    turret_drawing = drawn(lambda p: turret(p, at, 8, [2, neon], fires))
    muzzles = turret_drawing["muzzles"]
    assert [m[1] for m in muzzles] == [fires, fires]
    # Two barrels side by side, ahead of the dome (+Z).
    assert muzzles[0][0][0] != muzzles[1][0][0]
    for m in muzzles:
        assert m[0][2] > at[2] + 8 * 0.6
    parts = turret_drawing["parts"]
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.neon.geometry.colors) > 0
    assert parts.neon.geometry.colors[:3] == neon
