# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/refinery_titan_parts.py` and the Refinery Titan's guns."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts
from helpers.view_probes import drawn

from game.config.bosses.final_bosses import REFINERY_TITAN
from game.view.bosses.refinery_titan_model import build_refinery_titan
from game.view.bosses.refinery_titan_parts import draw_missile_battery, draw_turret


def test_fb_refinery_titan_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """FB-REFINERY-TITAN-03: its five parts and every gun mount (BOSS-58).

    Its turrets' rotors and its missile battery's ports are the shared mount models.
    """
    mounts = drawn_mounts(monkeypatch, build_refinery_titan)
    check_mounts(mounts, REFINERY_TITAN)


def test_fb_refinery_titan_03_its_turret_and_battery_are_growths_under_their_mounts() -> None:
    """Their own drawings carry no gun: their mounts' models do (BOSS-58)."""
    for draw in [draw_turret, draw_missile_battery]:
        part = drawn(lambda p, d=draw: d(p, [10, 0, 20]))
        assert len(part["parts"].hull.geometry.positions) > 0
        assert part["muzzles"] == []
