# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/sentinel_model.py`: the Sentinel's hull guns."""

from typing import Any

from helpers.bosses_top_turrets import check_turret, drawn_turrets, read_as_records

from game.view.bosses import sentinel_model
from game.view.bosses.sentinel_model import _sign_of, build_sentinel


def test_mb_sentinel_01_a_hull_gun_on_each_outer_flank_turns_on_its_turret(
    monkeypatch: Any,
) -> None:
    """MB-SENTINEL-01: a gun growth on each body's outer flank, its twin barrels on a turret.

    Their specs are dict literals read by attribute (`read_as_records`).
    """
    read_as_records(monkeypatch, sentinel_model, "turret")
    turrets = drawn_turrets(monkeypatch, build_sentinel)
    assert sorted(turrets) == ["gun-left", "gun-right"]
    for turret in turrets.values():
        check_turret(turret)


def test_sign_of_is_math_sign() -> None:
    assert [_sign_of(-3), _sign_of(0), _sign_of(2.5)] == [-1, 0, 1]
