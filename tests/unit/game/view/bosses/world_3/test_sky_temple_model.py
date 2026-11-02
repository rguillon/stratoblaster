# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/sky_temple_model.py`: the twin cannons."""

from typing import Any

from helpers.bosses_worlds_probe import geometry_size
from helpers.view_probes import drawn

from game.view.bosses.world_3 import sky_temple_model as module


def test_fb_sky_temple_03_twin_cannons_stand_either_side_of_the_door() -> None:
    result = drawn(module.draw_cannons)
    assert len(result["muzzles"]) == 2
    assert result["muzzles"][0][0][0] == -result["muzzles"][1][0][0]


def test_fb_sky_temple_03_no_cannons_are_drawn_when_the_design_has_no_guns(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "TEMPLE_GUNS", [])
    assert geometry_size(drawn(module.draw_cannons)) == 0
