"""Unit tests of `src/game/config/bomb_look.py`."""

from game.config.bomb_look import BOMB_LOOK


def test_p11_r05_bomb_look_has_its_depth_wave_and_flash() -> None:
    assert BOMB_LOOK.depth is not None
    assert BOMB_LOOK.wave is not None
    assert BOMB_LOOK.flash is not None
