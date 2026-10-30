"""Unit tests of `src/core/entities/jointed_enemy.py`."""

import math
from typing import Any

import pytest
from helpers.fakes import FakeContext

from core.entities.boss_joint import BossJointSpec, JointSwing
from core.entities.enemy import EnemyStats
from core.entities.jointed_enemy import EnemyPartSpec, JointedDesign, JointedEnemy

DESIGN = JointedDesign(
    parts=[
        EnemyPartSpec("turret", -20, 10, 5, 3),
        EnemyPartSpec("shield", 0, 20, 6, 4, shields=True),
        EnemyPartSpec("orbiter", 0, -10, 3, 2, orbits=True),
        EnemyPartSpec("claw", 0, 10, 2, 1, joint="arm"),
        EnemyPartSpec("hand", 0, 15, 1, 1, joint="wrist"),
    ],
    joints={
        "arm": BossJointSpec(0, 0, JointSwing(90, 1, 0.25)),
        "wrist": BossJointSpec(0, 10, JointSwing(0, 1), parent="arm"),
    },
)


class Hull(JointedEnemy):
    """A jointed enemy whose `act` only records the steps it was given."""

    def __init__(self, x: float, y: float, stats: EnemyStats, design: JointedDesign) -> None:
        super().__init__(x, y, stats, design)
        self.acts: list[float] = []

    def act(self, ctx: Any, dt: float) -> None:
        self.acts.append(dt)


def make_hull(design: JointedDesign = DESIGN) -> Hull:
    return Hull(100, 200, EnemyStats("hull", 30, 50, 500), design)


def part_by_id(hull: JointedEnemy, id: str) -> Any:
    found = [part for part in hull.parts if part.spec.id == id]
    assert len(found) == 1
    return found[0]


def test_a_part_spec_has_no_joint_and_is_not_shielding_by_default() -> None:
    spec = EnemyPartSpec("a", 1, 2, 3, 4)
    assert (spec.joint, spec.orbits, spec.aim, spec.shields) == (None, False, 0, False)


def test_a_design_has_no_joints_by_default() -> None:
    assert JointedDesign([]).joints is None


def test_the_base_act_is_abstract() -> None:
    enemy = JointedEnemy(100, 200, EnemyStats("hull", 30, 50, 500), JointedDesign([]))
    with pytest.raises(NotImplementedError):
        enemy.update(FakeContext(), 0.1)


def test_a_part_hanging_on_a_joint_that_is_unknown_is_refused() -> None:
    design = JointedDesign([EnemyPartSpec("a", 0, 0, 1, 1, joint="nope")])
    with pytest.raises(ValueError, match="hangs on no joint"):
        make_hull(design)


def test_a_part_is_placed_when_the_enemy_is_made() -> None:
    hull = make_hull()
    turret = part_by_id(hull, "turret")
    assert (turret.x, turret.y) == pytest.approx((80, 210))
    assert turret.heading == pytest.approx(math.pi)


def test_a_part_on_a_joint_moves_with_its_joint_and_turns_too() -> None:
    hull = make_hull()
    claw = part_by_id(hull, "claw")
    assert (claw.x, claw.y) == pytest.approx((110, 200))
    assert claw.heading == pytest.approx(math.pi + math.pi / 2)


def test_a_part_hanging_on_a_child_joint_turns_with_its_parent_joints() -> None:
    hull = make_hull()
    hand = part_by_id(hull, "hand")
    assert (hand.x, hand.y) == pytest.approx((115, 200))
    assert hand.heading == pytest.approx(math.pi + math.pi / 2)


def test_every_part_has_a_unique_negative_id_for_its_enemy() -> None:
    hull = make_hull()
    hull.id = 2
    ids = [part.id for part in hull.parts]
    assert ids[0] == -(2 * 64 + 1)
    assert len(set(ids)) == len(ids)
    assert all(part_id < 0 for part_id in ids)


def test_a_standing_part_is_one_of_the_enemys_hit_targets() -> None:
    hull = make_hull()
    assert hull.hit_targets[0] is hull
    assert len(hull.hit_targets) == 1 + len(hull.parts)


def test_a_destroyed_part_is_no_longer_a_target_or_found() -> None:
    hull = make_hull()
    turret = part_by_id(hull, "turret")
    turret.destroy()
    assert hull.part("turret") is None
    assert turret not in hull.hit_targets


def test_part_returns_the_part_with_the_id_or_none() -> None:
    hull = make_hull()
    assert hull.part("shield") is part_by_id(hull, "shield")
    assert hull.part("nope") is None


def test_a_standing_shield_keeps_shots_from_the_hull() -> None:
    hull = make_hull()
    assert hull.shielded
    assert hull not in hull.shot_targets
    assert part_by_id(hull, "shield") in hull.shot_targets


def test_without_its_shield_the_hull_takes_shots() -> None:
    hull = make_hull()
    part_by_id(hull, "shield").destroy()
    assert not hull.shielded
    assert hull in hull.shot_targets


def test_a_part_loses_health_and_flashes_when_it_is_hit() -> None:
    part = part_by_id(make_hull(), "turret")
    assert part.since_hit == math.inf
    part.health = 1
    assert part.health == 1
    assert part.since_hit == 0


def test_a_part_health_stops_at_zero() -> None:
    part = part_by_id(make_hull(), "turret")
    part.health = -4
    assert part.health == 0
    assert part.destroyed


def test_a_part_gives_no_bonus_and_no_points() -> None:
    part = part_by_id(make_hull(), "turret")
    assert part.drop_chance == 0
    assert part.points is None


def test_a_part_is_gone_once_destroyed_or_once_its_enemy_is() -> None:
    hull = make_hull()
    turret = part_by_id(hull, "turret")
    assert not turret.gone
    hull.gone = True
    assert turret.gone


def test_a_part_destroy_kills_it_at_once() -> None:
    part = part_by_id(make_hull(), "turret")
    part.destroy()
    assert part.destroyed
    assert part.health == 0


def test_a_part_fires_lasers_from_one_radius_ahead_of_it() -> None:
    part = part_by_id(make_hull(), "turret")
    assert (part.emitter.x, part.emitter.y) == pytest.approx((80, 205))


def test_a_part_placed_on_an_orbit_turns_with_the_spin() -> None:
    hull = make_hull()
    hull.spin = math.pi / 2
    hull.update(FakeContext(), 0.0)
    orbiter = part_by_id(hull, "orbiter")
    assert (orbiter.x, orbiter.y) == pytest.approx((90, 200))
    assert orbiter.heading == pytest.approx(math.pi + math.pi / 2)


def test_a_part_destroyed_by_the_player_is_broken_once_on_the_next_step() -> None:
    hull = make_hull()
    ctx = FakeContext()
    turret = part_by_id(hull, "turret")
    turret.destroy()
    hull.update(ctx, 0.0)
    assert ctx.broken == [turret]
    assert turret.broken
    hull.update(ctx, 0.0)
    assert ctx.broken == [turret]


def test_each_step_swings_the_joints_and_runs_the_act() -> None:
    hull = make_hull()
    ctx = FakeContext()
    hull.update(ctx, 0.5)
    assert hull.acts == [0.5]
    assert hull.joints.angle("arm") == pytest.approx(-math.pi / 2)


def test_the_joints_can_be_held_still() -> None:
    hull = make_hull()
    hull.swinging = False
    hull.update(FakeContext(), 0.5)
    assert hull.joints.angle("arm") == pytest.approx(math.pi / 2)


def test_on_destroyed_blows_up_every_part_still_on_the_enemy() -> None:
    hull = make_hull()
    ctx = FakeContext()
    part_by_id(hull, "turret").destroy()
    hull.on_destroyed(ctx)
    assert len(ctx.broken) == len(hull.parts)
    assert all(part.broken and part.destroyed for part in hull.parts)
    hull.on_destroyed(ctx)
    assert len(ctx.broken) == len(hull.parts)


def test_a_part_that_gains_health_gets_no_hit_flash() -> None:
    part = part_by_id(make_hull(), "turret")
    part.health = 10
    assert part.health == 10
    assert part.since_hit == math.inf
