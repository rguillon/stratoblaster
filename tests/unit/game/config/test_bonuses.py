"""Unit tests of `src/game/config/bonuses.py`."""

from game.config.bonuses import BONUS_RULES
from game.config.scoring import SCORING


def test_p11_r07_drop_chance_grows_with_enemy_health_between_its_bounds() -> None:
    chance = BONUS_RULES.chance
    assert chance.perHealth > 0
    assert 0 < chance["min"] < chance["max"] <= 1


def test_p11_r07_life_and_bomb_bonuses_are_rare_drops() -> None:
    special = BONUS_RULES.special
    assert 0 < special.life < special.bomb < 0.1
    assert special.life + special.bomb < BONUS_RULES.chance["min"]


def test_p11_r07_overflow_points_are_the_scoring_table() -> None:
    assert BONUS_RULES.overflowPoints.life == SCORING.overflow.life
    assert BONUS_RULES.overflowPoints.bomb == SCORING.overflow.bomb


def test_p11_r07_bonuses_fall_slower_than_the_ground_and_have_a_pickup_radius() -> None:
    assert 0 < BONUS_RULES.fallSpeed < 70
    assert BONUS_RULES.pickupRadius > 0
