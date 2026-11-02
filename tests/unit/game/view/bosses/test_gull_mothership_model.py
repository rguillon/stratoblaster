# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/gull_mothership_model.py`: the Gull Mothership's flak."""

from typing import Any

from helpers.bosses_top_turrets import check_turret, drawn_turrets

from game.view.bosses.gull_mothership_model import build_gull_mothership


def test_fb_gull_mothership_03_its_flak_growths_turn_twin_guns_on_their_crowns(
    monkeypatch: Any,
) -> None:
    turrets = drawn_turrets(monkeypatch, build_gull_mothership)
    assert sorted(turrets) == ["flak-left", "flak-right"]
    for turret in turrets.values():
        check_turret(turret)
        assert len(turret[1]["muzzles"]) == 2
