"""The joints of the enemies and bosses, from their config records (P05-R13, P07): the core reads
`BossJointSpec`s, the config keeps the records as written (camelCase).
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss_joint import BossJointSpec, JointSwing
from core.entities.jointed_enemy import EnemyPartSpec, JointedDesign
from game.sim.config_access import keys_of, opt

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def joint_specs(joints: Any) -> Any:
    """The joints of a boss or enemy record, by id, as the core's specs."""
    result: Any = {}
    for joint_id in keys_of(joints):
        joint = joints[joint_id]
        swing = joint.swing
        phase = swing.phase
        if phase == None:  # noqa: E711
            phase = 0
        result[joint_id] = BossJointSpec(
            joint.x,
            joint.y,
            JointSwing(swing.amplitudeDeg, swing.period, phase),
            opt(joint.parent),
        )
    return result


def enemy_parts(parts: Any) -> list[EnemyPartSpec]:
    """The parts of a jointed enemy from its config records: an omitted `aim` is 0, and an omitted
    `orbits` or `shields` is off."""
    result: list[EnemyPartSpec] = []
    for part in parts:
        aim = 0 if part.aim == None else part.aim  # noqa: E711
        result.append(
            EnemyPartSpec(
                part.id,
                part.x,
                part.y,
                part.radius,
                part.health,
                opt(part.joint),
                part.orbits is True,
                aim,
                part.shields is True,
            )
        )
    return result


def jointed_design(design: Any) -> JointedDesign:
    """A jointed enemy's design from its config: its parts, and its joints as the core's specs."""
    joints = None if design.joints == None else joint_specs(design.joints)  # noqa: E711
    return JointedDesign(enemy_parts(design.parts), joints)
