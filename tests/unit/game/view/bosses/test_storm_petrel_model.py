# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/storm_petrel_model.py`: the Storm Petrel's cockpit turret."""

from typing import Any

from helpers.bosses_top_turrets import check_turret, drawn_turrets

from game.view.bosses.storm_petrel_model import build_storm_petrel


def test_fb_storm_petrel_03_its_cockpit_turret_turns_on_its_barbette(monkeypatch: Any) -> None:
    turrets = drawn_turrets(monkeypatch, build_storm_petrel)
    assert sorted(turrets) == ["core"]
    check_turret(turrets["core"])
