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


def test_ui_ship_03_the_ring_is_neon_blue_green_not_acid_yellow() -> None:
    """The ring under the highlighted ship is the menus' neon cyan (UI-LOOK-03, D-198): no red and
    a blue-green hue, where the old acid yellow had no blue."""
    red, green, blue = MENU_CONFIG.ship_select.ring.color
    assert red == 0
    assert blue > 0.5
    assert green > 0.5
    assert (red, green, blue) != (1, 0.92, 0.05)
