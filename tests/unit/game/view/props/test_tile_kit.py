"""Unit tests of `src/game/view/props/tile_kit.py`."""

import pytest
from helpers.geometry_checks import bounds, check_colored

from game.config.window_look import WINDOW_OFFSET
from game.view.props.tile_kit import geometry_of, js_remainder, js_round, tile_kit, windows


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(7, 3, 1), (-7, 3, -1), (6, 3, 0), (-6, 3, 0)],
)
def test_p15_r07_js_remainder_takes_the_sign_of_the_dividend(a, b, expected):
    assert js_remainder(a, b) == expected


def test_p15_r07_js_remainder_matches_javascript_for_a_negative_divisor():
    assert js_remainder(5, -3) == 2


@pytest.mark.parametrize(
    ("x", "expected"),
    [(2.4, 2), (2.5, 3), (-2.5, -2), (0, 0), (3.49, 3)],
)
def test_p15_r07_js_round_rounds_halves_up(x, expected):
    assert js_round(x) == expected


def test_p15_r07_a_kit_holds_its_plot_tile_and_seed():
    k = tile_kit(18.0, 12.0, 10, 4)
    assert (k.w, k.d, k.tile, k.seed) == (18.0, 12.0, 10, 4)
    assert k.s is not k.lights


def test_p15_r07_the_random_generator_of_a_kit_is_seeded_by_its_model():
    a = tile_kit(18.0, 12.0, 10, 4)
    b = tile_kit(18.0, 12.0, 10, 4)
    assert [a.random() for _ in range(3)] == [b.random() for _ in range(3)]
    other = tile_kit(18.0, 12.0, 10, 5)
    assert [a.random() for _ in range(3)] != [other.random() for _ in range(3)]


def test_p15_r07_geometry_of_a_kit_is_its_structure_lights_and_windows():
    k = tile_kit(10.0, 10.0, 10, 1)
    prop = geometry_of(k)
    assert prop.structure is k.s.geometry
    assert prop.lights is k.lights.geometry
    assert prop.windows is k.windows.geometry
    check_colored(prop.structure)


def test_d210_windows_put_one_quad_on_each_wall_of_the_block():
    k = tile_kit(10.0, 10.0, 10, 1)
    windows(k, [6.0, 4.0], [1.0, 7.0], [1.0, 0.72, 0.38], [1.0, 2.0])
    geo = k.windows.geometry
    check_colored(geo)
    assert len(geo.indices) == 4 * 6
    low, high = bounds(geo)
    assert low[0] == pytest.approx(1.0 - 3.0 - WINDOW_OFFSET)
    assert high[2] == pytest.approx(2.0 + 2.0 + WINDOW_OFFSET)
    assert (low[1], high[1]) == (1.0, 7.0)
