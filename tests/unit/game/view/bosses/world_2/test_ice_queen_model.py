# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/ice_queen_model.py`: its crown shards."""

from typing import Any
from unittest.mock import MagicMock

from game.config.record import record
from game.view.bosses.world_2 import ice_queen_model as module


def _shard_muzzles(monkeypatch: Any, part_id: str) -> list[Any]:
    """Draw the shard `part_id`; return the muzzles it hands to `ice_shard`."""
    handed: list[Any] = []
    monkeypatch.setattr(module, "ice_shard", lambda _p, muzzles, _h: handed.append(muzzles))
    module.shard_part(part_id)(MagicMock())
    return handed[0]


def test_mb_ice_queen_03_a_crown_shard_takes_its_muzzles_from_the_design(
    monkeypatch: Any,
) -> None:
    assert _shard_muzzles(monkeypatch, "shard-1") == module.ICE_QUEEN.guns["shard-1"].gun


def test_mb_ice_queen_03_a_shard_without_guns_gets_no_muzzles(monkeypatch: Any) -> None:
    monkeypatch.setitem(module.ICE_QUEEN.guns, "shard-unarmed", record({"turret": [0, 0]}))
    monkeypatch.setitem(module.ICE_QUEEN.guns, "shard-missing", None)
    assert _shard_muzzles(monkeypatch, "shard-unarmed") == []
    assert _shard_muzzles(monkeypatch, "shard-missing") == []
