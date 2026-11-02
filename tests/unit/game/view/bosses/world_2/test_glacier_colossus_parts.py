# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/glacier_colossus_parts.py`: its cutter lasers."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import design_muzzles, drawn_at, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.view.bosses.world_2 import glacier_colossus_parts as module
from game.view.bosses.world_2.glacier_colossus_model import build_glacier_colossus


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-9), module._sign(0), module._sign(9)] == [-1, 0, 1]


@pytest.mark.parametrize("piece", ["cutter-left", "cutter-right"])
def test_fb_glacier_colossus_03_a_cutter_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_glacier_colossus)
    cutter = turret_drawings(capture)[piece]
    assert muzzle_kinds(cutter) == ["laser"]
    assert cutter["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, piece, "laser")[0]
    )
    assert len(cutter["parts"].flesh.geometry.positions) > 0


def test_fb_glacier_colossus_03_a_cutter_has_no_laser_when_the_design_gives_it_none(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(module, "COLOSSUS_CUTTER_LASER", [])
    cutter = drawn_at(module.cutter, [80.0, 0.0, 42.0])
    assert cutter["muzzles"] == []
    # The pod, its stripes and the emitter's ring are still drawn.
    assert len(cutter["parts"].flesh.geometry.positions) > 0
    assert len(cutter["parts"].neon.geometry.positions) > 0
