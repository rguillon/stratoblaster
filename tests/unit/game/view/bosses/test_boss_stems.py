"""Unit tests of `src/game/view/bosses/boss_stems.py` and the frames' pylons and bridges: what holds
a boss's pieces to it (D-227)."""

import pytest

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.hidden_weapons import armour_region
from game.view.bosses.boss_armour import rooted, supports_in
from game.view.bosses.boss_frame import draw_bridge, draw_pylon
from game.view.bosses.boss_stems import stems_drawing, stems_for, surface_below
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.islands import loose_triangles
from render.geometry.shatter import triangles
from render.geometry.solids import Placement, SolidBuilder

GREY = [0.5, 0.5, 0.5]


def _tris(*boxes: tuple[list[float], list[float]]) -> list:
    b = SolidBuilder()
    for size, at in boxes:
        b.box(size, GREY, Placement(at))
    return triangles(b.geometry)


def _drawn(draw) -> list:
    parts = collect_parts(draw)["parts"]
    return triangles(parts.hull.geometry) + triangles(parts.neon.geometry)


def test_surface_below_is_the_highest_up_facing_face_under_a_point() -> None:
    deck = _tris(([40, 2, 40], [0, 0, 0]), ([10, 2, 10], [0, 4, 0]))
    assert surface_below(deck, 0, 0, 100) == pytest.approx(6)
    assert surface_below(deck, 15, 0, 100) == pytest.approx(2)
    assert surface_below(deck, 15, 0, 1) is None
    assert surface_below(deck, 50, 0, 100) is None


def test_a_piece_hanging_over_the_hull_gets_a_stem_down_to_it() -> None:
    # (Away from the centre: the main object is the one there.)
    tris = _tris(([60, 2, 60], [0, 0, 0]), ([4, 1, 4], [18, 8, 18]))
    stems = stems_for(tris)
    assert len(stems) == 1
    kind, x, z, low, high, _w = stems[0]
    assert kind == "stem" and (x, z) == pytest.approx((18, 18))
    assert low == pytest.approx(2) and 8 < high < 9
    held = tris + _drawn(stems_drawing(stems, GREY))
    assert not any(loose_triangles(held, BOSS_LOOK.armour.hold))


def test_a_piece_off_the_hull_gets_a_beam_to_it() -> None:
    tris = _tris(([20, 2, 20], [0, 0, 0]), ([4, 2, 4], [30, 0, 0]))
    stems = stems_for(tris)
    assert [s[0] for s in stems] == ["beam"]
    held = tris + _drawn(stems_drawing(stems, GREY))
    assert not any(loose_triangles(held, BOSS_LOOK.armour.hold))
    assert stems_for(_tris(([20, 2, 20], [0, 0, 0]))) == []


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


def test_supports_stand_in_a_region_even_in_part_and_root_on_what_lasts() -> None:
    region = armour_region("wings", 1, [[10, -10], [30, -10], [30, 10], [10, 10]], "wing")
    # Model space: +X is the screen's left (a region's X right is model -X).
    inside = [-20, 0, 5, 4]
    edge = [-8, 0, 5, 4]
    away = [-50, 0, 5, 4]
    assert supports_in(region, [inside, edge, away]) == [inside, edge]
    deck = _tris(([10, 2, 10], [-20, 0, 0]))
    assert rooted([inside, away], deck) == [[-20, 0, 5, 4, pytest.approx(2)], away]
