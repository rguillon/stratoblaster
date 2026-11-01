"""Unit tests of `src/game/config/title_look.py`."""

from game.config.title_look import NEON, TITLE_LOOK, WINDOW_COLORS


def test_ui_title_07_the_title_scene_has_a_seed_and_a_neon_intensity() -> None:
    """Also UI-TITLE-10 (the neon intensity)."""
    assert isinstance(TITLE_LOOK.seed, int)
    assert TITLE_LOOK.neonIntensity > 0


def test_ui_title_08_neon_and_window_colours_are_rgb_in_range() -> None:
    for color in NEON + WINDOW_COLORS:
        assert len(color) == 3
        assert all(0 <= c <= 1 for c in color)
