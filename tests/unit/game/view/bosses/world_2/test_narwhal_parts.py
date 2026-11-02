# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/narwhal_parts.py`."""

from game.view.bosses.world_2 import narwhal_parts as module


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-4), module._sign(0), module._sign(4)] == [-1, 0, 1]
