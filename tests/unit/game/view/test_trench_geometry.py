# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/trench_geometry.py` (UI-TITLE-07)."""

import math

import pytest
from helpers.geometry_checks import bounds, check_colored

from core.math.rng import create_rng
from game.config.title_look import TITLE_LOOK as LOOK
from game.view.trench_geometry import build_streaks, build_trench_chunk


def test_ui_title_07_the_trench_stretch_spans_its_length_between_its_walls() -> None:
    chunk = build_trench_chunk(LOOK.trench, create_rng(2))
    check_colored(chunk["structure"])
    check_colored(chunk["lights"])
    low, high = bounds(chunk["structure"])
    look = LOOK.trench
    assert low[2] == pytest.approx(-look["length"])
    assert high[2] == pytest.approx(0)
    assert low[0] == pytest.approx(-look.halfWidth)
    assert high[0] == pytest.approx(look.halfWidth)
    assert low[1] == pytest.approx(look.floorY)
    assert high[1] == pytest.approx(look.floorY + look.wallHeight)


def test_ui_title_07_the_lights_stay_inside_the_trench() -> None:
    chunk = build_trench_chunk(LOOK.trench, create_rng(5))
    low, high = bounds(chunk["lights"])
    look = LOOK.trench
    assert low[0] >= -look.halfWidth
    assert high[0] <= look.halfWidth
    assert low[2] >= -look["length"] - 1e-6
    assert high[2] <= 1e-6


def test_ui_title_07_the_trench_is_the_same_for_the_same_seed() -> None:
    a = build_trench_chunk(LOOK.trench, create_rng(9))
    b = build_trench_chunk(LOOK.trench, create_rng(9))
    assert a["structure"].positions == b["structure"].positions
    assert a["lights"].colors == b["lights"].colors


def test_ui_title_07_the_streaks_lie_round_the_axis_within_their_stretch() -> None:
    look = LOOK.streaks
    geo = build_streaks(look, create_rng(4))
    check_colored(geo)
    assert len(geo.positions) == look.count * 4 * 3
    xs, ys, zs = geo.positions[0::3], geo.positions[1::3], geo.positions[2::3]
    reach = look.radius[1] + look.width
    for x, y, z in zip(xs, ys, zs, strict=True):
        assert math.hypot(x, y - look.axisY) <= reach
        assert -look["length"] - 1e-6 <= z <= 1e-6


def test_ui_title_07_the_streaks_are_the_same_for_the_same_seed() -> None:
    a = build_streaks(LOOK.streaks, create_rng(6))
    b = build_streaks(LOOK.streaks, create_rng(6))
    assert a.positions == b.positions
