"""Moving limbs of a boss (`core.entities.boss_joint`, phase 7 review)."""

import math
from dataclasses import dataclass

import pytest

from core.entities.boss_joint import BossJoints, BossJointSpec, JointSwing


@dataclass
class FakePart:
    id: str
    joint: str | None = None
    orbits: bool = False


def test_a_swing_keeps_its_settings() -> None:
    swing = JointSwing(30, 2.0)
    assert (swing.amplitude_deg, swing.period, swing.phase) == (30, 2.0, 0)


def test_a_joint_spec_hangs_on_nothing_by_default() -> None:
    spec = BossJointSpec(1, 2, JointSwing(10, 1))
    assert (spec.x, spec.y, spec.parent) == (1, 2, None)


def test_a_joint_starts_at_its_phase() -> None:
    joints = BossJoints({"arm": BossJointSpec(0, 0, JointSwing(90, 1, 0.25))})
    assert joints.angle("arm") == pytest.approx(math.pi / 2)


def test_a_joint_swings_back_and_forth_with_time() -> None:
    joints = BossJoints({"arm": BossJointSpec(0, 0, JointSwing(90, 2))})
    assert joints.angle("arm") == pytest.approx(0)
    joints.step(0.5)  # A quarter of a period of 2 s: the top of the swing.
    assert joints.angle("arm") == pytest.approx(math.pi / 2)
    joints.step(0.5)  # Back to the middle of the swing.
    assert joints.angle("arm") == pytest.approx(0, abs=1e-12)


def test_an_unknown_joint_is_not_turned() -> None:
    assert BossJoints().angle("nope") == 0


def test_without_a_joint_a_point_does_not_move() -> None:
    assert BossJoints().move(None, 3, 4) == (3, 4)


def test_a_point_on_an_unknown_joint_does_not_move() -> None:
    assert BossJoints().move("nope", 3, 4) == (3, 4)


def test_a_point_turns_around_its_joint() -> None:
    joints = BossJoints({"arm": BossJointSpec(10, 0, JointSwing(90, 1, 0.25))})
    # The point 5 above the pivot, turned a quarter turn clockwise on screen, is 5 to its right.
    x, y = joints.move("arm", 10, 5)
    assert (x, y) == pytest.approx((15, 0))


def test_a_point_on_a_child_joint_turns_with_its_parent_too() -> None:
    joints = BossJoints(
        {
            "shoulder": BossJointSpec(0, 0, JointSwing(90, 1, 0.25)),
            "elbow": BossJointSpec(0, 10, JointSwing(0, 1), parent="shoulder"),
        }
    )
    assert joints.move("elbow", 0, 20) == pytest.approx((20, 0))


def test_a_part_must_hang_on_a_known_joint() -> None:
    with pytest.raises(ValueError, match="hangs on no joint"):
        BossJoints({}, [FakePart("claw", joint="arm")])


def test_a_part_cannot_both_orbit_and_hang_on_a_joint() -> None:
    specs = {"arm": BossJointSpec(0, 0, JointSwing(10, 1))}
    with pytest.raises(ValueError, match="both orbits"):
        BossJoints(specs, [FakePart("claw", joint="arm", orbits=True)])


def test_a_joint_cannot_hang_on_an_unknown_joint() -> None:
    specs = {"elbow": BossJointSpec(0, 0, JointSwing(10, 1), parent="missing")}
    with pytest.raises(ValueError, match="hangs on no joint"):
        BossJoints(specs)


def test_a_joint_cannot_hang_on_itself() -> None:
    with pytest.raises(ValueError, match="hangs on itself"):
        BossJoints({"a": BossJointSpec(0, 0, JointSwing(10, 1), parent="a")})


def test_joints_cannot_hang_on_each_other_in_a_cycle() -> None:
    specs = {
        "a": BossJointSpec(0, 0, JointSwing(10, 1), parent="b"),
        "b": BossJointSpec(0, 0, JointSwing(10, 1), parent="a"),
    }
    with pytest.raises(ValueError, match="hangs on itself"):
        BossJoints(specs)
