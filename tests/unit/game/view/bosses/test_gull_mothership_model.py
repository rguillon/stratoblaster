# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/gull_mothership_model.py`: the Gull Mothership's flak."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.final_bosses import GULL_MOTHERSHIP
from game.view.bosses.gull_mothership_model import build_gull_mothership


def test_fb_gull_mothership_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """FB-GULL-MOTHERSHIP-03: its model draws its hangars, flak growths and every gun mount.

    Its guns are the shared mount models (`boss_gun_models`), no turret drawing of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_gull_mothership)
    check_mounts(mounts, GULL_MOTHERSHIP)
