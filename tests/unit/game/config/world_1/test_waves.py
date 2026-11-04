# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/world_1/waves.py`."""

from typing import Any

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
def test_wld_1_19_each_beat_names_a_kind_and_a_side_in_order(beats: Any) -> None:
    """Each level's written beats (LVL-1-1-09 … LVL-1-5-09), of known kinds (WLD-1-17)."""
    assert_beats_well_formed(beats, KINDS)


def test_wld_1_21_each_filler_names_known_kinds_and_its_gap_shrinks() -> None:
    """Each level's filler (WLD-1-21)."""
    for level_id, filler in WORLD_1_FILLERS.items():
        assert filler["kinds"], level_id
        assert set(filler["kinds"]) <= KINDS, level_id
        start, end = filler["maxGap"]
        assert start >= end > 0, level_id


def test_wld_1_20_denser_multiplies_the_groups_of_a_beat_and_rounds_half_up() -> None:
    assert denser([4, "scout", 2, 2, "top", 0.3], 1.5)[2] == 3
    assert denser([4, "scout", 1, 0, "top", 0.3], 1.5) == [4, "scout", 2, 1.5, "top", 0.3, 0.3]


def test_wld_1_20_a_single_group_beat_gets_a_wider_spread_when_made_denser() -> None:
    more = denser([4, "gnat", 1, 0, "left", 0.3], 2)
    assert more[6] == pytest.approx(-0.15)


def test_wld_1_19_wave_script_turns_seconds_into_distance_at_the_ground_speed() -> None:
    """Waves are triggered by distance (GAME-LEVEL-01)."""
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


def test_game_level_05_quiet_before_drops_the_waves_that_start_just_before_a_boss() -> None:
    script = [{"at": 90}, {"at": 95}, {"at": 110}]
    kept = quiet_before(script, [100], 10)
    assert [w["at"] for w in kept] == [90, 110]


def test_wld_1_21_fill_adds_filler_groups_of_the_beats_kind_into_the_lulls() -> None:
    beats = [[0, "scout", 1, 0, "top", 0.5], [20, "scout", 1, 0, "top", 0.5]]
    filler = record({"kinds": ["scout"], "maxGap": [5, 5]})
    filled = fill(beats, filler)
    assert len(filled) > len(beats)
    assert all(b[0] >= 0 for b in filled)
    assert all(b[1] == "scout" for b in filled)
    assert filled == sorted(filled, key=lambda b: b[0])


def test_wld_1_21_fill_never_brings_in_a_kind_the_wave_before_it_was_not() -> None:
    beats = [[0, "hornet", 1, 0, "top", 0.5], [30, "scout", 1, 0, "top", 0.5]]
    filled = fill(beats, record({"kinds": ["hornet", "scout"], "maxGap": [5, 5]}))
    assert {b[1] for b in filled if 0 < b[0] < 30} == {"hornet"}


def test_wld_1_21_the_heavy_kinds_are_left_alone_in_their_lull() -> None:
    beats = [[0, "carrier", 1, 0, "top", 0.5], [30, "carrier", 1, 0, "top", 0.5]]
    assert fill(beats, record({"kinds": ["hornet"], "maxGap": [5, 5]})) == beats


def test_wld_1_21_the_filler_starts_once_the_wave_has_come_in() -> None:
    beats = [[0, "scout", 4, 2, "top", 0.5], [40, "scout", 1, 0, "top", 0.5]]
    filled = fill(beats, record({"kinds": ["scout"], "maxGap": [5, 5]}))
    assert min(b[0] for b in filled if b[0] > 0 and b[0] < 40) >= 6 + 5


def test_wld_1_21_fill_puts_the_beats_in_time_order_first() -> None:
    beats = [[20, "scout", 1, 0, "top", 0.5], [0, "scout", 1, 0, "top", 0.5]]
    filled = fill(beats, record({"kinds": ["scout"], "maxGap": [5, 5]}))
    assert filled[0][:2] == [0, "scout"]
    assert filled == sorted(filled, key=lambda b: b[0])


def test_wld_1_21_a_single_beat_has_no_lull_to_fill() -> None:
    beat = [10, "scout", 1, 0, "top", 0.5]
    assert fill([beat], record({"kinds": ["scout"], "maxGap": [5, 2]})) == [beat]


def test_wld_1_20_a_pincer_beat_keeps_its_alternate_flag_when_made_denser() -> None:
    assert denser([4, "wasp", 3, 1, "left", 0.7, 0, 1], 2) == [4, "wasp", 6, 1, "left", 0.7, 0, 1]
    single = denser([4, "carrier", 1, 0, "top", 0.3, 0.5, 1], 2)
    assert single == [4, "carrier", 2, 1.5, "top", 0.3, 0.5, 1]


def test_wave_script_passes_the_alternate_flag_on() -> None:
    script = wave_script(10, [[1, "wasp", 3, 1, "left", 0.7, 0, 1]], density=1)
    assert script[0]["alternate"] is True
    assert "alternate" not in wave_script(10, [[1, "wasp", 3, 1, "left", 0.7]], density=1)[0]
