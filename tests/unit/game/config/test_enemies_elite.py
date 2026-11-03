# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/enemies_elite.py`."""

import math

import pytest

from game.config.enemies import ENEMY_CONFIG
from game.config.enemies_elite import (
    ELITE_CONFIG,
    HYDRA_NECKS,
    aim_from,
    along_aim,
    around,
    fold_entries,
    hydra_heads,
    radius,
    scissor_arms,
    swing,
)


def test_enm_28_aim_from_points_the_heading_at_the_target() -> None:
    assert aim_from([0, 0], [0, -10]) == pytest.approx(0)
    assert aim_from([10, 0], [0, 0]) == pytest.approx(math.pi / 2)


def test_enm_28_along_aim_walks_back_from_a_point_along_the_heading() -> None:
    assert along_aim([0, 10], 0, 4) == pytest.approx([0, 6])


def test_enm_hive_10_around_places_points_evenly_on_a_circle() -> None:
    """Also ENM-HIVE-10 (the Hive's ring)."""
    points = around(4, 10, 2)
    assert len(points) == 4
    for x, y, height in points:
        assert math.hypot(x, y) == pytest.approx(10)
        assert height == 2


def test_enm_27_fold_entries_builds_a_dict_from_key_value_pairs() -> None:
    assert fold_entries([["a", 1], ["b", 2]]) == {"a": 1, "b": 2}


def test_enm_27_swing_is_a_record_of_amplitude_period_and_phase() -> None:
    assert swing(15, 2, 0.5) == {"amplitudeDeg": 15, "period": 2, "phase": 0.5}


def test_enm_11_elite_radius_is_a_fraction_of_half_the_model_size() -> None:
    assert radius(2) == pytest.approx(2 * 34 * 0.85 / 2)


def test_enm_hydra_08_hydra_necks_each_have_a_pivot_and_a_head() -> None:
    assert HYDRA_NECKS
    for neck in HYDRA_NECKS:
        assert len(neck["pivot"]) == 2
        assert len(neck["head"]) == 2


def test_enm_hydra_08_hydra_heads_are_one_per_neck_and_the_list_is_exposed_on_the_config() -> None:
    assert len(hydra_heads()) == len(HYDRA_NECKS)
    assert ELITE_CONFIG.hydra is not None


def test_enm_scissor_09_scissor_has_two_mirrored_arms() -> None:
    arms = scissor_arms()
    assert len(arms) == 2
    assert arms[0]["pivot"][0] == pytest.approx(-arms[1]["pivot"][0])


def test_enm_hydra_14_hydra_launches_slower_homing_missiles_than_the_rocketeer() -> None:
    hydra = ELITE_CONFIG.hydra
    assert "bullet" not in hydra
    assert hydra.missile.speed < ENEMY_CONFIG.rocketeer.missile.speed
    assert hydra.missile.homingSeconds > 0
    assert hydra.headFireInterval > 0.5


def test_enm_hive_09_hive_launches_a_splitter_every_six_seconds() -> None:
    assert ELITE_CONFIG.hive.launchInterval == 6
