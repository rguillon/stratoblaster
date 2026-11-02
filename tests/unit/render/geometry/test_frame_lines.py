# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/frame_lines.py`.

The ribs of the dark metal frame a boss's shed armour leaves
(docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md).
"""

import math

from render.geometry.frame_lines import Footprint, clip_line, frame_lines

# A 40 x 20 rectangle (x -20..20, z -10..10) in two triangles, one each winding.
RECT = Footprint([[[-20, -10], [20, -10], [20, 10]], [[-20, -10], [-20, 10], [20, 10]]])
# An L: the rectangle's left half and a tall arm.
L_SHAPE = Footprint([
    [[-20, -10], [0, -10], [0, 10]],
    [[-20, -10], [-20, 10], [0, 10]],
    [[0, -10], [20, -10], [20, -5]],
    [[0, -10], [0, -5], [20, -5]],
])


def test_a_footprint_holds_what_its_triangles_cover_and_knows_its_bounds() -> None:
    assert RECT.holds(0, 0)
    assert RECT.holds(19, 9)
    assert not RECT.holds(21, 0)
    assert not RECT.holds(0, 11)
    assert RECT.low == [-20, -10]
    assert RECT.high == [20, 10]
    assert RECT.centre() == [0, 0]
    assert Footprint([]).empty()


def test_wing_frames_have_ribs_across_x_and_two_spars_along_it() -> None:
    lines = frame_lines("wing", RECT, 9, 12)
    ribs = [line for line in lines if line[0][0] == line[1][0]]
    spars = [line for line in lines if line[0][1] == line[1][1]]
    assert len(ribs) == 5
    assert all(-20 < r[0][0] < 20 for r in ribs)
    assert len(spars) == 2


def test_shell_frames_are_a_lattice() -> None:
    lines = frame_lines("shell", RECT, 9, 12)
    spars = [line for line in lines if line[0][1] == line[1][1]]
    assert len(spars) == 3


def test_ring_frames_have_spokes_from_the_middle_and_a_hoop() -> None:
    lines = frame_lines("ring", RECT, 9, 12)
    spokes = [line for line in lines if line[0] == [0, 0]]
    assert len(spokes) == 12
    reach = math.hypot(40, 20) / 2
    assert all(abs(math.hypot(s[1][0], s[1][1]) - reach) < 1e-9 for s in spokes)
    assert len(lines) == 12 + 24


def test_clip_line_keeps_the_pieces_over_the_footprint() -> None:
    pieces = clip_line([[-30, 0], [30, 0]], RECT, 1, 3)
    assert len(pieces) == 1
    (a, b) = pieces[0]
    assert -20 <= a[0] <= -19
    assert 19 <= b[0] <= 20
    # The L leaves a gap along z = 0 past x = 0; along z = -8 it is whole.
    assert len(clip_line([[-30, 0], [30, 0]], L_SHAPE, 1, 3)) == 1
    assert clip_line([[-30, 0], [30, 0]], L_SHAPE, 1, 3)[0][1][0] <= 0.5
    gap = Footprint([
        [[-20, -1], [-5, -1], [-5, 1]],
        [[-20, -1], [-20, 1], [-5, 1]],
        [[5, -1], [20, -1], [20, 1]],
        [[5, -1], [5, 1], [20, 1]],
    ])
    assert len(clip_line([[-30, 0], [30, 0]], gap, 1, 3)) == 2
    # Pieces under `least` are dropped.
    assert clip_line([[-30, 0], [30, 0]], gap, 1, 20) == []
