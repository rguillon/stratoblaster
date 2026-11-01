# Copyright (c) 2026 Renaud Guillon
"""The joints of the enemies and bosses, from their config records (ENM-33, BOSS-33).

The core reads `BossJointSpec`s, the config keeps the records as written (camelCase). Each boss's
own limbs are its boss file's (`specs/bosses/`).
"""

from core.entities.boss_joint import BossJointSpec, JointSwing
from core.entities.jointed_enemy import EnemyPartSpec, JointedDesign
from game.sim.config_access import keys_of, opt

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def joint_specs(joints: Any) -> Any:
    """Return the joints of a boss or enemy record, by id, as the core's specs."""
    result: Any = {}
    for joint_id in keys_of(joints):
        joint = joints[joint_id]
        swing = joint.swing
        phase = swing.phase
        if phase == None:
            phase = 0
        result[joint_id] = BossJointSpec(
            joint.x,
            joint.y,
            JointSwing(swing.amplitudeDeg, swing.period, phase),
            opt(joint.parent),
        )
    return result


def enemy_parts(parts: Any) -> list[EnemyPartSpec]:
    """Return the parts of a jointed enemy from its config records.

    An omitted `aim` is 0, and an omitted `orbits` or `shields` is off.
    """
    result: list[EnemyPartSpec] = []
    for part in parts:
        aim = 0 if part.aim == None else part.aim
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
    """Return a jointed enemy's design from its config: its parts on joints or in orbit (ENM-27).

    And its joints as the core's specs.
    """
    joints = None if design.joints == None else joint_specs(design.joints)
    return JointedDesign(enemy_parts(design.parts), joints)
