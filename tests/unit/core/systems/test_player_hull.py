"""Tests of the player's health and lives (GD-20, GD-21, GD-22), `core/systems/player_hull.py`."""

from core.systems.player_hull import HullDamage, HullRules, PlayerHull


def _rules(lives: float = 3, max_lives: float | None = None) -> HullRules:
    return HullRules(
        lives,
        2,
        3,
        HullDamage(bullet=10, missile=20, laser=5, collision=30),
        15,
        max_lives,
    )


def test_gd20_a_new_hull_starts_with_full_health_and_the_rule_lives() -> None:
    hull = PlayerHull(_rules(), 100)
    assert (hull.health, hull.max_health, hull.lives, hull.invincible) == (100, 100, 3, 0)
    assert hull.out is False


def test_gd20_lives_kept_from_the_level_before_override_the_rules() -> None:
    assert PlayerHull(_rules(), 100, lives=1).lives == 1


def test_gd22_a_hit_takes_health_and_makes_the_ship_invincible() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.hit(40) == "hit"
    assert hull.health == 60
    assert hull.invincible == 2


def test_gd22_hits_are_ignored_while_invincible() -> None:
    hull = PlayerHull(_rules(), 100)
    hull.hit(40)
    assert hull.hit(40) == "ignored"
    assert hull.health == 60


def test_gd22_invincibility_counts_down_and_stops_at_zero() -> None:
    hull = PlayerHull(_rules(), 100)
    hull.hit(10)
    hull.step(0.5)
    assert hull.invincible == 1.5
    hull.step(5)
    assert hull.invincible == 0
    assert hull.hit(10) == "hit"


def test_gd20_running_out_of_health_loses_a_life_and_refills_health() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.hit(100) == "lifeLost"
    assert hull.lives == 2
    assert hull.health == 100
    # Still invincible after the life is lost.
    assert hull.invincible == 2


def test_gd20_losing_the_last_life_ends_the_game() -> None:
    hull = PlayerHull(_rules(lives=1), 100)
    assert hull.hit(100) == "gameOver"
    assert hull.lives == 0
    assert hull.out is True
    assert hull.health == 0


def test_gd20_a_hit_on_a_ship_that_is_out_is_ignored() -> None:
    hull = PlayerHull(_rules(lives=0), 100)
    assert hull.out is True
    assert hull.hit(10) == "ignored"
    assert hull.health == 100


def test_gd20_damage_never_takes_health_below_zero() -> None:
    hull = PlayerHull(_rules(), 10)
    hull.hit(500)
    assert hull.lives == 2
    assert hull.health == 10


def test_p11_r07_a_life_bonus_adds_one_life_without_a_limit() -> None:
    hull = PlayerHull(_rules(), 100)
    assert hull.add_life() is True
    assert hull.lives == 4


def test_p11_r07_a_life_bonus_stops_at_the_most_lives() -> None:
    hull = PlayerHull(_rules(lives=2, max_lives=3), 100)
    assert hull.add_life() is True
    assert hull.lives == 3
    assert hull.add_life() is False
    assert hull.lives == 3


def test_p11_r07_a_life_bonus_does_nothing_once_the_game_is_over() -> None:
    hull = PlayerHull(_rules(lives=0), 100)
    assert hull.add_life() is False
    assert hull.lives == 0
