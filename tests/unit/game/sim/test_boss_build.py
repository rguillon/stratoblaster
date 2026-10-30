"""Unit tests of `src/game/sim/boss_build.py`."""

import pytest

from core.entities.boss import BossStats
from core.systems.boss_pattern import BossAimedShape, BossBurstShape, BossLaserShape
from game.config.bosses.boss_kit import bullet, volley
from game.config.bosses.mini_bosses import REEF_WARDEN
from game.config.bosses.world_3.stone_idol import STONE_IDOL
from game.config.bosses.world_4.geyser_rig import GEYSER_RIG
from game.config.record import record
from game.sim.boss_build import (
    armed_pattern,
    armed_volley,
    boss_stats,
    break_ring_ids,
    bullet_spec,
    launch_volley,
)


def test_p07_r05_a_bullet_spec_carries_its_speed_radius_and_style() -> None:
    spec = bullet_spec(bullet("plasma", 120, 6))
    assert (spec.speed, spec.radius, spec.style) == (120, 6, "plasma")
    assert spec.burst is None


def test_p07_r05_a_bullet_with_a_burst_keeps_its_ring_of_small_bullets() -> None:
    spec = bullet_spec(
        record(
            {
                "speed": 40,
                "radius": 9,
                "style": "cryo",
                "burst": {"after": 1.5, "count": 6, "bullet": bullet("small", 60, 2)},
            }
        )
    )
    assert spec.burst.after == 1.5
    assert spec.burst.count == 6
    assert spec.burst.bullet.style == "small"


def test_p07_r05_an_aimed_volley_is_armed_with_the_guns_of_its_piece() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    armed = armed_volley(design, volley.aimed("core", 2, 3, 10, bullet("x", 1), 0.5))
    assert armed.from_ == "core"
    assert armed.every == 2
    assert isinstance(armed.shape, BossAimedShape)
    assert armed.shape.count == 3
    assert armed.muzzles == [[0, 0, 1]]
    assert armed.first == 0.5
    assert armed.turret is False


def test_p07_r05_a_burst_volley_keeps_its_gap_and_bullet() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    armed = armed_volley(design, volley.burst("core", 3, 2, 0.12, bullet("b", 1)))
    assert isinstance(armed.shape, BossBurstShape)
    assert armed.shape.gap == 0.12


def test_p07_r05_a_laser_volley_is_built_as_a_laser_shape() -> None:
    design = record({"guns": {"core": {"laser": [[1, 1, 1]]}}})
    armed = armed_volley(design, volley.laser("core", 5, 1.5))
    assert isinstance(armed.shape, BossLaserShape)
    assert armed.muzzles == [[1, 1, 1]]


def test_p07_r05_an_unknown_volley_shape_is_an_error() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    bad = record({"from": "core", "every": 1, "shape": {"kind": "spiral"}})
    with pytest.raises(ValueError, match="Unknown boss volley shape"):
        armed_volley(design, bad)


def test_p07_r05_armed_pattern_arms_each_volley_in_order() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    volleys = [
        volley.aimed("core", 1, 1, 0, bullet("a", 1)),
        volley.burst("core", 2, 2, 0.1, bullet("b", 1)),
    ]
    armed = armed_pattern(design, volleys)
    assert [v.every for v in armed] == [1, 2]


def test_p07_r05_a_launch_volley_fires_its_enemies_on_the_launch_side() -> None:
    launch = record({"from": "hangar", "kind": "hornets", "count": 2, "every": 6, "first": 1})
    armed = launch_volley(launch, 1)
    assert armed.from_ == "hangar"
    assert armed.every == 6
    assert armed.first == 1


def test_p07_r05_break_ring_ids_lists_the_parts_with_rings_and_none_without() -> None:
    assert break_ring_ids(record({"breakRings": None})) == []
    assert break_ring_ids(record({})) == []
    assert break_ring_ids(record({"breakRings": {"a": {}, "b": {}}})) == ["a", "b"]


def test_p07_r05_boss_stats_takes_the_numbers_and_parts_of_a_design() -> None:
    stats = boss_stats(REEF_WARDEN)
    assert isinstance(stats, BossStats)
    assert stats.name == REEF_WARDEN.stats["name"]
    assert stats.health == REEF_WARDEN.stats["health"]
    assert len(stats.parts) == len(REEF_WARDEN.stats["parts"])
    assert stats.rage_seconds == 3


def test_p07_r05_a_boss_with_joints_gets_a_swing_spec_for_each_joint() -> None:
    stats = boss_stats(GEYSER_RIG)
    assert set(stats.joints.keys()) == {"arm-left", "arm-right"}
    arm = stats.joints["arm-left"]
    assert arm.swing.period > 0
    assert (
        arm.swing.amplitude_deg == GEYSER_RIG.stats["joints"]["arm-left"]["swing"]["amplitudeDeg"]
    )


def test_p07_r05_a_boss_with_turret_guns_gets_a_turret_spec_per_turret_piece() -> None:
    stats = boss_stats(STONE_IDOL)
    assert set(stats.turrets.keys()) == {"eye-left", "eye-right"}
