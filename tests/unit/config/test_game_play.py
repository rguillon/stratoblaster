"""Unit tests of `src/config/game_play.py`."""

from config.game_play import GAME_PLAY_CONFIG
from config.scenery_stage import SCENERY_STAGE_CONFIG


def test_p06_r02_the_ship_flies_inside_the_playfield_above_the_hud() -> None:
    margin = GAME_PLAY_CONFIG.ship_margin
    assert margin.side > 0
    assert margin.bottom > 48  # the HUD's bar is 48 px high
    assert margin.top > margin.bottom


def test_p06_r03_the_ship_banks_by_at_most_its_maximum() -> None:
    assert GAME_PLAY_CONFIG.roll.max_deg > 0
    assert GAME_PLAY_CONFIG.roll.max_deg < 90


def test_p06_r09_the_simulation_steps_are_bounded_per_frame() -> None:
    assert GAME_PLAY_CONFIG.step_hz == 60
    assert GAME_PLAY_CONFIG.max_steps_per_frame >= 1
    assert GAME_PLAY_CONFIG.max_frame_seconds > 0


def test_p06_r09_the_stage_is_the_scenery_stage_config() -> None:
    assert GAME_PLAY_CONFIG.stage is SCENERY_STAGE_CONFIG


def test_p06_r09_the_stage_reach_and_clearance_are_ordered() -> None:
    stage = SCENERY_STAGE_CONFIG
    assert stage.prop_reach[0] < stage.prop_reach[1]
    assert stage.far_clip > stage.sun_distance
    assert stage.chunk_length > stage.cell > 0
