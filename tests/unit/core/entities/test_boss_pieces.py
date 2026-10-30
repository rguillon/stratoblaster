"""Unit tests of `src/core/entities/boss_pieces.py`."""

import math
from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import ProbeBoss

Make = Callable[..., ProbeBoss]


def as_tuple(point: Any) -> tuple[float, ...]:
    """A muzzle point's fields, to compare them."""
    if hasattr(point, "height"):
        return (point.x, point.y, point.height)
    return (point.x, point.y)


def test_p07_r01_part_ids_are_unique_and_below_zero(make_boss: Make) -> None:
    boss = make_boss()
    boss.id = 3
    assert boss.parts[0].id == -(3 * 64 + 1)
    assert boss.parts[1].id == -(3 * 64 + 2)
    assert boss.core.id == 3


def test_a_part_takes_its_radius_health_and_flags_from_its_spec(make_boss: Make) -> None:
    part = make_boss().parts[0]
    assert part.radius == 5
    assert part.max_health == 3
    assert part.health == 3
    assert part.drop_chance == 0.5
    assert part.shields_core is False
    assert part.index == 0
    assert part.broken is False


def test_part_points_default_to_zero(make_boss: Make) -> None:
    assert make_boss().parts[0].points == 0


def test_p11_r01_part_points_come_from_the_stats(make_boss: Make) -> None:
    assert make_boss(part_points=50).parts[0].points == 50


def test_a_part_without_a_turret_ignores_on_turret(make_boss: Make) -> None:
    point = make_boss().parts[1].place((0, -10, 5), on_turret=True)
    assert as_tuple(point) == pytest.approx((100, 190, 5))


def test_the_core_without_a_turret_places_muzzles_plainly(make_boss: Make) -> None:
    assert as_tuple(make_boss().core.place((0, -10, 5), on_turret=True)) == pytest.approx(
        (100, 190, 5)
    )


def test_part_emitter_is_one_radius_ahead_along_its_heading(make_boss: Make) -> None:
    part = make_boss().parts[0]
    emitter = part.emitter
    assert (emitter.x, emitter.y) == pytest.approx((80, 205))


def test_core_emitter_is_one_radius_ahead_of_the_core(make_boss: Make) -> None:
    emitter = make_boss().core.emitter
    assert (emitter.x, emitter.y) == pytest.approx((100, 188))


def test_p07_r01_damage_to_a_part_only_counts_once_in_place(make_boss: Make) -> None:
    boss = make_boss()
    part = boss.parts[0]
    part.health = 1  # Coming in: ignored.
    assert part.health == 3
    assert part.since_hit == math.inf
    boss.state = "fighting"
    part.health = 1
    assert part.health == 1
    assert part.since_hit == 0


def test_a_part_health_is_never_negative_and_is_destroyed_at_zero(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    part = boss.parts[0]
    part.health = -2
    assert part.health == 0
    assert part.destroyed


def test_a_part_gets_no_hit_flash_when_it_is_healed(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].health = 10
    assert boss.parts[0].since_hit == math.inf


def test_destroy_kills_a_part_at_once(make_boss: Make) -> None:
    part = make_boss().parts[0]
    part.destroy()
    assert part.destroyed
    assert part.health == 0


def test_a_part_is_gone_once_destroyed_or_once_its_boss_is(make_boss: Make) -> None:
    boss = make_boss()
    assert not boss.parts[1].gone
    boss.parts[1].destroy()
    assert boss.parts[1].gone
    boss.gone = True
    assert boss.parts[0].gone


def test_the_core_follows_its_boss_position(make_boss: Make) -> None:
    boss = make_boss()
    boss.x = 50
    boss.y = 60
    assert (boss.core.x, boss.core.y) == (50, 60)
    assert boss.core.radius == 12
    assert boss.core.max_health == 100


def test_the_core_takes_damage_only_once_unshielded_and_in_place(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.core.health = 60  # Shielded by the part at index 1: no damage.
    assert boss.core.health == 100
    boss.parts[1].destroy()
    boss.core.health = 60
    assert boss.core.health == 60
    assert boss.core.since_hit == 0


def test_the_core_ignores_damage_while_coming_in(make_boss: Make) -> None:
    boss = make_boss()
    boss.parts[1].destroy()
    boss.core.health = 60
    assert boss.core.health == 100


def test_a_core_that_gains_health_gets_no_hit_flash(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.parts[1].destroy()
    boss.core.health = 120
    assert boss.core.health == 120
    assert boss.core.since_hit == math.inf


def test_the_core_is_gone_once_its_boss_is_dying_or_gone(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    assert not boss.core.gone
    boss.hurt_core(0)
    assert boss.core.gone
    assert boss.core.health == 0


def test_the_core_id_is_its_bosss_id(make_boss: Make) -> None:
    boss = make_boss()
    boss.id = 9
    assert boss.core.id == 9
