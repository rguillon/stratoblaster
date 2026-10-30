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


def test_p03_r01_each_player_weapon_is_a_projectile_or_a_beam() -> None:
    assert [w.id for w in PLAYER_WEAPONS] == ["bullet", "laser", "missile"]
    assert {w.kind for w in PLAYER_WEAPONS} == {"projectile", "beam"}
    assert BULLET.kind == MISSILE.kind == "projectile"
    assert LASER.kind == "beam"


def test_p03_r01_diagonals_are_a_pair_mirrored_about_straight_ahead() -> None:
    assert diagonals(10) == [
        {"offsetX": 0, "angleDeg": -10},
        {"offsetX": 0, "angleDeg": 10},
    ]


def test_p03_r01_forward_and_dual_are_the_bullet_stream_layouts() -> None:
    assert FORWARD == {"offsetX": 0, "angleDeg": 0}
    assert len(DUAL) == 2
    assert DUAL_SPACING == 12 and DUAL[0]["offsetX"] == -DUAL[1]["offsetX"] == -6


def test_p03_r01_missiles_fan_out_at_an_inner_and_an_outer_angle() -> None:
    assert 0 < MISSILE_ANGLES.inner < MISSILE_ANGLES.outer
