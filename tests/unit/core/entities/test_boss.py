# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/entities/boss.py`."""

import math
from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import FakeContext, ProbeBoss

from core.entities.boss import Boss, BossDeath, BossPartSpec, BossStats

Make = Callable[..., ProbeBoss]


def as_tuple(point: Any) -> tuple[float, ...]:
    """Return a muzzle point's fields, to compare them."""
    if hasattr(point, "height"):
        return (point.x, point.y, point.height)
    return (point.x, point.y)


def test_boss_09_a_new_boss_is_coming_in_and_cannot_be_hurt(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.state == "entering"
    assert not boss.vulnerable
    assert boss.expires is False
    assert boss.rammable is False


def test_boss_12_parts_sit_at_their_offsets_from_the_centre(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.parts[0].x == pytest.approx(80)
    assert boss.parts[0].y == pytest.approx(210)
    assert boss.core.x == pytest.approx(100)


def test_boss_09_shots_spark_on_all_of_it_while_it_comes_in(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.shot_targets == boss.hit_targets
    assert boss.core in boss.shot_targets
    assert len(boss.shot_targets) == 3


def test_boss_15_a_shielded_core_is_passed_through(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    assert boss.core_shielded
    assert boss.shot_targets == [boss.parts[0], boss.parts[1]]
    assert boss.core not in boss.shot_targets


def test_boss_14_once_the_shield_is_gone_shots_reach_the_core(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(fighting=True)
    boss.parts[1].destroy()
    assert not boss.core_shielded
    assert boss.core in boss.shot_targets
    boss.update(ctx, 0.0)  # The targets are listed again on each step.
    assert boss.parts[1] not in boss.hit_targets


def test_boss_20_breaking_a_part_starts_a_stage_with_a_pause(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].destroy()
    boss.update(ctx, 0.0)
    assert boss.stage == 1
    assert boss.pause == pytest.approx(1.5)
    assert boss.rage == 0
    assert ctx.broken == [boss.parts[0]]
    assert boss.parts[0] not in boss.hit_targets


def test_boss_20_a_broken_part_is_counted_once(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].destroy()
    boss.update(ctx, 0.0)
    boss.update(ctx, 0.0)
    assert boss.stage == 1
    assert len(ctx.broken) == 1


def test_boss_21_the_stage_hook_is_called_with_each_new_stage(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(fighting=True)
    stages: list[int] = []
    boss.on_stage_change = lambda stage, _ctx: stages.append(stage)
    boss.parts[0].destroy()
    boss.parts[1].destroy()
    boss.update(ctx, 0.0)
    assert stages == [1, 2]
    assert boss.stage == 2


def test_boss_22_no_attack_during_the_stage_pause(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].destroy()
    for _ in range(3):
        boss.update(ctx, 0.5)
    assert boss.patterns == []
    boss.update(ctx, 0.5)
    assert boss.patterns == [0.5]


def test_boss_27_a_lost_part_does_not_make_the_boss_angry(
    make_boss: Make, ctx: FakeContext
) -> None:
    rages: list[float] = []
    boss = make_boss(fighting=True, rage_seconds=2.0)
    boss.update_rage = lambda _ctx, dt: rages.append(dt)
    boss.parts[0].destroy()
    boss.update(ctx, 0.0)
    assert boss.rage == 0
    boss.update(ctx, 1.5)  # The pause runs out first.
    boss.update(ctx, 0.5)
    assert rages == []
    assert boss.patterns == [0.5]


def test_boss_27_the_angry_pattern_runs_after_a_transformation(
    make_boss: Make, ctx: FakeContext
) -> None:
    rages: list[float] = []
    parts = [_part("a"), _part("b"), _part("x1", 1, shields=True)]
    boss = make_boss(
        fighting=True, parts=parts, transforms=[1], transform_seconds=1.0, rage_seconds=2.0
    )
    boss.update_rage = lambda _ctx, dt: rages.append(dt)
    _break(boss, ctx, "a")
    boss.update(ctx, 1.0)  # The transformation ends: it is angry.
    assert boss.rage == pytest.approx(2.0)
    # No pause is left from the lost part: it fires at once.
    boss.update(ctx, 0.5)
    assert rages == [0.5]
    assert boss.rage == pytest.approx(1.5)
    assert boss.patterns == []


def test_without_an_angry_hook_the_stage_pattern_goes_on(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True, rage_seconds=2.0)
    boss.parts[0].destroy()
    boss.update(ctx, 1.5)
    boss.update(ctx, 0.5)
    assert boss.patterns == [0.5]


def test_boss_19_hurt_core_to_zero_starts_the_death(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.hurt_core(0)
    assert boss.state == "dying"
    assert boss.core_health == 0
    assert boss.core.gone
    assert all(part.destroyed and part.broken for part in boss.parts)
    assert boss.shot_targets == []


def test_hurt_core_keeps_a_positive_health(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.hurt_core(40)
    assert boss.core_health == pytest.approx(40)
    assert boss.state == "fighting"


def test_full_and_remaining_health_count_the_core_and_the_parts(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    assert boss.full_health == pytest.approx(100 + 3 + 4)
    boss.hurt_core(40)
    boss.parts[0].destroy()
    assert boss.remaining_health == pytest.approx(40 + 4)


def test_d_305_scale_health_multiplies_the_core_and_every_part(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.scale_health(1.5)
    assert boss.core_health == pytest.approx(150)
    assert boss.core.max_health == pytest.approx(150)
    assert [part.max_health for part in boss.parts] == pytest.approx([4.5, 6])
    assert [part.health for part in boss.parts] == pytest.approx([4.5, 6])
    assert boss.full_health == pytest.approx(1.5 * (100 + 3 + 4))
    assert boss.remaining_health == pytest.approx(boss.full_health)


def test_break_next_destroys_the_parts_then_the_core(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    boss.break_next()
    assert boss.parts[0].destroyed
    boss.break_next()
    assert boss.parts[1].destroyed
    assert boss.state == "fighting"
    boss.break_next()
    assert boss.state == "dying"
    boss.break_next()  # Nothing more to break while dying.
    assert boss.state == "dying"


def test_boss_19_the_hull_blasts_one_by_one_then_it_is_gone(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(fighting=True)
    boss.hurt_core(0)
    boss.update(ctx, 0.5)
    assert len(ctx.explosions) == 3
    assert boss.health == 100
    boss.update(ctx, 0.5)
    assert len(ctx.explosions) == 5
    assert boss.health == 0
    assert boss.patterns == []


def test_a_blast_is_centred_near_the_part_it_is_on(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.hurt_core(0)
    boss.update(ctx, 0.0)  # The first blast is due at once, on the first gun.
    assert len(ctx.explosions) == 1
    x, y, radius = ctx.explosions[0]
    assert radius == pytest.approx(5)
    assert abs(x - 80) <= 5 * 0.6
    assert abs(y - 210) <= 5 * 0.6


def test_a_boss_without_parts_blasts_from_its_core(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True, parts=[])
    boss.hurt_core(0)
    boss.update(ctx, 1.0)
    assert len(ctx.explosions) == 5
    assert all(radius == pytest.approx(12) for _, _, radius in ctx.explosions)


def test_a_boss_without_a_roll_rule_does_not_roll(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.x += 10
    boss.update(ctx, 0.1)
    assert boss.roll == 0


def test_orbiting_parts_turn_with_the_spin(make_boss: Make, ctx: FakeContext) -> None:
    ring = BossPartSpec(
        id_="ring", x=-20, y=10, radius=5, health=3, shields_core=False, drop_chance=0, orbits=True
    )
    boss = make_boss(parts=[ring])
    boss.spin = math.pi / 2
    boss.update(ctx, 0.0)
    assert boss.parts[0].x == pytest.approx(110)
    assert boss.parts[0].y == pytest.approx(220)


def test_a_boss_that_does_not_arrive_does_not_move_or_attack(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss()
    boss.update(ctx, 0.5)
    assert boss.state == "entering"
    assert boss.moves == 0
    assert boss.patterns == []


def test_a_boss_that_arrives_starts_fighting(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss()
    boss.arrived = True
    boss.update(ctx, 0.5)
    assert boss.state == "fighting"
    assert boss.vulnerable
    assert boss.moves == 0  # It arrives during this step, so it does not move yet.


def test_a_fighting_boss_moves_and_attacks(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.update(ctx, 0.5)
    assert boss.moves == 1
    assert boss.patterns == [0.5]


def test_the_core_drop_chance_comes_from_the_stats(make_boss: Make) -> None:
    assert make_boss(core_drop_chance=0.25).drop_chance == 0.25
    assert make_boss().drop_chance is None


def test_part_points_are_passed_to_the_parts(make_boss: Make) -> None:
    assert make_boss(part_points=50).parts[0].points == 50


def test_the_base_hooks_of_a_boss_are_abstract(ctx: FakeContext) -> None:
    stats = BossStats(
        model="boss",
        radius=40.0,
        health=100.0,
        points=0.0,
        name="Base",
        core_radius=12.0,
        parts=[],
        ground_speed=1.0,
        stage_pause=1.0,
        death=BossDeath(seconds=1.0, every=0.5),
    )
    boss = Boss(100, 200, stats)
    with pytest.raises(NotImplementedError):
        boss.enter(ctx, 0.1)
    with pytest.raises(NotImplementedError):
        boss.move(ctx, 0.1)
    with pytest.raises(NotImplementedError):
        boss.update_pattern(ctx, 0.1)
    with pytest.raises(NotImplementedError):
        boss.update(ctx, 0.1)


def test_boss_death_keeps_its_timing() -> None:
    death = BossDeath(seconds=2.0, every=0.5)
    assert (death.seconds, death.every) == (2.0, 0.5)


@pytest.mark.parametrize("every", [0.0, -1.0, float("nan")])
def test_boss_death_needs_a_positive_blast_interval(every: float) -> None:
    """A death blast every `every` seconds never ends for `every` of zero.

    The blasts never catch up with the time, so the interval must be positive.
    """
    with pytest.raises(ValueError, match="positive interval"):
        BossDeath(seconds=1.0, every=every)


def test_a_part_orbiting_the_boss_turns_its_muzzles_with_the_spin(make_boss: Make) -> None:
    ring = BossPartSpec(
        id_="ring", x=-20, y=10, radius=5, health=3, shields_core=False, drop_chance=0, orbits=True
    )
    boss = make_boss(parts=[ring])
    boss.spin = math.pi / 2
    assert as_tuple(boss.parts[0].place((1, 0, 0))) == pytest.approx((100, 199, 0))


# The boss transformations: as it loses parts, a boss transforms and reveals hidden weapon parts
# (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-design.md, Part B).


def _part(part_id: str, reveal: int | None = None, shields: bool = False) -> BossPartSpec:
    return BossPartSpec(part_id, 0, 0, 5, 10, shields, 0.0, orbits=False, joint=None, reveal=reveal)


def _parts() -> list[BossPartSpec]:
    """4 original parts, 1 hidden part for each of 2 transformations (shielding the core)."""
    return [
        _part("a"),
        _part("b"),
        _part("c"),
        _part("d"),
        _part("x1", 1, shields=True),
        _part("x2", 2, shields=True),
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
        BossPartSpec(
            "claw-l",
            -40,
            -20,
            5,
            10,
            shields_core=False,
            drop_chance=0.0,
            orbits=False,
            joint=None,
            reveal=None,
        ),
        BossPartSpec(
            "claw-r",
            40,
            -20,
            5,
            10,
            shields_core=False,
            drop_chance=0.0,
            orbits=False,
            joint=None,
            reveal=None,
        ),
        BossPartSpec(
            "sting",
            0,
            -30,
            5,
            10,
            shields_core=False,
            drop_chance=0.0,
            orbits=False,
            joint=None,
            reveal=None,
            retire=1,
        ),
        BossPartSpec(
            "cannon",
            0,
            50,
            5,
            10,
            shields_core=True,
            drop_chance=0.0,
            orbits=False,
            joint=None,
            reveal=1,
        ),
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


def test_d228_a_part_retires_as_its_transformation_starts(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = _scorpion_like(make_boss)
    sting = _by_id(boss, "sting")
    health = boss.remaining_health
    assert not sting.hidden
    assert not sting.retired
    _break(boss, ctx, "claw-l")
    _break(boss, ctx, "claw-r")
    stage = boss.stage
    assert sting.retired
    assert sting.hidden
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
