# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/bomb_look.py`."""

from game.config.bomb_look import BOMB_LOOK


def test_gfx_fx_10_bomb_look_has_its_depth_wave_and_flash() -> None:
    assert BOMB_LOOK.depth is not None
    assert BOMB_LOOK.wave is not None
    assert BOMB_LOOK.flash is not None
