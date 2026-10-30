"""Things shots can hit (`core.entities.shot_target`)."""

from dataclasses import dataclass

import pytest

from core.entities.shot_target import closest_target, damage_target, is_alive


@dataclass
class Target:
    id: int
    x: float
    y: float
    radius: float = 5.0
    health: float = 10.0
    max_health: float = 10.0


def test_a_target_with_health_is_alive() -> None:
    assert is_alive(Target(1, 0, 0, health=0.5))
    assert not is_alive(Target(1, 0, 0, health=0))


def test_damage_takes_health_away() -> None:
    target = Target(1, 0, 0, health=10)
    assert damage_target(target, 3) == pytest.approx(3)
    assert target.health == pytest.approx(7)


def test_damage_never_takes_more_than_the_health_left() -> None:
    target = Target(1, 0, 0, health=2)
    assert damage_target(target, 5) == pytest.approx(2)
    assert target.health == 0


def test_negative_damage_does_nothing() -> None:
    target = Target(1, 0, 0, health=4)
    assert damage_target(target, -3) == 0
    assert target.health == 4


def test_a_dead_target_takes_no_damage() -> None:
    target = Target(1, 0, 0, health=0)
    assert damage_target(target, 3) == 0


def test_no_target_is_closest_to_an_empty_list() -> None:
    assert closest_target([], 0, 0) is None


def test_the_closest_living_target_wins() -> None:
    near = Target(1, 3, 4)
    far = Target(2, 30, 40)
    assert closest_target([far, near], 0, 0) is near


def test_dead_targets_are_skipped() -> None:
    dead = Target(1, 0, 1, health=0)
    alive = Target(2, 0, 5)
    assert closest_target([dead, alive], 0, 0) is alive


def test_a_target_out_of_reach_is_not_chosen() -> None:
    target = Target(1, 30, 40)
    assert closest_target([target], 0, 0, reach=10) is None


def test_a_target_within_reach_is_chosen() -> None:
    target = Target(1, 3, 4)
    assert closest_target([target], 0, 0, reach=10) is target
