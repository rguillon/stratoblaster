# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/world_2/ice_queen_shards.py`: the crown shards."""

from helpers.bosses_worlds_probe import geometry_size, muzzle_kinds
from helpers.view_probes import drawn

from game.view.bosses.world_2 import ice_queen_shards as module


def test_mb_ice_queen_03_a_shard_lies_between_its_two_muzzles() -> None:
    result = drawn(lambda p: module.ice_shard(p, [[-10, 20, 30], [10, 20, 30]], 30))
    assert muzzle_kinds(result) == ["gun", "gun"]
    assert len(result["parts"].hull.geometry.positions) > 0


def test_mb_ice_queen_03_a_shard_with_fewer_than_two_muzzles_is_not_drawn() -> None:
    for muzzles in [[], [[0, 20, 30]]]:
        result = drawn(lambda p, m=muzzles: module.ice_shard(p, m, 30))
        assert result["muzzles"] == []
        assert geometry_size(result) == 0
