# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_3/river_leviathan_body.py`: its ring turrets."""

from typing import Any

import pytest
from helpers.bosses_worlds_probe import design_muzzles, muzzle_kinds, turret_drawings
from helpers.view_probes import probe_builder

from game.view.bosses.world_3.river_leviathan_model import build_river_leviathan


def test_fb_river_leviathan_04_each_segment_turret_fires_from_its_emitter(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, build_river_leviathan)
    turrets = turret_drawings(capture)
    assert sorted(turrets) == ["segment-1", "segment-2", "segment-3", "segment-4"]
    for piece, turret in turrets.items():
        assert muzzle_kinds(turret) == ["gun"]
        assert turret["muzzles"][0][0] == pytest.approx(
            design_muzzles(capture.design, piece, "gun")[0]
        )
        # Four lamps around its dome light up as it charges.
        assert len(turret["parts"].charge.geometry.positions) > 0
