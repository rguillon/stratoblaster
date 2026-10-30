"""Unit tests of `src/game/config/shot_look.py`."""

from game.config.shot_look import SHOT_LOOK


def test_p03_r01_the_shot_look_covers_bullets_lasers_missiles_and_impacts() -> None:
    for name in ("bullet", "laser", "missile", "impact"):
        assert SHOT_LOOK[name] is not None, name
