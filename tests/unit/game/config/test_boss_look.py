"""Unit tests of `src/game/config/boss_look.py`."""

from game.config.boss_look import BOSS_LOOK


def test_p07_r01_boss_stage_strobe_and_rage_flicker_are_positive_rates() -> None:
    assert BOSS_LOOK.stageStrobeHz > 0
    assert BOSS_LOOK.rageFlicker.hz > 0
    assert 0 < BOSS_LOOK.rageFlicker.dim < 1


def test_p07_r01_boss_neon_is_an_rgb_triple_in_range() -> None:
    assert len(BOSS_LOOK.neon) >= 1
