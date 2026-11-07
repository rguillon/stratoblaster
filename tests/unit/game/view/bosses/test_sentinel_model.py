# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/sentinel_model.py`: the Sentinel's hull guns."""

from typing import Any

from helpers.bosses_top_turrets import check_mounts, drawn_mounts

from game.config.bosses.mini_bosses import SENTINEL
from game.view.bosses.sentinel_model import _sign_of, build_sentinel


def test_mb_sentinel_03_its_model_draws_every_gun_mount(monkeypatch: Any) -> None:
    """MB-SENTINEL-03: its model draws both hull guns, the drone bay and every gun mount (BOSS-58).

    Its guns are the shared mount models (`boss_gun_models`), no turret drawing of its own.
    """
    mounts = drawn_mounts(monkeypatch, build_sentinel)
    check_mounts(mounts, SENTINEL)


def test_sign_of_is_math_sign() -> None:
    assert [_sign_of(-3), _sign_of(0), _sign_of(2.5)] == [-1, 0, 1]
