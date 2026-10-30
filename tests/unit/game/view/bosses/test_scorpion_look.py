"""Unit tests of `src/game/view/bosses/scorpion_look.py`."""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.scorpion_look import YELLOW


def test_p07_r05_the_scorpion_is_lit_in_its_yellow_neon():
    assert YELLOW is BOSS_LOOK.neon["scorpion"]
    assert len(YELLOW) == 3
    # Yellow: red and green both lit, blue held back.
    assert YELLOW[0] > 0.5 and YELLOW[1] > 0.5 and YELLOW[2] < YELLOW[1]
