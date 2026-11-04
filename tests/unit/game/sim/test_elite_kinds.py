# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/elite_kinds.py`."""

from helpers.enemy_steps import area

from game.sim.elite_kinds import ELITE_KINDS


def test_enm_01_the_elite_era_kinds_are_the_four_tier_4_kinds_but_the_splitter() -> None:
    """Tier 4 (ENM-01): ENM-HYDRA-13, ENM-SCISSOR-16, ENM-JUGGERNAUT-16, ENM-HIVE-14."""
    assert [kind.id for kind in ELITE_KINDS] == ["hydra", "scissor", "juggernaut", "hive"]


def test_enm_07_an_elite_spawns_one_enemy_group_per_call() -> None:
    """Also ENM-HIVE-08: a Hive comes in alone."""
    hive = next(k for k in ELITE_KINDS if k.id == "hive")
    assert len(hive.spawn(area())) == 1
