# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/mesa_fortress_model.py`: the Mesa Fortress's guns."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.final_bosses import MESA_FORTRESS
from game.view.bosses.mesa_fortress_model import build_mesa_fortress


def test_fb_mesa_fortress_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """FB-MESA-FORTRESS-03: its lances, its silos and every gun mount (BOSS-58).

    The core's fan turret on its brow and its rotor are the shared mount models, no turret drawing
    of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_mesa_fortress)
    check_mounts(mounts, MESA_FORTRESS)
    assert any(mount.piece == "core" for mount, _model, _parts in mounts.values())
