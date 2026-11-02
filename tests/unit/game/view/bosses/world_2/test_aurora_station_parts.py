# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/aurora_station_parts.py`: its turrets."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.bosses_worlds_probe import (
    design_muzzles,
    drawn_at,
    geometry_size,
    muzzle_kinds,
    turret_drawings,
)
from helpers.view_probes import probe_builder

from game.view.bosses.world_2 import aurora_station_parts as module
from game.view.bosses.world_2.aurora_station_model import build_aurora_station


def test_sign_is_minus_one_zero_or_one() -> None:
    assert [module._sign(-3), module._sign(0), module._sign(2)] == [-1, 0, 1]


@pytest.mark.parametrize("piece", ["emitter-left", "emitter-right"])
def test_fb_aurora_station_06_an_emitter_turret_fires_its_laser_from_the_design_muzzle(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_aurora_station)
    turret = turret_drawings(capture)[piece]
    assert muzzle_kinds(turret) == ["laser"]
    assert turret["muzzles"][0][0] == pytest.approx(
        design_muzzles(capture.design, piece, "laser")[0]
    )


@pytest.mark.parametrize("piece", ["cryo-left", "cryo-right"])
def test_fb_aurora_station_06_a_cryo_turret_has_one_wide_barrel(
    monkeypatch: Any, piece: str
) -> None:
    capture = probe_builder(monkeypatch, build_aurora_station)
    turret = turret_drawings(capture)[piece]
    assert muzzle_kinds(turret) == ["gun"]
    assert len(turret["parts"].hull.geometry.positions) > 0


def test_cryo_turret_puts_its_hatch_on_the_outer_side(monkeypatch: Any) -> None:
    specs: list[Any] = []
    monkeypatch.setattr(module, "turret", lambda _p, _at, spec: specs.append(spec))
    module.cryo_turret(MagicMock(), [-30.0, 0.0, 4.0])
    module.cryo_turret(MagicMock(), [30.0, 0.0, 4.0])
    assert [spec.hatch for spec in specs] == [1, -1]
    assert [spec.barrels for spec in specs] == [1, 1]


def test_emitter_turret_draws_nothing_without_a_laser_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "AURORA_EMITTER", [])
    for x in [-36.0, 36.0]:
        result = drawn_at(module.emitter_turret, [x, 0.0, 40.0])
        assert result["muzzles"] == []
        assert geometry_size(result) == 0
