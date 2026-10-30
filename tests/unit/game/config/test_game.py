"""Unit tests of `src/game/config/game.py`."""

from game.config.game import GAME_CONFIG


def test_game_identity_is_set() -> None:
    assert GAME_CONFIG.id == "stratoblaster"
    assert GAME_CONFIG.title == "Stratoblaster"


def test_playfield_is_a_portrait_screen_with_positive_size() -> None:
    assert GAME_CONFIG.screen.width == 480
    assert GAME_CONFIG.screen.height == 640
    assert GAME_CONFIG.screen.height > GAME_CONFIG.screen.width > 0
