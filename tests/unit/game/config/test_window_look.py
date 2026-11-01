"""Unit tests of `src/game/config/window_look.py`."""

from game.config.window_look import WINDOW_ATLAS

# The atlas is 64 cells wide; D-215: 15 columns a window style, the doors' bands taking the last 4.
CELLS = 64
BAND = 15


def test_d210_the_atlas_has_as_many_bands_as_styles():
    assert len(WINDOW_ATLAS.styles) * BAND + len(WINDOW_ATLAS.doors) * 2 == CELLS
