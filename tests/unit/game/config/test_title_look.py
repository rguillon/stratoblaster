# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/title_look.py`."""

from game.config.title_look import NEON, STREAK_COLORS, TITLE_LOOK, WINDOW_COLORS


def test_ui_title_07_the_title_scene_has_a_seed_and_a_neon_intensity() -> None:
    """Also UI-TITLE-10 (the neon intensity)."""
    assert isinstance(TITLE_LOOK.seed, int)
    assert TITLE_LOOK.neonIntensity > 0


def test_ui_title_08_neon_and_window_colours_are_rgb_in_range() -> None:
    for color in NEON + WINDOW_COLORS + STREAK_COLORS:
        assert len(color) == 3
        assert all(0 <= c <= 1 for c in color)


def _stop_colors() -> list[list[float]]:
    return [stop["color"] for stop in TITLE_LOOK.sky["stops"]]


def test_ui_title_08_the_sky_haze_and_trench_stay_dark_and_red_free() -> None:
    """The sky's glow, the haze and the trench's floor and walls are dark.

    No channel is above 0.35, and they are never red, magenta or violet (red no more than green or
    blue).
    """
    dark = [
        *_stop_colors(),
        TITLE_LOOK.horizon,
        *TITLE_LOOK.trench.colors.values(),
    ]
    for r, g, b in dark:
        assert max(r, g, b) <= 0.35, (r, g, b)
        assert r <= g, (r, g, b)
        assert r <= b, (r, g, b)


def test_ui_title_08_the_neon_and_window_colours_stay_bright() -> None:
    """The neon, the lit slots and the streaks are bright: brightest channel at least 0.8."""
    for r, g, b in NEON + WINDOW_COLORS + STREAK_COLORS:
        assert max(r, g, b) >= 0.8, (r, g, b)
