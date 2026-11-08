# Copyright (c) 2026 Renaud Guillon
"""The tier mix of the assembled levels (ENM-50, D-283): waves, filler and bosses' quiet in."""

from typing import Any

import pytest

from game.config.enemy_tiers import ENEMY_TIERS
from game.config.wave_plans import GROUP_SIZE, kinds_of, tier_mix
from game.sim.world_1 import WORLD_1
from game.sim.world_2 import WORLD_2
from game.sim.world_3 import WORLD_3
from game.sim.world_4 import WORLD_4

WORLDS = [WORLD_1, WORLD_2, WORLD_3, WORLD_4]
LEVELS = [(world, level) for world in range(1, 5) for level in range(1, 6)]
TIER_OF = {kind: int(tier) for tier in ENEMY_TIERS for kind in ENEMY_TIERS[tier].kinds.values()}
# How far (percentage points) a tier's share of the ships may be from its target: a wave is one
# kind, so the shares move in steps of a wave.
TOLERANCE = 5


def _ships_by_tier(waves: list[Any]) -> dict[int, int]:
    ships: dict[int, int] = {}
    for wave in waves:
        tier = TIER_OF[wave["kind"]]
        ships[tier] = ships.get(tier, 0) + wave["count"] * GROUP_SIZE.get(wave["kind"], 1)
    return ships


@pytest.mark.parametrize(("world", "level"), LEVELS)
def test_enm_50_each_tier_has_its_share_of_the_ships_of_the_level(world: int, level: int) -> None:
    waves = WORLDS[world - 1][level - 1].waves
    ships = _ships_by_tier(waves)
    total = sum(ships.values())
    want = {pair[0]: pair[1] for pair in tier_mix(world, level)}
    assert set(ships) == set(want)
    for tier, percent in want.items():
        assert abs(100 * ships[tier] / total - percent) <= TOLERANCE, (tier, ships, total)


@pytest.mark.parametrize(("world", "level"), LEVELS)
def test_enm_50_every_kind_of_each_tier_of_a_level_comes_in_it(world: int, level: int) -> None:
    waves = WORLDS[world - 1][level - 1].waves
    assert {wave["kind"] for wave in waves} == set(kinds_of(world, level))
