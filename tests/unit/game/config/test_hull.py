"""Unit tests of `src/game/config/hull.py`."""

from game.config.hull import HULL_RULES


def test_the_player_starts_with_three_lives_and_two_seconds_of_invincibility() -> None:
    assert HULL_RULES.lives == 3
    assert HULL_RULES.invincibleSeconds == 2


def test_hits_take_the_damage_the_design_gives_each_kind_of_hit() -> None:
    damage = HULL_RULES.damage
    assert (damage.bullet, damage.missile, damage.laser, damage.collision) == (10, 20, 25, 30)
    assert HULL_RULES.ramDamage == 40


def test_the_hitbox_is_much_smaller_than_the_ship() -> None:
    assert 0 < HULL_RULES.hitRadius < 10
