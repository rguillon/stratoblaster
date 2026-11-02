# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/jungle_flesh.py`: signs."""

from game.view.bosses.world_3 import jungle_flesh as module


def test_sign_of_is_minus_one_zero_or_one() -> None:
    assert [module.sign_of(-2), module.sign_of(0), module.sign_of(2)] == [-1, 0, 1]
