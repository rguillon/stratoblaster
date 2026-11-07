# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/storm_petrel_model.py`: the Storm Petrel's cockpit turret."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.final_bosses import STORM_PETREL
from game.view.bosses.storm_petrel_model import build_storm_petrel


def test_fb_storm_petrel_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """FB-STORM-PETREL-03: its model draws its four parts and every gun mount (BOSS-58).

    Its guns are the shared mount models (`boss_gun_models`), no turret drawing of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_storm_petrel)
    check_mounts(mounts, STORM_PETREL)
