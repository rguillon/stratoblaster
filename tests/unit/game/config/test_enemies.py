# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/enemies.py`."""

import pytest

from game.config.enemies import (
    ENEMY_CONFIG,
    ENEMY_SPAWN_MARGIN,
    ENEMY_UNIT,
    HITBOX,
    bullet,
    radius,
)

FIRST_KINDS = [
    "hornet",
    "scout",
    "strafer",
    "spinner",
    "lancer",
    "rocketeer",
    "splitter",
    "carrier",
]


def test_enm_06_each_first_kind_has_stats_with_positive_health() -> None:
    """Also each basic kind's health and points requirement (specs/enemies/<kind>.md)."""
    for kind in FIRST_KINDS:
        assert ENEMY_CONFIG[kind].stats.health > 0, kind


def test_enm_05_the_unit_and_hitbox_are_the_medium_ship_scale() -> None:
    """Also ENM-11 (the hit radius factor)."""
    assert ENEMY_UNIT == 34
    assert pytest.approx(0.85) == HITBOX


def test_enm_11_a_hit_radius_is_a_fraction_of_half_the_model_size() -> None:
    assert radius(2) == pytest.approx(2 * ENEMY_UNIT * HITBOX / 2)
    assert radius(4) == pytest.approx(2 * radius(2))


def test_enm_16_bullets_carry_the_style_and_speed_given() -> None:
    assert bullet("dart", 90, 15) == {"speed": 90, "radius": 4, "style": "dart", "damage": 15}


def test_enm_07_spawn_margin_is_positive() -> None:
    assert ENEMY_SPAWN_MARGIN > 0


def test_enm_splitter_09_splitter_pod_is_a_smaller_kind_than_the_splitter() -> None:
    """The pods of ENM-SPLITTER-08."""
    assert ENEMY_CONFIG.splitterPod.stats.health < ENEMY_CONFIG.splitter.stats.health


def test_enm_splitter_05_the_splitter_is_a_diver_with_no_gun_and_no_path() -> None:
    """Tier 4's diver: dive tunables like a Hornet's, nothing to shoot with."""
    splitter = ENEMY_CONFIG.splitter
    for name in ("entrySpeed", "pause", "diveAcceleration", "diveMaxSpeed"):
        assert splitter[name] > 0, name
    assert 0 < splitter.stopRange[0] < splitter.stopRange[1] < 1
    for name in ("bullet", "fireInterval", "path", "muzzles"):
        assert name not in splitter, name


def test_enm_splitter_09_the_splitter_is_tougher_than_a_hornet() -> None:
    assert ENEMY_CONFIG.splitter.stats.health > ENEMY_CONFIG.hornet.stats.health
    assert ENEMY_CONFIG.splitter.stats.points > ENEMY_CONFIG.hornet.stats.points
