# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/stone_idol_parts.py`: its eyeballs."""

import math
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

from game.view.bosses.world_3 import stone_idol_parts as module
from game.view.bosses.world_3.stone_idol_model import build_stone_idol


def test_an_iris_point_lies_along_the_iris_tilt() -> None:
    point = module.iris_point([1.0, 2.0, 3.0], 5.0, 2.0)
    assert point == [
        1.0,
        pytest.approx(5.0 + 2.0 * math.cos(module.IRIS_TILT)),
        pytest.approx(3.0 + 2.0 * math.sin(module.IRIS_TILT)),
    ]


@pytest.mark.parametrize("piece", ["eye-left", "eye-right"])
def test_mb_stone_idol_03_an_eyeball_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_stone_idol)
    eye = turret_drawings(capture)[piece]
    assert muzzle_kinds(eye) == ["laser"]
    assert eye["muzzles"][0][0] == pytest.approx(design_muzzles(capture.design, piece, "laser")[0])
    # Its iris is a glowing gland.
    assert len(eye["parts"].vein.geometry.positions) > 0


def test_mb_stone_idol_03_no_eyeball_is_drawn_when_the_design_has_no_laser(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "IDOL_EYE", [])
    for x in [-20.0, 20.0]:
        assert geometry_size(drawn_at(module.eyeball, [x, 0.0, 10.0])) == 0
