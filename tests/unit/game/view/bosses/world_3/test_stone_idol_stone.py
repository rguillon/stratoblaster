# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/stone_idol_stone.py`: straight bars."""

import pytest
from helpers.view_probes import paths, recorder

from game.view.bosses.world_3 import stone_idol_stone as module


def test_a_bar_is_a_box_as_long_as_the_gap_between_its_ends() -> None:
    builder, log = recorder()
    module.bar(builder, [0.0, 0.0, 0.0], [3.0, 0.0, 4.0], [1.0, 0.5], [0.1, 0.2, 0.3])
    assert paths(log) == ["box"]
    size, color = log[0][1][:2]
    assert size == [1.0, 0.5, pytest.approx(5.0)]
    assert color == [0.1, 0.2, 0.3]


def test_a_bar_between_two_equal_points_is_not_drawn() -> None:
    builder, log = recorder()
    module.bar(builder, [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 0.5], [0.1, 0.2, 0.3])
    assert log == []
