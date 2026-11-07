# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/enemy_tiers.py` (ENM-01, ENM-49, ENM-50)."""

import itertools

from core.math.color import hue_saturation
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_tiers import (
    ENEMY_TIERS,
    ROLES,
    all_kinds,
    tier_kinds,
    tier_look,
    tier_of,
    world_kinds,
)
from game.config.readability import READABILITY

ENEMY_FAMILY = READABILITY.families.enemy


def test_enm_01_each_tier_has_one_kind_of_each_of_the_five_roles() -> None:
    for tier in range(1, 5):
        kinds = ENEMY_TIERS[str(tier)].kinds
        assert sorted(kinds.keys()) == sorted(ROLES)
        assert len(set(tier_kinds(tier))) == 5


def test_enm_01_the_twenty_kinds_are_listed_once_tier_by_tier() -> None:
    kinds = all_kinds()
    assert len(kinds) == 20
    assert len(set(kinds)) == 20
    assert kinds[:5] == ["hornet", "scout", "rocketeer", "lancer", "carrier"]
    assert kinds[15:] == ["splitter", "hydra", "juggernaut", "scissor", "hive"]


def test_enm_50_a_world_uses_the_kinds_of_its_tier() -> None:
    for world in range(1, 5):
        assert ENEMY_TIERS[str(world)].world == world
        assert world_kinds(world) == tier_kinds(world)


def test_enm_49_a_kind_belongs_to_its_tier_and_the_splitter_pod_to_the_splitter() -> None:
    assert tier_of("lancer") == 1
    assert tier_of("wasp") == 2
    assert tier_of("mortar") == 3
    assert tier_of("hive") == 4
    assert tier_of("splitter-pod") == 4
    assert tier_of("a-boss") == 0
    assert tier_look("a-boss") is None
    assert tier_look("scissor") is ENEMY_TIERS["4"]


def test_enm_49_the_tier_neons_are_in_the_enemy_family_and_twenty_degrees_apart() -> None:
    hues = []
    for tier in range(1, 5):
        theme = ENEMY_TIERS[str(tier)]
        hue, saturation = hue_saturation(theme.neon)
        assert ENEMY_FAMILY["from"] <= theme.hue <= ENEMY_FAMILY["to"]
        assert abs(hue - theme.hue) < 2
        assert saturation >= ENEMY_FAMILY["minSaturation"]
        hues.append(theme.hue)
    hues.sort()
    assert all(b - a >= 20 for a, b in itertools.pairwise(hues))


def test_enm_49_every_kind_has_its_tier_s_neon() -> None:
    for kind in all_kinds():
        assert ENEMY_LOOK.neon[kind] == tier_look(kind).neon
