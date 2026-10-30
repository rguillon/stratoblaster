"""Unit tests of `src/game/config/enemies_elite.py`."""

import math

import pytest

from game.config.enemies_elite import (
    ELITE_CONFIG,
    HYDRA_NECKS,
    aim_from,
    along_aim,
    around,
    fold_entries,
    hydra_heads,
    orbiter_drones,
    radius,
    scissor_arms,
    swing,
)


def test_p05_r19_aim_from_points_the_heading_at_the_target() -> None:
    assert aim_from([0, 0], [0, -10]) == pytest.approx(0)
    assert aim_from([10, 0], [0, 0]) == pytest.approx(math.pi / 2)


def test_p05_r19_along_aim_walks_back_from_a_point_along_the_heading() -> None:
    assert along_aim([0, 10], 0, 4) == pytest.approx([0, 6])


def test_p05_r19_around_places_points_evenly_on_a_circle() -> None:
    points = around(4, 10, 2)
    assert len(points) == 4
    for x, y, height in points:
        assert math.hypot(x, y) == pytest.approx(10)
        assert height == 2


def test_p05_r19_fold_entries_builds_a_dict_from_key_value_pairs() -> None:
    assert fold_entries([["a", 1], ["b", 2]]) == {"a": 1, "b": 2}


def test_p05_r19_swing_is_a_record_of_amplitude_period_and_phase() -> None:
    assert swing(15, 2, 0.5) == {"amplitudeDeg": 15, "period": 2, "phase": 0.5}


def test_p05_r19_elite_radius_is_a_fraction_of_half_the_model_size() -> None:
    assert radius(2) == pytest.approx(2 * 34 * 0.85 / 2)


def test_p05_r19_hydra_necks_each_have_a_pivot_and_a_head() -> None:
    assert HYDRA_NECKS
    for neck in HYDRA_NECKS:
        assert len(neck["pivot"]) == 2 and len(neck["head"]) == 2


def test_p05_r19_hydra_heads_are_one_per_neck_and_the_list_is_exposed_on_the_config() -> None:
    assert len(hydra_heads()) == len(HYDRA_NECKS)
    assert ELITE_CONFIG.hydra is not None


def test_p05_r19_scissor_has_two_mirrored_arms() -> None:
    arms = scissor_arms()
    assert len(arms) == 2
    assert arms[0]["pivot"][0] == pytest.approx(-arms[1]["pivot"][0])


def test_p05_r19_orbiter_has_three_drones_each_on_a_ring_round_its_centre() -> None:
    drones = orbiter_drones()
    assert [d["id"] for d in drones] == ["drone-0", "drone-1", "drone-2"]
    radii = {round(math.hypot(*d["centre"]), 6) for d in drones}
    assert len(radii) == 1
