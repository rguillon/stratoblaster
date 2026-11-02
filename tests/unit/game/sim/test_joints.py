# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/joints.py`: config joints and parts as the core's specs."""

import pytest

from core.entities.boss_joint import BossJointSpec
from core.entities.jointed_enemy import EnemyPartSpec
from game.config.record import record
from game.sim.joints import enemy_parts, joint_specs, jointed_design

NECK = {"x": 2, "y": -5, "swing": {"amplitudeDeg": 20, "period": 3, "phase": 0.25}}

HEAD = {"x": 0, "y": -9, "swing": {"amplitudeDeg": 10, "period": 2}, "parent": "neck"}


def test_enm_33_joints_keep_their_pivot_swing_and_parent() -> None:
    specs = joint_specs(record({"neck": NECK, "head": HEAD}))
    assert set(specs) == {"neck", "head"}
    neck = specs["neck"]
    assert isinstance(neck, BossJointSpec)
    assert (neck.x, neck.y, neck.parent) == (2, -5, None)
    assert (neck.swing.amplitude_deg, neck.swing.period, neck.swing.phase) == (20, 3, 0.25)
    assert specs["head"].parent == "neck"


def test_enm_33_a_swing_without_a_phase_starts_at_the_top_of_its_period() -> None:
    head = joint_specs(record({"head": HEAD}))["head"]
    assert head.swing.phase == 0


def test_enm_27_parts_default_to_no_aim_no_orbit_and_no_shield() -> None:
    arm = {"id": "arm", "x": 4, "y": 1, "radius": 3, "health": 20, "joint": "neck"}
    drone = {
        "id": "drone",
        "x": 0,
        "y": 9,
        "radius": 2,
        "health": 10,
        "orbits": True,
        "aim": 1.5,
        "shields": True,
    }
    plain, orbiting = enemy_parts([record(arm), record(drone)])
    assert isinstance(plain, EnemyPartSpec)
    assert (plain.id, plain.joint, plain.aim, plain.orbits, plain.shields) == (
        "arm",
        "neck",
        0,
        False,
        False,
    )
    assert (orbiting.joint, orbiting.aim, orbiting.orbits, orbiting.shields) == (
        None,
        pytest.approx(1.5),
        True,
        True,
    )


def test_enm_27_a_design_without_joints_has_none() -> None:
    part = {"id": "pod", "x": 0, "y": 0, "radius": 2, "health": 5}
    bare = jointed_design(record({"parts": [part]}))
    assert bare.joints is None
    assert [p.id for p in bare.parts] == ["pod"]
    jointed = jointed_design(record({"parts": [part], "joints": {"neck": NECK}}))
    assert set(jointed.joints) == {"neck"}
