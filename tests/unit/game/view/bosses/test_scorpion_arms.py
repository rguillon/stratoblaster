# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/scorpion_arms.py`."""

from game.view.bosses.scorpion_arms import _sign


def test_sign_is_math_sign() -> None:
    assert [_sign(-3), _sign(0), _sign(2.5)] == [-1, 0, 1]
