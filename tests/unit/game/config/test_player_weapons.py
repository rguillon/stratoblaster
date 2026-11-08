# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/player_weapons.py`."""

from game.config.player_weapons import (
    BULLET,
    DUAL,
    DUAL_SPACING,
    FORWARD,
    LASER,
    MISSILE,
    MISSILE_ANGLES,
    PLAYER_WEAPONS,
    diagonals,
)


def test_game_wpn_01_each_player_weapon_is_a_projectile_or_a_beam() -> None:
    assert [w.id for w in PLAYER_WEAPONS] == ["bullet", "laser", "missile"]
    assert {w.kind for w in PLAYER_WEAPONS} == {"projectile", "beam"}
    assert BULLET.kind == MISSILE.kind == "projectile"
    assert LASER.kind == "beam"


def test_game_wpn_03_diagonals_are_a_pair_mirrored_about_straight_ahead() -> None:
    """Also GAME-WPN-10 (the missiles' diagonals)."""
    assert diagonals(10) == [
        {"offsetX": 0, "angleDeg": -10},
        {"offsetX": 0, "angleDeg": 10},
    ]


def test_game_wpn_03_forward_and_dual_are_the_bullet_stream_layouts() -> None:
    assert FORWARD == {"offsetX": 0, "angleDeg": 0}
    assert len(DUAL) == 2
    assert DUAL_SPACING == 12
    assert DUAL[0]["offsetX"] == -DUAL[1]["offsetX"] == -6


def test_game_wpn_10_missiles_fan_out_at_an_inner_and_an_outer_angle() -> None:
    assert 0 < MISSILE_ANGLES.inner < MISSILE_ANGLES.outer


def test_game_wpn_12_laser_deals_125_percent_and_missiles_40_percent_of_the_guns() -> None:
    """Each level's laser deals 125 % of the guns' damage per second, the missiles 40 % of it.

    Every stream counted (GAME-WPN-12, D-281). Whole percentages are compared with integers, so no
    float rounding decides a level.
    """
    assert len(BULLET.levels) == len(LASER.levels) == len(MISSILE.levels) == 5
    for level in range(5):
        guns = BULLET.shotsPerSecond * BULLET.damage * len(BULLET.levels[level])
        laser = LASER.levels[level].damagePerSecond
        missiles = MISSILE.shotsPerSecond * MISSILE.damage * len(MISSILE.levels[level])
        assert 100 * laser == 125 * guns, level + 1
        assert 100 * missiles == 40 * guns, level + 1
        assert laser > guns > missiles, level + 1
