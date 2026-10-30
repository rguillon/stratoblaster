"""Unit tests of `src/game/config/bosses/boss_rage.py`."""

import pytest

from game.config.bosses.boss_kit import volley
from game.config.bosses.boss_rage import angry, arms, rage, rate
from game.config.bosses.final_bosses import OVERLORD, STORM_PETREL

PATTERNS = ["spirals", "flower", "curtain", "vortex"]


def test_rate_grows_with_heat_and_scales_by_the_share() -> None:
    assert rate(0, 1) == 20
    assert rate(4.5, 1) == pytest.approx(56)
    assert rate(2, 0.5) == pytest.approx((20 + 16) * 0.5)


def test_arms_grows_with_heat_by_whole_bullets() -> None:
    assert arms(0) == 5
    assert arms(1) == 6
    assert arms(4.5) == 8


def test_angry_bullet_speeds_up_a_little_with_heat() -> None:
    assert angry("plasma", 0) == {"speed": 120, "radius": 4, "style": "plasma"}
    assert angry("plasma", 4.5)["speed"] == pytest.approx(156)


@pytest.mark.parametrize("name", PATTERNS)
@pytest.mark.parametrize("heat", [0, 2.25, 4.5])
def test_every_pattern_fires_only_from_the_core_with_angry_bullets(name: str, heat: float) -> None:
    volleys = rage[name](heat, "a", "b")
    assert volleys
    for shot in volleys:
        assert shot["from"] == "core"
        assert shot["every"] > 0
        assert shot["shape"]["bullet"]["style"] in {"a", "b"}


@pytest.mark.parametrize("name", PATTERNS)
def test_a_hotter_pattern_fires_faster_than_a_cooler_one(name: str) -> None:
    cool = rage[name](0, "a", "b")
    hot = rage[name](4.5, "a", "b")
    assert min(s["every"] for s in hot) < min(s["every"] for s in cool)


def test_a_sharing_pattern_fires_less_often_than_a_full_one() -> None:
    full = rage["spirals"](2, "a", "b", 1)
    shared = rage["spirals"](2, "a", "b", 0.5)
    assert shared[0]["every"] == pytest.approx(full[0]["every"] * 2)


def test_spirals_are_two_rings_turning_opposite_ways() -> None:
    a, b = rage["spirals"](0, "x", "y")
    assert a["shape"]["kind"] == b["shape"]["kind"] == "ring"
    assert a["shape"]["turnDeg"] == 13 and b["shape"]["turnDeg"] == -17
    assert b["first"] == pytest.approx(a["first"] + a["every"] / 2)


def test_curtain_sweeps_eight_fans_and_a_ring() -> None:
    volleys = rage["curtain"](0, "x", "y")
    fans = [v for v in volleys if v["shape"]["kind"] == "fan"]
    rings = [v for v in volleys if v["shape"]["kind"] == "ring"]
    assert len(fans) == 8 and len(rings) == 1
    assert [f["shape"]["headingDeg"] for f in fans] == [-40, -20, 0, 20, 40, 20, 0, -20]


def test_vortex_has_a_spiral_and_bursts_at_the_player() -> None:
    spiral, bursts = rage["vortex"](0, "x", "y")
    assert spiral["shape"]["count"] == max(3, arms(0) - 2)
    assert bursts["shape"]["kind"] == "burst"
    assert bursts["shape"]["count"] == 3


def test_real_bosses_angry_patterns_are_built_from_the_rage_record() -> None:
    assert OVERLORD.rage and STORM_PETREL.rage
    assert all(v["from"] == "core" for v in STORM_PETREL.rage)
    assert volley.aimed  # the builders the patterns use are the kit's
