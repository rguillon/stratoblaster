"""How a boss rolls into its sideways moves (`core.entities.boss_roll`)."""

import math

import pytest

from core.entities.boss_roll import BossRoll, roll_towards

RULE = BossRoll(max_deg=30, full_speed=100, ease_per_sec=1)
LIMIT = math.pi / 6


def test_a_roll_rule_keeps_its_settings() -> None:
    rule = BossRoll(max_deg=12, full_speed=50, ease_per_sec=3)
    assert (rule.max_deg, rule.full_speed, rule.ease_per_sec) == (12, 50, 3)


def test_a_boss_at_rest_eases_back_to_level() -> None:
    assert roll_towards(RULE, LIMIT, 0, 0.5) == pytest.approx(LIMIT * 0.5)


def test_full_speed_rolls_to_the_maximum() -> None:
    assert roll_towards(RULE, 0, 100, 1) == pytest.approx(LIMIT)


def test_a_fast_boss_is_held_at_the_maximum() -> None:
    assert roll_towards(RULE, 0, 1000, 1) == pytest.approx(LIMIT)
    assert roll_towards(RULE, 0, -1000, 1) == pytest.approx(-LIMIT)


def test_a_slow_boss_rolls_in_proportion() -> None:
    assert roll_towards(RULE, 0, 50, 1) == pytest.approx(LIMIT / 2)


def test_the_easing_is_capped_at_reaching_the_target() -> None:
    fast_ease = BossRoll(max_deg=30, full_speed=100, ease_per_sec=1000)
    assert roll_towards(fast_ease, 0, 100, 1) == pytest.approx(LIMIT)
