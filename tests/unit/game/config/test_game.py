# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/game.py`."""

from game.config.game import GAME_CONFIG


def test_game_identity_is_set() -> None:
    """UI-TITLE-02 (the game's name)."""
    assert GAME_CONFIG.id == "stratoblaster"
    assert GAME_CONFIG.title == "Stratoblaster"


def test_game_screen_01_the_playfield_is_a_16_9_landscape_screen() -> None:
    """GAME-SCREEN-01 (D-249): 1280 x 720, a full HD screen at x1.5."""
    assert GAME_CONFIG.screen.width == 1280
    assert GAME_CONFIG.screen.height == 720
    assert GAME_CONFIG.screen.width / GAME_CONFIG.screen.height == 16 / 9
