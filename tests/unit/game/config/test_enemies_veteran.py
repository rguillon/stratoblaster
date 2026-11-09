# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/enemies_veteran.py`."""

import pytest

from game.config.enemies_veteran import (
    VETERAN_CONFIG,
    bullet,
    radius,
)

VETERAN_KINDS = ["wasp", "mortar", "phantom"]


def test_enm_06_each_veteran_kind_has_positive_health() -> None:
    """Also each veteran kind's health and points requirement (specs/enemies/<kind>.md)."""
    for kind in VETERAN_KINDS:
        assert VETERAN_CONFIG[kind].stats.health > 0, kind


def test_enm_11_veteran_radius_is_a_fraction_of_half_the_model_size() -> None:
    assert radius(1) == pytest.approx(34 * 0.85 / 2)


def test_enm_16_bullet_defaults_to_a_size_of_four() -> None:
    assert bullet("x", 50, 20) == {"speed": 50, "radius": 4, "style": "x", "damage": 20}
