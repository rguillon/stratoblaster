# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the loft station lookups the bosses' drawn armour uses (D-254)."""

import pytest

from game.view.bosses import final_boss_shells
from game.view.bosses.world_2 import loft_spans
from game.view.bosses.world_3 import river_leviathan_model

STATIONS = [[-10.0, 2.0, 0.0, 4.0], [0.0, 4.0, 0.0, 8.0], [10.0, 2.0, 0.0, 4.0]]


def test_a_shell_station_is_interpolated_and_the_last_one_past_the_end() -> None:
    assert final_boss_shells.station_at(STATIONS, -5) == pytest.approx([-5, 3, 0, 6])
    assert final_boss_shells.station_at(STATIONS, 20) == STATIONS[2]


def test_a_loft_span_station_past_the_end_keeps_the_last_section() -> None:
    assert loft_spans.station_at(STATIONS, 5) == pytest.approx([5, 3, 0, 6])
    assert loft_spans.station_at(STATIONS, 20) == [20, 2, 0, 4]


def test_the_leviathan_head_past_its_nose_is_its_last_station() -> None:
    head = river_leviathan_model.HEAD
    assert river_leviathan_model._station(head[len(head) - 1][0] + 50) == head[len(head) - 1]
