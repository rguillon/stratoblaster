# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/config/game_play.py`."""

from config.game_play import GAME_PLAY_CONFIG
from config.scenery_stage import SCENERY_STAGE_CONFIG


def test_game_screen_05_the_ship_flies_inside_the_playfield_and_the_hud_columns() -> None:
    """D-251: it may reach the bottom edge (its model on screen), not the HUD's side columns."""
    margin = GAME_PLAY_CONFIG.ship_margin
    assert margin.side > 0
    assert 17 <= margin.bottom <= 24  # half the balanced ship's length, ENEMY_UNIT 34
    assert margin.top > margin.bottom
    assert margin.panel == 200  # the HUD's side columns, UI-HUD-01


def test_game_ship_05_the_ship_banks_by_at_most_its_maximum() -> None:
    assert GAME_PLAY_CONFIG.roll.max_deg > 0
    assert GAME_PLAY_CONFIG.roll.max_deg < 90


def test_eng_100_the_simulation_steps_are_bounded_per_frame() -> None:
    assert GAME_PLAY_CONFIG.step_hz == 60
    assert GAME_PLAY_CONFIG.max_steps_per_frame >= 1
    assert GAME_PLAY_CONFIG.max_frame_seconds > 0


def test_the_stage_is_the_scenery_stage_config() -> None:
    assert GAME_PLAY_CONFIG.stage is SCENERY_STAGE_CONFIG
