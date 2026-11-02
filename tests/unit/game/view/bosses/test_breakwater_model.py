# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/breakwater_model.py`: the Breakwater's turrets."""

from typing import Any

from helpers.bosses_top_turrets import check_turret, drawn_turrets, read_as_records

from game.view.bosses import breakwater_model
from game.view.bosses.breakwater_model import build_breakwater


def test_mb_breakwater_01_its_mouth_gun_and_mortars_turn_on_turrets_aiming_their_guns(
    monkeypatch: Any,
) -> None:
    """MB-BREAKWATER-01: a gun in its mouth and two barnacle mortars, each on its turret.

    Their specs are dict literals read by attribute (`read_as_records`).
    """
    read_as_records(monkeypatch, breakwater_model, "turret")
    turrets = drawn_turrets(monkeypatch, build_breakwater)
    assert sorted(turrets) == ["core", "mortar-left", "mortar-right"]
    for turret in turrets.values():
        check_turret(turret)
