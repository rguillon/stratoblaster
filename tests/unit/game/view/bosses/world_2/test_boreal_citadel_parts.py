# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/boreal_citadel_parts.py`: its aurora cannons."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import muzzle_kinds, turret_drawings, turret_point
from helpers.view_probes import probe_builder

from game.view.bosses.world_2.boreal_citadel_model import build_boreal_citadel


@pytest.mark.parametrize("piece", ["cannon-left", "cannon-right"])
def test_fb_boreal_citadel_07_an_aurora_cannon_turret_fires_its_laser_over_its_pivot(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_boreal_citadel)
    cannon = turret_drawings(capture)[piece]
    assert muzzle_kinds(cannon) == ["laser"]
    # The lens sits ahead of the turret, on its line (its laser leaves straight down the screen).
    tip = cannon["muzzles"][0][0]
    pivot = turret_point(capture.design, piece)
    assert tip[0] == pytest.approx(pivot[0])
    assert tip[2] > pivot[2]
    # Its charge coils and lens light up as it charges.
    assert len(cannon["parts"].charge.geometry.positions) > 0
