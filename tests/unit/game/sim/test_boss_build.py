# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/boss_build.py`."""

import pytest

from core.entities.boss import BossStats
from core.systems.boss_pattern import (
    BossAimedShape,
    BossBurstShape,
    BossLaserShape,
    BossMissilesShape,
)
from game.config.bosses.boss_kit import BOSS_TIMING, bullet, part, volley
from game.config.bosses.mini_bosses import REEF_WARDEN
from game.config.bosses.world_3.stone_idol import STONE_IDOL
from game.config.bosses.world_4.geyser_rig import GEYSER_RIG
from game.config.record import merge, record
from game.sim.boss_build import (
    angry_pattern,
    armed_pattern,
    armed_volley,
    boss_stats,
    break_ring_ids,
    bullet_spec,
    launch_volley,
)
from game.sim.boss_kinds import BOSS_DESIGNS


def test_boss_23_a_bullet_spec_carries_its_speed_radius_and_style() -> None:
    spec = bullet_spec(bullet("plasma", 120, 6))
    assert (spec.speed, spec.radius, spec.style) == (120, 6, "plasma")
    assert spec.burst is None


def test_enm_17_a_bullet_with_a_burst_keeps_its_ring_of_small_bullets() -> None:
    spec = bullet_spec(
        record({
            "speed": 40,
            "radius": 9,
            "style": "cryo",
            "burst": {"after": 1.5, "count": 6, "bullet": bullet("small", 60, 2)},
        })
    )
    assert spec.burst.after == 1.5
    assert spec.burst.count == 6
    assert spec.burst.bullet.style == "small"


def test_boss_23_an_aimed_volley_is_armed_with_the_guns_of_its_piece() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    armed = armed_volley(design, volley.aimed("core", 2, 3, 10, bullet("x", 1), 0.5))
    assert armed.from_ == "core"
    assert armed.every == 2
    assert isinstance(armed.shape, BossAimedShape)
    assert armed.shape.count == 3
    assert armed.muzzles == [[0, 0, 1]]
    assert armed.first == 0.5
    assert armed.turret is False


def test_boss_23_a_burst_volley_keeps_its_gap_and_bullet() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    armed = armed_volley(design, volley.burst("core", 3, 2, 0.12, bullet("b", 1)))
    assert isinstance(armed.shape, BossBurstShape)
    assert armed.shape.gap == 0.12


def test_boss_23_a_laser_volley_is_built_as_a_laser_shape() -> None:
    design = record({"guns": {"core": {"laser": [[1, 1, 1]]}}})
    armed = armed_volley(design, volley.laser("core", 5, 1.5))
    assert isinstance(armed.shape, BossLaserShape)
    assert armed.muzzles == [[1, 1, 1]]


def test_boss_23_an_unknown_volley_shape_is_an_error() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    bad = record({"from": "core", "every": 1, "shape": {"kind": "spiral"}})
    with pytest.raises(ValueError, match="Unknown boss volley shape"):
        armed_volley(design, bad)


def test_boss_20_armed_pattern_arms_each_volley_in_order() -> None:
    design = record({"guns": {"core": {"gun": [[0, 0, 1]]}}})
    volleys = [
        volley.aimed("core", 1, 1, 0, bullet("a", 1)),
        volley.burst("core", 2, 2, 0.1, bullet("b", 1)),
    ]
    armed = armed_pattern(design, volleys)
    assert [v.every for v in armed] == [1, 2]


def test_boss_25_a_launch_volley_fires_its_enemies_from_its_part() -> None:
    launch = record({"from": "hangar", "kind": "hornets", "count": 2, "every": 6, "first": 1})
    armed = launch_volley(launch)
    assert armed.from_ == "hangar"
    assert armed.every == 6
    assert armed.first == 1


def test_boss_23_break_ring_ids_lists_the_parts_with_rings_and_none_without() -> None:
    assert break_ring_ids(record({"breakRings": None})) == []
    assert break_ring_ids(record({})) == []
    assert break_ring_ids(record({"breakRings": {"a": {}, "b": {}}})) == ["a", "b"]


def test_boss_07_boss_stats_takes_the_numbers_and_parts_of_a_design() -> None:
    stats = boss_stats(REEF_WARDEN)
    assert isinstance(stats, BossStats)
    assert stats.name == REEF_WARDEN.stats["name"]
    assert stats.health == REEF_WARDEN.stats["health"]
    assert len(stats.parts) == len(REEF_WARDEN.stats["parts"])
    assert stats.rage_seconds == BOSS_TIMING.rageSeconds


def test_boss_33_a_boss_with_joints_gets_a_swing_spec_for_each_joint() -> None:
    stats = boss_stats(GEYSER_RIG)
    assert set(stats.joints.keys()) == {"arm-left", "arm-right"}
    arm = stats.joints["arm-left"]
    assert arm.swing.period > 0
    assert (
        arm.swing.amplitude_deg == GEYSER_RIG.stats["joints"]["arm-left"]["swing"]["amplitudeDeg"]
    )


def test_boss_29_a_boss_with_turret_guns_gets_a_turret_spec_per_turret_piece() -> None:
    stats = boss_stats(STONE_IDOL)
    assert set(stats.turrets.keys()) == {"eye-left", "eye-right", "third-eye"}


def _with_parts(parts: list, transforms: list | None = None) -> object:
    stats = merge(REEF_WARDEN.stats, {"parts": [part(*p) for p in parts]})
    extra = {"stats": stats}
    if transforms is not None:
        extra["transforms"] = transforms
    return merge(REEF_WARDEN, extra)


def test_hidden_parts_carry_their_reveal_and_others_none() -> None:
    design = _with_parts([["a", [0, 0], 5, 10], ["x", [0, 0], 5, 10, {"reveal": 1}]])
    stats = boss_stats(design)
    assert [p.reveal for p in stats.parts] == [None, 1]


def test_a_mini_boss_with_one_reveal_transforms_once_half_its_parts_are_gone() -> None:
    parts = [[f"p{i}", [0, 0], 5, 10] for i in range(5)]
    parts.append(["x", [0, 0], 5, 10, {"reveal": 1}])
    assert boss_stats(_with_parts(parts)).transforms == [3]


def test_a_final_boss_with_two_reveals_transforms_at_a_third_and_two_thirds() -> None:
    parts = [[f"p{i}", [0, 0], 5, 10] for i in range(5)]
    parts.extend([["x", [0, 0], 5, 10, {"reveal": 1}], ["y", [0, 0], 5, 10, {"reveal": 2}]])
    stats = boss_stats(_with_parts(parts))
    assert stats.transforms == [2, 4]
    assert stats.transform_seconds == BOSS_TIMING.transformSeconds


def test_a_design_may_set_its_own_transformation_points() -> None:
    parts = [["a", [0, 0], 5, 10], ["x", [0, 0], 5, 10, {"reveal": 1}]]
    assert boss_stats(_with_parts(parts, [1])).transforms == [1]


def test_a_boss_without_hidden_parts_does_not_transform() -> None:
    assert boss_stats(_with_parts([["a", [0, 0], 5, 10]])).transforms is None


def _revealed(design: object, form: int) -> list[str]:
    return [p["id"] for p in design.stats["parts"] if p.get("reveal") == form]  # type: ignore[attr-defined]


def test_boss_27_the_angry_pattern_is_the_newly_revealed_weapons_firing_faster() -> None:
    for design in BOSS_DESIGNS:
        forms = {p["reveal"] for p in design.stats["parts"] if p.get("reveal")}
        assert forms
        for form in forms:
            angry = angry_pattern(design, form)
            assert angry
            assert {v.from_ for v in angry} <= set(_revealed(design, form))


def test_boss_27_an_angry_volley_comes_boss_timing_rage_rate_times_as_often() -> None:
    gatling = [d for d in BOSS_DESIGNS if any(v["shape"]["kind"] == "burst" for v in d.stages[-1])]
    design = gatling[0]
    revealed = {p["id"] for p in design.stats["parts"] if p.get("reveal")}
    normal = [
        v for v in design.stages[-1] if v["from"] in revealed and v["shape"]["kind"] == "burst"
    ]
    angry = [
        v for v in angry_pattern(design, 1) + angry_pattern(design, 2) if v.shape.kind == "burst"
    ]
    assert angry
    assert min(v.every for v in angry) == pytest.approx(
        min(v["every"] for v in normal) / BOSS_TIMING.rageRate
    )


def test_boss_27_an_angry_laser_keeps_its_warning_its_beam_and_a_gap() -> None:
    for design in BOSS_DESIGNS:
        for form in (1, 2):
            for v in angry_pattern(design, form):
                if isinstance(v.shape, BossLaserShape):
                    laser = v.shape.laser
                    least = laser.warning_seconds + laser.firing_seconds + BOSS_TIMING.rageLaserGap
                    assert v.every >= least - 1e-9


def test_boss_27_an_angry_missile_rack_fires_more_missiles() -> None:
    counts: list[float] = []
    for design in BOSS_DESIGNS:
        base = {v["from"]: v for v in design.stages[-1] if v["shape"]["kind"] == "missiles"}
        angry = angry_pattern(design, 1) + angry_pattern(design, 2)
        counts.extend(
            v.shape.count / base[v.from_]["shape"]["count"]
            for v in angry
            if isinstance(v.shape, BossMissilesShape)
        )
    assert counts
    assert set(counts) == {BOSS_TIMING.rageMissiles}
