# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/breakwater_model.py`: the Breakwater's turrets."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.mini_bosses import BREAKWATER
from game.view.bosses.breakwater_model import build_breakwater


def test_mb_breakwater_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """MB-BREAKWATER-03: its model draws the ram plate, both mortars and every gun mount (BOSS-58).

    Its guns are the shared mount models (`boss_gun_models`), no turret drawing of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_breakwater)
    check_mounts(mounts, BREAKWATER)
