"""Unit tests of `src/game/view/bosses/boss_frame.py`: the frame a shed armour region leaves (its
floor and ribs, BOSS-44, D-224), and the pylons and bridges that hold pieces up (BOSS-52,
D-227)."""

from typing import Any

import pytest

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.hidden_weapons import armour_region
from game.view.bosses.boss_armour import cut_armour
from game.view.bosses.boss_frame import (
    draw_bridge,
    draw_pylon,
    floor_height,
    floor_triangles,
    frame_drawings,
    frame_segments,
    longest_two,
)
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.shatter import triangles, up_facing
from render.geometry.solids import Placement

GREY = [0.5, 0.5, 0.5]

WING = armour_region("wings", 1, [[10, -20], [50, -20], [50, 20], [10, 20]], "wing")


def _plane(p: Any) -> None:
    """A wide, flat delta: a slab 120 x 60, a fuselage box on it, a muzzle and a reactor."""
    p.hull.box([120, 4, 60], GREY, Placement([0, -2, 0]))
    p.flesh.box([12, 10, 60], GREY, Placement([0, 2, 0]))
    p.neon.box([2, 1, 50], GREY, Placement([40, 2, 0]))
    p.muzzle([0, 0, 30])
    p.reactor([0, 0, -30], 3)


def _drawn(draw: Any) -> list[Any]:
    parts = collect_parts(draw)["parts"]
    return triangles(parts.hull.geometry) + triangles(parts.neon.geometry)


def test_longest_two_picks_the_two_longest_segments() -> None:
    segs = [[[0, 0], [0, n]] for n in [3, 9, 1, 7, 4]]
    assert [s[1][1] for s in longest_two(segs)] == [9, 7]
    assert longest_two(segs[:1]) == segs[:1]


def test_a_pylon_reaches_from_its_floor_to_the_piece() -> None:
    drawn = _drawn(lambda p: draw_pylon(p, 0, [3, 4, 10, 6], GREY))
    ys = [v.position[1] for t in drawn for v in t]
    assert min(ys) == pytest.approx(0) and max(ys) == pytest.approx(10)
    on_deck = _drawn(lambda p: draw_pylon(p, 0, [3, 4, 10, 6, 5], GREY))
    assert min(v.position[1] for t in on_deck for v in t) == pytest.approx(5)
    assert _drawn(lambda p: draw_pylon(p, 0, [3, 4, 0.1, 6], GREY)) == []


def test_a_bridge_runs_along_the_floor_then_up_to_its_end() -> None:
    drawn = _drawn(lambda p: draw_bridge(p, [[0, 0, 0], [20, 6, 0]], GREY))
    xs = [v.position[0] for t in drawn for v in t]
    ys = [v.position[1] for t in drawn for v in t]
    assert max(xs) >= 20 and min(xs) <= 0
    assert max(ys) >= 6


def test_the_frame_floor_lies_flat_and_dark_under_the_armour() -> None:
    tris = cut_armour(_plane, [WING]).regions[0]["hull"]
    y = floor_height(tris)
    assert y == pytest.approx(-2 + BOSS_LOOK.frame.lift)
    floor = floor_triangles(tris, y)
    assert floor and all(v.position[1] == y for t in floor for v in t)
    assert all(up_facing(t, 0.9) for t in floor)
    assert all(v.color[:3] == BOSS_LOOK.frame.floor for t in floor for v in t)


def test_the_frame_ribs_lie_within_the_armour_top_view() -> None:
    tris = cut_armour(_plane, [WING]).regions[0]["hull"]
    segments = frame_segments(tris, "wing")
    assert len(segments) >= 6
    for a, b in segments:
        for x in (a[0], b[0]):
            assert 10 - 4 <= abs(x) <= 50 + 4
    assert frame_segments([], "wing") == []
    floor, ribs = frame_drawings(tris, "wing", [1, 0, 1])
    drawn_floor = collect_parts(floor)["parts"]
    drawn_ribs = collect_parts(ribs)["parts"]
    assert drawn_floor.hull.geometry.positions and not drawn_floor.neon.geometry.positions
    assert drawn_ribs.hull.geometry.positions and drawn_ribs.neon.geometry.positions
