# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/reef_warden_model.py`: the Reef Warden's turrets."""

from typing import Any

from helpers.bosses_top_turrets import check_turret, drawn_turrets, read_as_records

from game.view.bosses import reef_warden_model
from game.view.bosses.reef_warden_model import build_reef_warden


def test_mb_reef_warden_01_its_prow_and_side_cannons_turn_on_turrets_aiming_their_guns(
    monkeypatch: Any,
) -> None:
    """MB-REEF-WARDEN-01: a prow cannon on its snout and two side cannons, each on its turret.

    Their specs are dict literals read by attribute (`read_as_records`).
    """
    read_as_records(monkeypatch, reef_warden_model, "turret")
    turrets = drawn_turrets(monkeypatch, build_reef_warden)
    assert sorted(turrets) == ["cannon-left", "cannon-right", "core"]
    for turret in turrets.values():
        check_turret(turret)
