"""Unit tests of `src/game/view/props/window_facades.py` (D-210)."""

import pytest
from helpers.geometry_checks import bounds, check_colored

from core.math.rng import create_rng
from game.config.window_look import WINDOW_ATLAS, WINDOW_CELL, WINDOW_OFFSET
from game.view.props.window_facades import facade_windows, round_windows, tint_of, wall_uv
from render.geometry.textured import QuadBuilder

CELLS = 64
BAND = 16


def test_d210_the_tint_is_half_the_window_colour_over_white():
    assert tint_of([1.0, 0.5, 0.0]) == pytest.approx([1.0, 0.75, 0.5])


def test_d210_a_wall_maps_on_one_cell_per_window_in_its_style_band():
    random = create_rng(1)
    for _ in range(50):
        u0, v0, u1, v1 = wall_uv(random, 2, 5 * WINDOW_CELL.width, 4 * WINDOW_CELL.height)
        assert (u1 - u0) * CELLS == pytest.approx(5)
        assert (v1 - v0) * CELLS == pytest.approx(4)
        assert u0 * CELLS >= 2 * BAND
        assert u1 * CELLS <= 3 * BAND


def test_d210_a_wall_wider_than_a_band_gets_the_whole_band():
    u0, _, u1, _ = wall_uv(create_rng(1), 0, 100 * WINDOW_CELL.width, 3)
    assert (u0, u1) == (0, BAND / CELLS)


def test_d210_a_tiny_wall_gets_one_cell():
    u0, v0, u1, v1 = wall_uv(create_rng(1), 1, 0.5, 0.5)
    assert (u1 - u0, v1 - v0) == pytest.approx((1 / CELLS, 1 / CELLS))


def test_d210_a_box_gets_one_quad_per_wall_just_off_it():
    quads = QuadBuilder()
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 6.0], [1.0, 9.0], [1.0, 1.0, 1.0])
    geo = quads.geometry
    check_colored(geo)
    assert len(geo.indices) == 4 * 6
    assert len(geo.uvs) == 2 * len(geo.positions) // 3
    low, high = bounds(geo)
    assert low == pytest.approx([-5 - WINDOW_OFFSET, 1.0, -3 - WINDOW_OFFSET])
    assert high == pytest.approx([5 + WINDOW_OFFSET, 9.0, 3 + WINDOW_OFFSET])


def _bands(geo: object) -> list[int]:
    """The style band of each quad of `geo`."""
    uvs = geo.uvs  # type: ignore[attr-defined]
    return [int(min(uvs[i], uvs[i + 4]) * CELLS) // BAND for i in range(0, len(uvs), 8)]


def test_d210_a_box_is_one_style_unless_mixed():
    for seed in range(10):
        quads = QuadBuilder()
        facade_windows(quads, create_rng(seed), [0.0, 0.0, 10.0, 10.0], [0.0, 9.0], [1, 1, 1])
        assert len(set(_bands(quads.geometry))) == 1
    mixed = set()
    for seed in range(10):
        quads = QuadBuilder()
        facade_windows(quads, create_rng(seed), [0.0, 0.0, 10.0, 10.0], [0.0, 9.0], [1, 1, 1], True)
        mixed.add(len(set(_bands(quads.geometry))))
    assert max(mixed) > 1


def test_d210_a_wall_too_low_or_too_narrow_gets_no_quad():
    quads = QuadBuilder()
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 6.0], [1.0, 1.5], [1, 1, 1])
    assert quads.geometry.indices == []
    facade_windows(quads, create_rng(2), [0.0, 0.0, 10.0, 0.5], [1.0, 6.0], [1, 1, 1])
    assert len(quads.geometry.indices) == 2 * 6


def test_d210_the_atlas_has_as_many_bands_as_styles():
    assert len(WINDOW_ATLAS.styles) * BAND == CELLS


def test_d210_a_round_tower_gets_one_quad_per_facet_following_its_taper():
    quads = QuadBuilder()
    tower = [2.0, 3.0, 5.0, 20.0, 4.0, 2.0, 6]
    round_windows(quads, create_rng(2), tower, [5.0, 25.0], [1.0, 1.0, 1.0])
    geo = quads.geometry
    check_colored(geo)
    assert len(geo.indices) == 6 * 6
    # The first facet's first corners: at the foot, radius 4 (+ offset); at the top, radius 2.
    assert geo.positions[0:3] == pytest.approx([2.0 + 4 + WINDOW_OFFSET, 5.0, 3.0])
    assert geo.positions[3:6] == pytest.approx([2.0 + 2 + WINDOW_OFFSET, 25.0, 3.0])
    assert len(set(_bands(geo))) == 1


def test_d210_a_round_tower_too_low_gets_no_windows():
    quads = QuadBuilder()
    round_windows(quads, create_rng(2), [0.0, 0.0, 0.0, 10.0, 3.0, 3.0, 8], [2.0, 2.5], [1, 1, 1])
    assert quads.geometry.indices == []
