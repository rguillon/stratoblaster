"""Unit tests of `src/game/config/enemies_veteran.py`."""

import math

import pytest

from game.config.enemies_veteran import (
    MANTIS_ARM,
    MANTIS_SHOULDER,
    VETERAN_CONFIG,
    bullet,
    mantis_muzzles,
    mantis_tip,
    radius,
)

VETERAN_KINDS = ["wasp", "mortar", "mantis", "phantom", "minelayer"]


def test_p05_r14_each_veteran_kind_has_positive_health() -> None:
    for kind in VETERAN_KINDS:
        assert VETERAN_CONFIG[kind].stats.health > 0, kind


def test_p05_r14_veteran_radius_is_a_fraction_of_half_the_model_size() -> None:
    assert radius(1) == pytest.approx(34 * 0.85 / 2)


def test_p05_r14_bullet_defaults_to_a_size_of_four() -> None:
    assert bullet("x", 50) == {"speed": 50, "radius": 4, "style": "x"}


def test_p05_r14_mantis_arm_tip_is_mirrored_by_side() -> None:
    right = mantis_tip(1, MANTIS_ARM.length)
    left = mantis_tip(-1, MANTIS_ARM.length)
    assert left[0] == pytest.approx(-right[0])
    assert left[1] == pytest.approx(right[1])


def test_p05_r14_mantis_arm_tip_is_at_the_arm_length_from_its_shoulder() -> None:
    tip = mantis_tip(1, 10)
    dx = tip[0] - MANTIS_SHOULDER[0]
    dy = tip[1] - MANTIS_SHOULDER[1]
    assert math.hypot(dx, dy) == pytest.approx(10)


def test_p05_r14_mantis_fires_two_muzzles_along_each_blade() -> None:
    muzzles = mantis_muzzles(1)
    assert len(muzzles) == 2
    assert muzzles[0][0] != pytest.approx(muzzles[1][0])
