# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/menu.py`."""

from config.menu import MENU_CONFIG


def test_ui_flow_08_the_screen_fade_is_a_quarter_second() -> None:
    assert MENU_CONFIG.transition_seconds == 0.25


def test_ui_ship_03_the_highlighted_ship_is_larger_than_the_dimmed_ones() -> None:
    ships = MENU_CONFIG.ship_select
    assert ships.highlight_scale > ships.dim_scale > 0


def test_ui_ship_01_the_camera_and_lights_are_positive_where_they_should_be() -> None:
    """Also UI-SHIP-03: the key light and the ring of the highlighted ship."""
    ships = MENU_CONFIG.ship_select
    assert ships.camera.horizontal_fov > 0
    assert ships.camera.framing_margin >= 1
    assert ships.lights.spot_intensity > ships.lights.ambient_intensity > 0
    assert ships.ring.diameter > ships.ring.thickness > 0


def test_ui_ship_01_the_environment_stops_go_from_the_floor_to_the_sky() -> None:
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


def test_ui_ship_03_the_ring_is_the_menus_hot_pink() -> None:
    """The ring under the highlighted ship is the menus' hot pink (UI-LOOK-03, D-323).

    Full red, some blue, little green: pink, not the old cyan or acid yellow.
    """
    red, green, blue = MENU_CONFIG.ship_select.ring.color
    assert red == 1
    assert blue > 0.5
    assert green < 0.5
