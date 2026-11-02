# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/sky_temple_details.py`: points on a tier's edge."""

from game.view.bosses.world_3 import sky_temple_details as module


def test_a_drape_point_on_an_east_or_west_edge_runs_along_z() -> None:
    assert module.drape_point(5, 1, 20, 2, 7) == [22, 7, 5]
    assert module.drape_point(5, -1, 20, 2, 7) == [-22, 7, 5]


def test_a_drape_point_on_the_back_edge_runs_along_x() -> None:
    assert module.drape_point(5, 0, 20, 2, 7) == [5, 7, -22]
