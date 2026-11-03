# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_frame.py`.

The frame a shed armour region leaves (its floor and ribs, BOSS-44), drawn from the region's
outlines (D-254).
"""

from typing import Any

import pytest

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_frame import (
    FLOOR,
    footprint_of,
    frame_drawings,
    frame_segments,
    longest_two,
)
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.mesh_triangles import triangles

# A wing on the boss's right, in model space (XZ): x -50..-10, z -20..20.
WING = [[-10.0, -20.0], [-50.0, -20.0], [-50.0, 20.0], [-10.0, 20.0]]


def _drawn(draw: Any) -> Any:
    return collect_parts(draw)["parts"]


def test_longest_two_picks_the_two_longest_segments() -> None:
    segs = [[[0, 0], [0, n]] for n in [3, 9, 1, 7, 4]]
    assert [s[1][1] for s in longest_two(segs)] == [9, 7]
    assert longest_two(segs[:1]) == segs[:1]


def test_the_footprint_covers_the_outlines_whatever_their_winding() -> None:
    shape = footprint_of([WING])
    assert shape.holds(-30, 0)
    assert not shape.holds(0, 0)
    assert footprint_of([list(reversed(WING))]).holds(-30, 0)
    assert footprint_of([]).empty()


def test_the_frame_ribs_lie_within_the_armour_top_view() -> None:
    segments = frame_segments([WING], "wing")
    assert len(segments) >= 6
    for a, b in segments:
        for x in (a[0], b[0]):
            assert 10 - 4 <= abs(x) <= 50 + 4
        for z in (a[1], b[1]):
            assert abs(z) <= 20 + 4
    assert frame_segments([], "wing") == []


def test_the_frame_floor_lies_flat_and_dark_under_the_armour_its_ribs_on_it() -> None:
    floor, ribs = frame_drawings([WING], "shell", [1, 0, 1], 3.0)
    drawn_floor = _drawn(floor)
    tris = triangles(drawn_floor.hull.geometry)
    assert tris
    ys = [v.position[1] for t in tris for v in t]
    assert max(ys) == pytest.approx(3.0)
    assert min(ys) == pytest.approx(3.0 - FLOOR)
    assert all(v.color[:3] == BOSS_LOOK.frame.floor for t in tris for v in t)
    assert all(-50 <= v.position[0] <= -10 for t in tris for v in t)
    assert not drawn_floor.neon.geometry.positions
    drawn_ribs = _drawn(ribs)
    rib_ys = drawn_ribs.hull.geometry.positions[1::3]
    assert min(rib_ys) == pytest.approx(3.0)
    # One rib in three carries a neon seam; the pipes lie along the longest ribs.
    assert drawn_ribs.neon.geometry.positions
    assert len(drawn_ribs.hull.geometry.indices) > 0
