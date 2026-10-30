"""Unit tests of `src/game/sim/rules_build.py`."""

from core.systems.bonus_world import BonusRules
from core.systems.boss_fights import BossFightRules
from core.systems.player_bombs import BombRules
from core.systems.player_hull import HullRules
from game.config.bombs import BOMB_RULES
from game.config.bonuses import BONUS_RULES
from game.config.boss_fights import BOSS_FIGHT_RULES
from game.config.hull import HULL_RULES
from game.config.record import record
from game.sim.rules_build import bomb_rules, bonus_rules, boss_fight_rules, hull_rules


def test_p11_r05_hull_rules_take_the_lives_and_damage_of_the_config() -> None:
    rules = hull_rules(HULL_RULES)
    assert isinstance(rules, HullRules)
    assert rules.lives == 3
    assert rules.damage.bullet == 10
    assert rules.ram_damage == 40
    assert rules.invincible_seconds == 2
    assert rules.hit_radius == 5


def test_p11_r05_hull_rules_leave_an_omitted_life_cap_as_none() -> None:
    rules = hull_rules(HULL_RULES)
    assert rules.max_lives is None


def test_p11_r05_hull_rules_keep_a_life_cap_when_the_config_has_one() -> None:
    capped = record({**HULL_RULES, "maxLives": 5})
    assert hull_rules(capped).max_lives == 5


def test_p11_r05_bomb_rules_take_the_start_damage_and_seconds() -> None:
    rules = bomb_rules(BOMB_RULES)
    assert isinstance(rules, BombRules)
    assert (rules.start, rules.damage, rules.seconds) == (3, 100, 1)
    assert rules.max is None


def test_p11_r05_bonus_rules_convert_the_chances_and_the_overflow_points() -> None:
    rules = bonus_rules(BONUS_RULES)
    assert isinstance(rules, BonusRules)
    assert rules.chance.per_health == 0.0015
    assert (rules.chance.min, rules.chance.max) == (0.06, 0.2)
    assert rules.fall_speed == 45
    assert rules.special.life == 0.01 and rules.special.bomb == 0.03
    assert rules.overflow_points.life == 5000


def test_p11_r05_bonus_rules_leave_an_omitted_special_drop_as_none() -> None:
    plain = record({**BONUS_RULES, "special": None, "overflowPoints": None})
    rules = bonus_rules(plain)
    assert rules.special is None
    assert rules.overflow_points is None


def test_p11_r05_boss_fight_rules_take_the_ease_and_bar_fill_seconds() -> None:
    rules = boss_fight_rules(BOSS_FIGHT_RULES)
    assert isinstance(rules, BossFightRules)
    assert (rules.speed_ease_seconds, rules.bar_fill_seconds) == (2, 1)
