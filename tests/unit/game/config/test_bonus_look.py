"""Unit tests of `src/game/config/bonus_look.py`."""

from game.config.bonus_look import BONUS_LOOK


def test_p11_r07_life_and_bomb_bonuses_have_their_own_look() -> None:
    assert BONUS_LOOK.life is not None
    assert BONUS_LOOK.bomb is not None
    assert BONUS_LOOK.life != BONUS_LOOK.bomb


def test_p11_r07_the_frame_is_inset_inside_the_bonus() -> None:
    assert 0 < BONUS_LOOK.frameInset < 1
    assert BONUS_LOOK.size > 0
