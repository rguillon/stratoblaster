"""Unit tests of the boss transformations in `src/core/entities/boss.py`: as it loses parts, a boss
transforms and reveals hidden weapon parts (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-
transform-design.md, Part B)."""

import math
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


# D-228: a transformation called for by named parts, a boss turning round, a part retiring.


def _scorpion_like(make_boss: Make) -> ProbeBoss:
    parts = [
        BossPartSpec("claw-l", -40, -20, 5, 10, False, 0.0, False, None, None),
        BossPartSpec("claw-r", 40, -20, 5, 10, False, 0.0, False, None, None),
        BossPartSpec("sting", 0, -30, 5, 10, False, 0.0, False, None, None, 1),
        BossPartSpec("cannon", 0, 50, 5, 10, True, 0.0, False, None, 1),
    ]
    return make_boss(
        fighting=True,
        parts=parts,
        transforms=[1],
        transform_seconds=2.0,
        transform_parts=[["claw-l", "claw-r"]],
        turns=[math.pi],
    )


def test_d228_named_parts_call_for_a_transformation_whatever_else_is_lost(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = _scorpion_like(make_boss)
    # One claw is not enough, even though the count of `transforms` would be.
    _break(boss, ctx, "claw-l")
    assert boss.state == "fighting"
    _break(boss, ctx, "claw-r")
    assert boss.state == "transforming"


def test_d228_a_part_retires_as_its_transformation_starts(make_boss: Make, ctx: FakeContext) -> None:
    boss = _scorpion_like(make_boss)
    sting = _by_id(boss, "sting")
    health = boss.remaining_health
    assert not sting.hidden and not sting.retired
    _break(boss, ctx, "claw-l")
    _break(boss, ctx, "claw-r")
    stage = boss.stage
    assert sting.retired and sting.hidden
    assert not sting.destroyed
    assert sting not in boss.hit_targets
    # It no longer counts in its health; its stage is the same (it was not destroyed).
    assert boss.remaining_health == health - 30
    boss.update(ctx, 3.0)
    assert boss.form == 1
    assert boss.stage == stage
    assert sting.retired


def test_d228_the_boss_turns_round_as_it_transforms_its_parts_with_it(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = _scorpion_like(make_boss)
    cannon = _by_id(boss, "cannon")
    boss.update(ctx, 0.0)
    assert (cannon.x, cannon.y) == pytest.approx((boss.x, boss.y + 50))
    _break(boss, ctx, "claw-l")
    _break(boss, ctx, "claw-r")
    boss.update(ctx, 1.0)
    assert math.pi < boss.heading < 2 * math.pi
    boss.update(ctx, 1.5)
    assert boss.form == 1
    assert boss.heading == pytest.approx(2 * math.pi)
    boss.update(ctx, 0.0)
    # Behind it, now below it (towards the player).
    assert (cannon.x, cannon.y) == pytest.approx((boss.x, boss.y - 50))
    claw = _by_id(boss, "claw-l")
    assert (claw.x, claw.y) == pytest.approx((boss.x + 40, boss.y + 20))


def test_d228_k_skips_a_retired_part_and_does_not_reveal_forever(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = _scorpion_like(make_boss)
    for _ in range(8):
        boss.break_next()
        boss.update(ctx, 0.0)
    assert boss.form == 1
    assert boss.state == "dying"
