# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/final_boss_gull.py`."""

from game.view.bosses.final_boss_gull import _sign_of


def test_sign_of_is_math_sign() -> None:
    assert [_sign_of(-3), _sign_of(0), _sign_of(2.5)] == [-1, 0, 1]
