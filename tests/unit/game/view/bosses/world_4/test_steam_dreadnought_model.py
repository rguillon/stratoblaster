# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_4/steam_dreadnought_model.py`: bridge and bow."""

from typing import Any

from helpers.bosses_worlds_probe import muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_4 import steam_dreadnought_model as module


def test_the_bridge_beacon_is_where_the_core_rings_leave_from() -> None:
    assert muzzle_kinds(drawn(module._draw_bridge)) == ["ring"]


def test_the_bridge_has_no_beacon_when_the_design_has_no_ring_muzzle(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "DREAD_BEACON", [])
    result = drawn(module._draw_bridge)
    assert result["muzzles"] == []
    # Its tiers and mast stay.
    assert len(result["parts"].hull.geometry.positions) > 0


def test_the_bow_has_its_twin_guns_and_its_laser_ram() -> None:
    kinds = muzzle_kinds(drawn(module._draw_bow))
    assert kinds == ["gun"] * len(module.DREAD_BOW_GUNS) + ["laser"]


def test_the_bow_keeps_its_guns_when_the_design_has_no_ram_lens(monkeypatch: Any) -> None:
    monkeypatch.setattr(module, "DREAD_LENS", [])
    assert muzzle_kinds(drawn(module._draw_bow)) == ["gun"] * len(module.DREAD_BOW_GUNS)
