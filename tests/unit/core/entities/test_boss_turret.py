"""A turret on a boss's piece (`core.entities.boss_turret`, phase 7 review)."""

import math

import pytest

from core.entities.boss_turret import BossTurret, BossTurretSpec


def test_a_turret_spec_keeps_its_pivot_and_turn_rates() -> None:
    spec = BossTurretSpec(4, -2, 90)
    assert (spec.x, spec.y, spec.turn_rate_deg) == (4, -2, 90)
    assert spec.laser_turn_rate_deg is None


def test_a_turret_spec_can_turn_slower_on_a_laser_warning() -> None:
    assert BossTurretSpec(0, 0, 90, 15).laser_turn_rate_deg == 15


def test_a_new_turret_points_straight_down() -> None:
    turret = BossTurret(BossTurretSpec(0, 0, 90))
    assert turret.aim == 0
    assert turret.turned((3, 4, 2)) == pytest.approx((3, 4, 2))


def test_a_turret_turns_its_muzzles_around_its_pivot() -> None:
    turret = BossTurret(BossTurretSpec(0, 0, 90))
    turret.aim = math.pi / 2  # Clockwise on screen: the muzzle below the pivot moves to its left.
    assert turret.turned((0, -10, 5)) == pytest.approx((-10, 0, 5))


def test_a_turret_keeps_its_pivot_when_it_is_away_from_the_origin() -> None:
    turret = BossTurret(BossTurretSpec(5, 5, 90))
    turret.aim = math.pi / 2
    assert turret.turned((5, -5, 2)) == pytest.approx((-5, 5, 2))
