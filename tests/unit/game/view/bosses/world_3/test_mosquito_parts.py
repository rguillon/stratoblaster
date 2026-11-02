# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/mosquito_parts.py`: the proboscis's needle."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    geometry_size,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder

from game.view.bosses.world_3 import mosquito_parts as module
from game.view.bosses.world_3.mosquito_model import build_mosquito


def test_mb_mosquito_03_the_needle_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, build_mosquito)
    needle = turret_drawings(capture)["proboscis"]
    assert muzzle_kinds(needle) == ["laser"]
    assert needle["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, "proboscis", "laser")[0]
    )
    # Its point glows as the laser charges.
    assert len(needle["parts"].charge.geometry.positions) > 0


def test_mb_mosquito_03_no_needle_is_drawn_when_the_design_has_no_laser(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "MOSQUITO_NEEDLE", [])
    assert geometry_size(drawn_at(module.needle, [0.0, 4.0, 30.0])) == 0
