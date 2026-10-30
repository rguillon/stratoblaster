"""Unit tests of `src/render/scenery/window_atlas.py` (D-210)."""

from typing import Any

import pytest
from helpers.render_fakes import FakeTypedArray

from game.config.record import record
from game.config.window_look import WINDOW_ATLAS
from render.scenery import window_atlas
from render.scenery.window_atlas import (
    atlas_cells,
    kept_window_atlas,
    style_columns,
    window_atlas_pixels,
)

# A small atlas: 2 styles of 2 columns, 4 rows of 8-pixel cells.
LOOK = record(
    {
        "size": 32,
        "cell": 8,
        "styles": [
            {"window": [2, 2, 6, 6], "lit": 1},
            {"window": [1, 1, 7, 7], "lit": 0},
        ],
        "colors": [[1, 0.5, 0.25]],
        "brightness": [1, 1],
        "blinds": 0,
        "dark": [0, 0, 0.2],
        "glass": [0.1, 0.1, 0.1],
        "halo": 0.5,
        "seed": 3,
    }
)


@pytest.fixture(autouse=True)
def _typed_arrays(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(window_atlas, "_uint8_array", FakeTypedArray)


def _pixel(pixels: Any, x: int, y: int) -> list[int]:
    i = (y * LOOK.size + x) * 4
    return list(pixels[i : i + 4])


def test_d210_the_atlas_has_cells_in_one_band_of_columns_per_style():
    assert atlas_cells(LOOK) == 4
    assert style_columns(LOOK) == 2
    assert atlas_cells(WINDOW_ATLAS) == 64
    assert style_columns(WINDOW_ATLAS) == 16


def test_d210_a_lit_window_shows_its_light_opaque():
    pixels = window_atlas_pixels(LOOK)
    assert len(pixels) == 32 * 32 * 4
    # The first style is always lit, its window from (2, 2) to (6, 6) in each cell.
    assert _pixel(pixels, 3, 3) == [255, 128, 64, 255]
    assert _pixel(pixels, 8 + 5, 16 + 2) == [255, 128, 64, 255]


def test_d210_a_lit_window_has_a_halo_and_the_wall_between_shows_through():
    pixels = window_atlas_pixels(LOOK)
    halo = _pixel(pixels, 1, 3)
    assert halo[3] == 128
    assert halo[0] < 255
    assert _pixel(pixels, 0, 0)[3] == 0


def test_d210_a_dark_window_is_opaque_and_dark():
    pixels = window_atlas_pixels(LOOK)
    # The second style is never lit: its cells start at column 2 (pixel 16).
    assert _pixel(pixels, 16 + 3, 3) == [0, 0, 51, 255]
    assert _pixel(pixels, 16, 0)[3] == 0


def test_d210_a_blind_dims_the_top_half_of_a_lit_window():
    look = record({**LOOK, "blinds": 1})
    pixels = window_atlas_pixels(look)
    assert _pixel(pixels, 3, 2)[0] == 255
    assert _pixel(pixels, 3, 5)[0] < 255


def test_d210_the_atlas_is_made_once_per_look():
    assert kept_window_atlas(LOOK) is kept_window_atlas(LOOK)
