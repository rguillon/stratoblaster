"""Unit tests of `src/core/entities/boss_turret.py`."""

import math
from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import ProbeBoss

from core.entities.boss_turret import BossTurret, BossTurretSpec

Make = Callable[..., ProbeBoss]


def as_tuple(point: Any) -> tuple[float, ...]:
    """A muzzle point's fields, to compare them."""
    if hasattr(point, "height"):
        return (point.x, point.y, point.height)
    return (point.x, point.y)


def test_turrets_belong_to_the_parts_and_core_named_in_the_stats(make_boss: Make) -> None:
    boss = make_boss(turrets={"gun": BossTurretSpec(0, 0, 90)})
    assert boss.parts[0].turret is not None
    assert boss.parts[1].turret is None
    assert boss.core.turret is None


def test_the_core_can_have_a_turret(make_boss: Make) -> None:
    boss = make_boss(turrets={"core": BossTurretSpec(0, 0, 90)})
    assert boss.core.turret is not None


def test_a_part_placed_on_its_turret_turns_with_it(make_boss: Make) -> None:
    boss = make_boss(turrets={"gun": BossTurretSpec(0, 0, 90)})
    boss.parts[0].turret.aim = math.pi / 2
    assert as_tuple(boss.parts[0].place((0, -10, 5), on_turret=True)) == pytest.approx((90, 200, 5))


def test_a_part_placed_off_its_turret_stays_where_the_muzzle_is(make_boss: Make) -> None:
    boss = make_boss(turrets={"gun": BossTurretSpec(0, 0, 90)})
    boss.parts[0].turret.aim = math.pi / 2
    assert as_tuple(boss.parts[0].place((0, -10, 5))) == pytest.approx((100, 190, 5))


def test_the_core_places_its_turret_muzzles(make_boss: Make) -> None:
    boss = make_boss(turrets={"core": BossTurretSpec(0, 0, 90)})
    boss.core.turret.aim = math.pi / 2
    assert as_tuple(boss.core.place((0, -10, 5), on_turret=True)) == pytest.approx((90, 200, 5))
    assert as_tuple(boss.core.place((0, -10, 5))) == pytest.approx((100, 190, 5))


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
