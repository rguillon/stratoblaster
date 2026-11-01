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


def _stop_colors() -> list[list[float]]:
    return [stop["color"] for stop in TITLE_LOOK.sky["stops"]]


def test_ui_title_08_the_sky_haze_and_towers_stay_dark_and_red_free() -> None:
    """The sky's glow, the haze and the towers, streets and signs panels: dark (no channel above
    0.35) and never red, magenta or violet (red no more than green or blue)."""
    dark = [
        *_stop_colors(),
        TITLE_LOOK.horizon,
        TITLE_LOOK.skyline.color,
        *TITLE_LOOK.city.colors.values(),
        TITLE_LOOK.city.street.color,
        TITLE_LOOK.city.signs.panel,
    ]
    for r, g, b in dark:
        assert max(r, g, b) <= 0.35, (r, g, b)
        assert r <= g and r <= b, (r, g, b)


def test_ui_title_08_the_neon_and_window_colours_stay_bright() -> None:
    """The neon signs and the lit windows are bright: their brightest channel is at least 0.8."""
    for r, g, b in NEON + WINDOW_COLORS:
        assert max(r, g, b) >= 0.8, (r, g, b)
