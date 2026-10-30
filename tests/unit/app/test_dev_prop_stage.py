"""Unit tests of `src/app/dev_prop_stage.py` (D-205: the props viewer's floor ruled in blocks)."""

import math
from types import SimpleNamespace

import pytest

from app.dev_prop_stage import block_centre, blocks_of, close_up_distance, game_distance


def test_d205_a_footprint_covers_whole_blocks_at_least_one() -> None:
    assert blocks_of(0, 10) == 1
    assert blocks_of(10, 10) == 1
    assert blocks_of(10.000000001, 10) == 1
    assert blocks_of(10.5, 10) == 2
    assert blocks_of(30, 10) == 3


def test_d205_an_even_footprint_is_centred_on_a_line_an_odd_one_in_a_square() -> None:
    assert block_centre(2, 10) == 0
    assert block_centre(1, 10) == 5
    assert block_centre(3, 10) == 5


def test_d205_the_game_distance_is_the_cameras_down_its_view_in_ground_units() -> None:
    camera = SimpleNamespace(tiltDeg=0.0, fovDeg=60.0, flightAltitude=100.0, groundScale=2.0)
    game = SimpleNamespace(
        screen=SimpleNamespace(width=480, height=720),
        view=SimpleNamespace(scenery=SimpleNamespace(camera=camera)),
    )
    # Straight down: the playfield fills the view, from 720 / (2 tan 30°) above the flight plane.
    height = 100 + 720 / (2 * math.tan(math.pi / 6))
    assert game_distance(game) == pytest.approx(height / 2)


def test_d205_a_close_up_fills_its_share_of_the_screen() -> None:
    fov = math.pi / 2
    distance = close_up_distance(10, fov, 0.5)
    assert 10 / (2 * distance * math.tan(fov / 2)) == pytest.approx(0.5)
