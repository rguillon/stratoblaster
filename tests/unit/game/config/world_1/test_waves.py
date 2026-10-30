"""Unit tests of `src/game/config/world_1/waves.py`."""

import pytest
from helpers.config_checks import assert_beats_well_formed, enemy_kind_ids

from game.config.record import record
from game.config.world_1.waves import (
    WAVES_1_1,
    WAVES_1_2,
    WAVES_1_3,
    WAVES_1_4,
    WAVES_1_5,
    WORLD_1_FILLERS,
    denser,
    fill,
    quiet_before,
    wave_script,
)

KINDS = enemy_kind_ids()
SCRIPTS = [WAVES_1_1, WAVES_1_2, WAVES_1_3, WAVES_1_4, WAVES_1_5]


@pytest.mark.parametrize("beats", SCRIPTS)
def test_p06_r07_each_beat_names_a_kind_and_a_side_in_order(beats) -> None:
    assert_beats_well_formed(beats, KINDS)


def test_p06_r07_each_filler_names_known_kinds_and_its_gap_shrinks() -> None:
    for level_id, filler in WORLD_1_FILLERS.items():
        assert filler["kinds"], level_id
        assert set(filler["kinds"]) <= KINDS, level_id
        start, end = filler["maxGap"]
        assert start >= end > 0, level_id


def test_p06_r07_denser_multiplies_the_groups_of_a_beat_and_rounds_half_up() -> None:
    assert denser([4, "scout", 2, 2, "top", 0.3], 1.5)[2] == 3
    assert denser([4, "scout", 1, 0, "top", 0.3], 1.5) == [4, "scout", 2, 1.5, "top", 0.3, 0.3]


def test_p06_r07_a_single_group_beat_gets_a_wider_spread_when_made_denser() -> None:
    more = denser([4, "gnat", 1, 0, "left", 0.3], 2)
    assert more[6] == pytest.approx(-0.15)


def test_p06_r07_wave_script_turns_seconds_into_distance_at_the_ground_speed() -> None:
    script = wave_script(70, [[4, "scout", 1, 0, "top", 0.5]], density=1)
    assert script == [
        {
            "at": 280,
            "kind": "scout",
            "count": 1,
            "interval": 0,
            "entry": {"side": "top", "position": 0.5},
        }
    ]


def test_p06_r07_quiet_before_drops_the_waves_that_start_just_before_a_boss() -> None:
    script = [{"at": 90}, {"at": 95}, {"at": 110}]
    kept = quiet_before(script, [100], 10)
    assert [w["at"] for w in kept] == [90, 110]


def test_p06_r07_fill_adds_filler_groups_into_the_lulls_between_beats() -> None:
    beats = [[0, "gnat", 1, 0, "top", 0.5], [20, "gnat", 1, 0, "top", 0.5]]
    filler = record({"kinds": ["scout"], "maxGap": [5, 5]})
    filled = fill(beats, filler)
    assert len(filled) > len(beats)
    assert all(b[0] >= 0 for b in filled)
    assert filled == sorted(filled, key=lambda b: b[0])
