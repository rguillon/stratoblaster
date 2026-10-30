"""Unit tests of `src/config/menu.py`."""

from config.menu import MENU_CONFIG


def test_p01_r15_the_screen_fade_is_a_quarter_second() -> None:
    assert MENU_CONFIG.transition_seconds == 0.25


def test_p01_r06_the_highlighted_ship_is_larger_than_the_dimmed_ones() -> None:
    ships = MENU_CONFIG.ship_select
    assert ships.highlight_scale > ships.dim_scale > 0


def test_p01_r06_the_camera_and_lights_are_positive_where_they_should_be() -> None:
    ships = MENU_CONFIG.ship_select
    assert ships.camera.horizontal_fov > 0
    assert ships.camera.framing_margin >= 1
    assert ships.lights.spot_intensity > ships.lights.ambient_intensity > 0
    assert ships.ring.diameter > ships.ring.thickness > 0


def test_p01_r06_the_environment_stops_go_from_the_floor_to_the_sky() -> None:
    stops = MENU_CONFIG.environment.stops
    heights = [stop.at for stop in stops]
    assert heights == sorted(heights)
    assert heights[0] == -1
    assert heights[-1] == 1
    assert MENU_CONFIG.environment.cube_size > 0


def test_p01_r05_the_cookies_last_a_year_and_frames_are_capped() -> None:
    assert MENU_CONFIG.cookie_max_age_days == 365
    assert 0 < MENU_CONFIG.max_frame_seconds < 1
    assert MENU_CONFIG.glow.intensity > 0
