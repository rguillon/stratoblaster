"""Unit tests of the boss transformations in `src/core/entities/boss.py`: as it loses parts, a boss
transforms and reveals hidden weapon parts (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-
transform-design.md, Part B)."""

from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import FakeContext, ProbeBoss

from core.entities.boss import BossPartSpec

Make = Callable[..., ProbeBoss]


def _part(part_id: str, reveal: int | None = None, shields: bool = False) -> BossPartSpec:
    return BossPartSpec(part_id, 0, 0, 5, 10, shields, 0.0, False, None, reveal)


def _parts() -> list[BossPartSpec]:
    """4 original parts, 1 hidden part for each of 2 transformations (shielding the core)."""
    return [
        _part("a"),
        _part("b"),
        _part("c"),
        _part("d"),
        _part("x1", 1, True),
        _part("x2", 2, True),
    ]


@pytest.fixture
def boss(make_boss: Make) -> ProbeBoss:
    return make_boss(
        fighting=True, parts=_parts(), transforms=[1, 3], transform_seconds=1.5, rage_seconds=2.0
    )


def _break(boss: ProbeBoss, ctx: FakeContext, part_id: str) -> None:
    next(p for p in boss.parts if p.spec.id == part_id).destroy()
    boss.update(ctx, 0.0)


def _by_id(boss: ProbeBoss, part_id: str) -> Any:
    return next(p for p in boss.parts if p.spec.id == part_id)


def test_hidden_parts_are_neither_hit_nor_shield_the_core_nor_take_damage(boss: ProbeBoss) -> None:
    x1 = _by_id(boss, "x1")
    assert x1.hidden
    assert x1 not in boss.hit_targets
    assert x1 not in boss.shot_targets
    assert not boss.core_shielded
    x1.health = 1
    assert x1.health == 10


def test_a_boss_transforms_once_enough_original_parts_are_destroyed(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    _break(boss, ctx, "a")
    assert boss.state == "transforming"
    assert boss.transforming_into == 1
    assert not boss.vulnerable
    boss.update(ctx, 0.75)
    assert boss.transform == pytest.approx(0.5)
    # It still moves, but does not fire.
    assert boss.patterns == []
    assert boss.moves >= 1


def test_after_its_transformation_its_new_parts_are_live_and_it_is_angry(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    _break(boss, ctx, "a")
    boss.update(ctx, 1.5)
    x1 = _by_id(boss, "x1")
    assert boss.state == "fighting"
    assert boss.form == 1
    assert boss.transform == 0
    assert not x1.hidden
    assert x1 in boss.hit_targets
    assert boss.core_shielded
    assert boss.rage == pytest.approx(2.0)
    assert _by_id(boss, "x2").hidden


def test_revealed_parts_do_not_count_towards_the_next_transformation(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    _break(boss, ctx, "a")
    boss.update(ctx, 1.5)
    _break(boss, ctx, "x1")
    _break(boss, ctx, "b")
    assert boss.state == "fighting"
    _break(boss, ctx, "c")
    assert boss.state == "transforming"
    assert boss.transforming_into == 2


def test_thresholds_crossed_at_once_give_transformations_one_after_the_other(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    for part_id in ["a", "b", "c"]:
        _by_id(boss, part_id).destroy()
    boss.update(ctx, 0.0)
    assert boss.transforming_into == 1
    boss.update(ctx, 1.5)
    assert boss.form == 1
    assert boss.state == "transforming"
    assert boss.transforming_into == 2
    boss.update(ctx, 1.5)
    assert boss.form == 2
    assert boss.state == "fighting"


def test_the_transform_hook_hears_of_each_transformation(make_boss: Make, ctx: FakeContext) -> None:
    heard: list[int] = []
    boss = make_boss(fighting=True, parts=_parts(), transforms=[1, 3])
    boss.on_transform = lambda k, _ctx: heard.append(k)
    _break(boss, ctx, "a")
    boss.update(ctx, 1.5)
    for part_id in ["b", "c"]:
        _break(boss, ctx, part_id)
    assert heard == [1, 2]


def test_the_health_bar_counts_hidden_parts_from_the_start(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    full = boss.full_health
    assert full == 100 + 6 * 10
    assert boss.remaining_health == full
    _break(boss, ctx, "a")
    boss.update(ctx, 1.5)
    assert boss.full_health == full
    assert boss.remaining_health == full - 10


def test_break_next_skips_hidden_parts_and_finishes_a_transformation(
    boss: ProbeBoss, ctx: FakeContext
) -> None:
    boss.break_next()
    boss.update(ctx, 0.0)
    assert _by_id(boss, "a").destroyed
    assert boss.state == "transforming"
    boss.break_next()
    assert boss.form == 1
    assert boss.state == "fighting"
    for _ in range(4):
        boss.break_next()
        boss.update(ctx, 0.0)
        if boss.state == "transforming":
            boss.break_next()
    assert all(p.destroyed for p in boss.parts if p.spec.id != "x2") or boss.form == 2
    # Every part, hidden ones included, goes before the core.
    while boss.state != "dying":
        boss.break_next()
        boss.update(ctx, 0.0)
        if boss.state == "transforming":
            boss.break_next()
    assert all(p.destroyed for p in boss.parts)
    assert boss.form == 2


def test_a_boss_without_transformations_never_transforms(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    _break(boss, ctx, "gun")
    _break(boss, ctx, "shield")
    assert boss.state == "fighting"
    assert boss.form == 0


def test_parts_broken_as_it_comes_in_transform_it_once_in_place(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(parts=_parts(), transforms=[1, 3])
    boss.break_next()
    boss.update(ctx, 0.0)
    assert boss.state == "entering"
    boss.arrived = True
    boss.update(ctx, 0.0)
    assert boss.state == "transforming"


def test_break_next_never_reaches_the_core_while_weapons_are_hidden(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(parts=_parts(), transforms=[1, 3])
    for _ in range(4):
        boss.break_next()
        boss.update(ctx, 0.0)
    assert boss.state == "entering"
    boss.break_next()
    assert boss.state != "dying"
    assert boss.form == 1
    assert _by_id(boss, "x1") in boss.hit_targets
