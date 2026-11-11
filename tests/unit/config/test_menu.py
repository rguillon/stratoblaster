# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/menu.py`."""

from config.menu import MENU_CONFIG


def test_ui_flow_08_the_screen_fade_is_a_quarter_second() -> None:
    assert MENU_CONFIG.transition_seconds == 0.25


def test_ui_title_09_the_environment_stops_go_from_the_floor_to_the_sky() -> None:
    stops = MENU_CONFIG.environment.stops
    heights = [stop.at for stop in stops]
    assert heights == sorted(heights)
    assert heights[0] == -1
    assert heights[-1] == 1
    assert MENU_CONFIG.environment.cube_size > 0


def test_ui_title_03_the_cookies_last_a_year_and_frames_are_capped() -> None:
    """The high score cookie's lifetime (UI-TITLE-03, ENG-07), the frame time cap and the glow."""
    assert MENU_CONFIG.cookie_max_age_days == 365
    assert 0 < MENU_CONFIG.max_frame_seconds < 1
    assert MENU_CONFIG.glow.intensity > 0
