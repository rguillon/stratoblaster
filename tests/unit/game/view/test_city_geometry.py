"""Unit tests of `src/game/view/city_geometry.py`."""

import pytest
from helpers.geometry_checks import bounds, check_colored

from core.math.rng import create_rng
from game.config.title_look import TITLE_LOOK as LOOK
from game.view.city_geometry import build_city_chunk, build_rain, build_skyline


def test_the_skyline_is_flat_silhouettes_standing_on_the_ground():
    towers = build_skyline(LOOK.skyline, create_rng(1))
    check_colored(towers["structure"])
    low, _ = bounds(towers["structure"])
    assert low[1] == pytest.approx(0)
    # Flat in the XY plane: every vertex lies at the same depth.
    assert set(towers["structure"].positions[2::3]) == {0}


def test_the_skyline_spans_the_half_width_it_is_given():
    towers = build_skyline(LOOK.skyline, create_rng(1))
    low, high = bounds(towers["structure"])
    half = LOOK.skyline.halfWidth
    assert low[0] >= -half - 1e-6
    assert high[0] >= half - LOOK.skyline.width[1] - 1e-6


def test_the_skyline_is_the_same_for_the_same_seed():
    a = build_skyline(LOOK.skyline, create_rng(9))
    b = build_skyline(LOOK.skyline, create_rng(9))
    assert a["structure"].positions == b["structure"].positions


def test_the_city_chunk_spans_its_length_along_z():
    chunk = build_city_chunk(LOOK.city, create_rng(2))
    check_colored(chunk["structure"])
    low, high = bounds(chunk["structure"])
    assert low[2] >= -1e-6
    assert high[2] <= LOOK.city["length"] + 1e-6


def test_two_chunks_of_the_same_seed_are_the_same_city():
    a = build_city_chunk(LOOK.city, create_rng(4))
    b = build_city_chunk(LOOK.city, create_rng(4))
    assert a["structure"].positions == b["structure"].positions
    assert a["lights"].colors == b["lights"].colors


def test_a_city_chunk_has_lit_windows_and_neon():
    chunk = build_city_chunk(LOOK.city, create_rng(5))
    assert len(chunk["lights"].positions) > 0
    check_colored(chunk["lights"])


def test_rain_is_one_streak_per_drop_drawn_twice_for_a_seamless_loop():
    geo = build_rain(LOOK.rain, create_rng(3))
    check_colored(geo)
    # Each drop is a quad (4 vertices), drawn twice, stacked.
    assert len(geo.positions) // 3 == LOOK.rain["count"] * 2 * 4


def test_rain_falls_within_the_height_it_is_given():
    geo = build_rain(LOOK.rain, create_rng(3))
    _, high = bounds(geo)
    assert high[1] <= 2 * LOOK.rain["height"] + LOOK.rain["length"][1] + 1e-6
