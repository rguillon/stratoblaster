# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/reef_warden_model.py`: the Reef Warden's turrets."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.mini_bosses import REEF_WARDEN
from game.view.bosses.reef_warden_model import build_reef_warden


def test_mb_reef_warden_03_its_model_draws_every_gun_mount_where_its_design_puts_it(
    monkeypatch: Any,
) -> None:
    """MB-REEF-WARDEN-03: its model draws every gun mount where its design puts it (BOSS-58).

    Its guns are the shared mount models (`boss_gun_models`), no turret drawing of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_reef_warden)
    check_mounts(mounts, REEF_WARDEN)
