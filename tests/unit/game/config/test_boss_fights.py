"""Unit tests of `src/game/config/boss_fights.py`."""

from game.config.boss_fights import BOSS_FIGHT_RULES


def test_the_ground_eases_and_the_health_bar_fills_in_seconds() -> None:
    assert BOSS_FIGHT_RULES.speedEaseSeconds == 2
    assert BOSS_FIGHT_RULES.barFillSeconds == 1
