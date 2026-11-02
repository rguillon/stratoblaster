# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/game.py`."""

import pytest

from game.config.game import GAME_CONFIG


def test_game_identity_is_set() -> None:
    """UI-TITLE-02 (the game's name)."""
    assert GAME_CONFIG.id == "stratoblaster"
    assert GAME_CONFIG.title == "Stratoblaster"


def test_game_screen_01_the_playfield_is_a_1138_x_640_landscape_screen() -> None:
    """GAME-SCREEN-01: 16:9 at the height the game was tuned at (D-249)."""
    assert GAME_CONFIG.screen.width == 1138
    assert GAME_CONFIG.screen.height == 640
    assert GAME_CONFIG.screen.width > GAME_CONFIG.screen.height > 0


def test_game_screen_01_the_screen_is_16_9_within_half_a_percent() -> None:
    """GAME-SCREEN-01, GAME-SCREEN-02: a 1920 x 1080 window is filled (bars under a pixel)."""
    ratio = GAME_CONFIG.screen.width / GAME_CONFIG.screen.height
    assert ratio == pytest.approx(16 / 9, rel=0.005)
    scale = min(1920 / GAME_CONFIG.screen.width, 1080 / GAME_CONFIG.screen.height)
    assert 1080 - GAME_CONFIG.screen.height * scale < 1
    assert 1920 - GAME_CONFIG.screen.width * scale < 1
