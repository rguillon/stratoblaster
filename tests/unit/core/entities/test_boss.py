"""Unit tests of `src/core/entities/boss.py`."""

import math
from collections.abc import Callable
from typing import Any

import pytest
from helpers.fakes import FakeContext, ProbeBoss

from core.entities.boss import Boss, BossDeath, BossPartSpec, BossStats

Make = Callable[..., ProbeBoss]


def as_tuple(point: Any) -> tuple[float, ...]:
    """A muzzle point's fields, to compare them."""
    if hasattr(point, "height"):
        return (point.x, point.y, point.height)
    return (point.x, point.y)


def test_p07_r01_a_new_boss_is_coming_in_and_cannot_be_hurt(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.state == "entering"
    assert not boss.vulnerable
    assert boss.expires is False
    assert boss.rammable is False


def test_p07_r01_parts_sit_at_their_offsets_from_the_centre(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.parts[0].x == pytest.approx(80)
    assert boss.parts[0].y == pytest.approx(210)
    assert boss.core.x == pytest.approx(100)


def test_p07_r05_shots_spark_on_all_of_it_while_it_comes_in(make_boss: Make) -> None:
    boss = make_boss()
    assert boss.shot_targets == boss.hit_targets
    assert boss.core in boss.shot_targets
    assert len(boss.shot_targets) == 3


def test_p07_r01_a_shielded_core_is_passed_through(make_boss: Make) -> None:
    boss = make_boss(fighting=True)
    assert boss.core_shielded
    assert boss.shot_targets == [boss.parts[0], boss.parts[1]]
    assert boss.core not in boss.shot_targets


def test_p07_r01_once_the_shield_is_gone_shots_reach_the_core(
    make_boss: Make, ctx: FakeContext
) -> None:
    boss = make_boss(fighting=True)
    boss.parts[1].destroy()
    assert not boss.core_shielded
    assert boss.core in boss.shot_targets
    boss.update(ctx, 0.0)  # The targets are listed again on each step.
    assert boss.parts[1] not in boss.hit_targets


def test_p07_r04_breaking_a_part_starts_a_stage_with_a_pause(
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


def test_p07_r04_a_broken_part_is_counted_once(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].destroy()
    boss.update(ctx, 0.0)
    boss.update(ctx, 0.0)
    assert boss.stage == 1
    assert len(ctx.broken) == 1


def test_p07_r04_the_stage_hook_is_called_with_each_new_stage(
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


def test_p07_r04_no_attack_during_the_stage_pause(make_boss: Make, ctx: FakeContext) -> None:
    boss = make_boss(fighting=True)
    boss.parts[0].destroy()
    for _ in range(3):
        boss.update(ctx, 0.5)
    assert boss.patterns == []
    boss.update(ctx, 0.5)
    assert boss.patterns == [0.5]


def test_angry_pattern_follows_the_pause(make_boss: Make, ctx: FakeContext) -> None:
    rages: list[float] = []
    boss = make_boss(fighting=True, rage_seconds=2.0)
    boss.update_rage = lambda _ctx, dt: rages.append(dt)
    boss.parts[0].destroy()
    boss.update(ctx, 0.0)
    assert boss.rage == pytest.approx(2.0)
    boss.update(ctx, 1.5)  # The pause runs out first.
    assert rages == []
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


def test_p07_r06_hurt_core_to_zero_starts_the_death(make_boss: Make) -> None:
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


def test_p07_r06_the_hull_blasts_one_by_one_then_it_is_gone(
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
        id="ring", x=-20, y=10, radius=5, health=3, shields_core=False, drop_chance=0, orbits=True
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
    """A death blast every `every` seconds never ends for `every` of zero (the blasts never catch up
    with the time), so the interval must be positive."""
    with pytest.raises(ValueError, match="positive interval"):
        BossDeath(seconds=1.0, every=every)


def test_a_part_orbiting_the_boss_turns_its_muzzles_with_the_spin(make_boss: Make) -> None:
    ring = BossPartSpec(
        id="ring", x=-20, y=10, radius=5, health=3, shields_core=False, drop_chance=0, orbits=True
    )
    boss = make_boss(parts=[ring])
    boss.spin = math.pi / 2
    assert as_tuple(boss.parts[0].place((1, 0, 0))) == pytest.approx((100, 199, 0))
