"""Unit tests of `src/game/view/props/city_props.py`."""

import pytest
from helpers.geometry_checks import check_colored

from game.view.props.city_props import window_bands
from render.geometry.solids import SolidBuilder

WHITE = [1.0, 0.9, 0.5]


def bands_of(**changes):
    options = {
        "size": [10.0, 10.0],
        "span": [0.0, 20.0],
        "gap": 5.0,
        "band": 2.0,
        "color": WHITE,
        "at": [0.0, 0.0],
    }
    options.update(changes)
    lights = SolidBuilder(True)
    window_bands(
        lights,
        options["size"],
        options["span"],
        options["gap"],
        options["band"],
        options["color"],
        options["at"],
    )
    return lights.geometry


def test_p15_r09_window_bands_are_one_quad_per_face_and_row():
    geo = bands_of()
    # Rows from y 0 to 20, every 5, each 2 high: four rows (0, 5, 10, 15) on four faces, one quad
    # (four vertices, two triangles) each.
    assert check_colored(geo) == 4 * 4 * 4
    assert len(geo.indices) // 3 == 4 * 4 * 2


def test_p15_r09_no_window_bands_on_a_span_too_short_for_a_row():
    geo = bands_of(span=[0.0, 0.0])
    assert len(geo.positions) == 0


@pytest.mark.parametrize(("gap", "rows"), [(5.0, 4), (10.0, 2), (20.0, 1)])
def test_p15_r09_a_wider_gap_makes_fewer_rows(gap, rows):
    assert len(bands_of(gap=gap).positions) == rows * 4 * 4 * 3
