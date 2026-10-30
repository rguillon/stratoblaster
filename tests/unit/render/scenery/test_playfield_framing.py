"""Unit tests of `src/render/scenery/playfield_framing.py`."""

import math

import pytest

from core.content.game_definition import LogicalScreen
from render.scenery.playfield_framing import (
    frame_playfield,
    playfield_eye,
    visible_ground,
    visible_half_width,
)
from render.scenery.scenery_look import PlayfieldCameraLook

SCREEN = LogicalScreen(400, 600)


def _camera(tilt_deg: float, fov_deg: float) -> PlayfieldCameraLook:
    return PlayfieldCameraLook(tilt_deg, fov_deg, 100)


def test_the_camera_looks_down_at_the_tilt_and_the_field_of_view() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    assert framing.tilt == pytest.approx(math.radians(30))
    assert framing.half_fov == pytest.approx(math.radians(20))
    assert framing.direction == pytest.approx(
        (-math.cos(math.radians(30)), math.sin(math.radians(30)))
    )


def test_the_camera_height_makes_the_whole_screen_height_fit_the_field_of_view() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    tilt, half = framing.tilt, framing.half_fov
    # The rays to the bottom and top edges of the playfield cross the flight plane at its
    # distances: their span is the screen height.
    span = math.tan(tilt + half) - math.tan(tilt - half)
    assert framing.height * span == pytest.approx(SCREEN.height)
    assert framing.back == pytest.approx(-framing.height * math.tan(tilt - half))


def test_a_camera_that_does_not_see_below_the_horizon_is_refused() -> None:
    with pytest.raises(ValueError, match="below the horizon"):
        frame_playfield(SCREEN, _camera(80, 40))
    with pytest.raises(ValueError, match="below the horizon"):
        frame_playfield(SCREEN, _camera(-80, 40))


def test_a_camera_with_no_field_of_view_is_refused() -> None:
    with pytest.raises(ValueError, match="below the horizon"):
        frame_playfield(SCREEN, _camera(30, 0))


def test_the_eye_is_over_the_centre_line_behind_the_bottom_edge() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    eye = playfield_eye(SCREEN, framing)
    assert (eye.x, eye.y) == (200, framing.back)
    assert eye.height == framing.height


def test_the_ground_seen_reaches_further_the_lower_it_lies() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    raised = visible_ground(framing, 400 / 600, camera_y=100, low=50, high=50)
    flat = visible_ground(framing, 400 / 600, camera_y=100, low=0, high=0)
    assert flat.z_far > raised.z_far
    assert flat.z_far == pytest.approx(100 * math.tan(framing.tilt + framing.half_fov))
    assert flat.half_width > raised.half_width > 0


def test_the_ground_window_is_empty_when_the_ground_is_at_the_camera() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    window = visible_ground(framing, 1, camera_y=5, low=5, high=5)
    assert window.z_far == 0
    assert window.half_width == 0


def test_less_of_the_playfield_is_seen_at_the_bottom_than_at_the_top() -> None:
    framing = frame_playfield(SCREEN, _camera(30, 40))
    bottom = visible_half_width(framing, 400 / 600, 0)
    top = visible_half_width(framing, 400 / 600, 600)
    assert 0 < bottom < top
    middle = visible_half_width(framing, 400 / 600, 300)
    assert bottom < middle < top
