# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemy_kinds.py`."""

from typing import Any

import pytest
from helpers.enemy_steps import area

from game.config.enemies import ENEMY_SPAWN_MARGIN
from game.config.enemy_tiers import all_kinds
from game.sim.enemies.strafer import Strafer
from game.sim.enemy_kinds import ENEMY_KINDS, side_pass

TIER_IDS = [
    "hornet",
    "scout",
    "rocketeer",
    "lancer",
    "carrier",
    "wasp",
    "strafer",
    "harrier",
    "sweeper",
    "hatchery",
    "phantom",
    "spinner",
    "mortar",
    "prism",
    "broodmother",
    "splitter",
    "juggernaut",
    "hydra",
    "scissor",
    "hive",
]


def test_enm_01_every_kind_of_the_game_is_listed_once_with_a_unique_id() -> None:
    """Twenty kinds, tier 1 first, each tier in the order of its roles."""
    ids = [kind.id for kind in ENEMY_KINDS]
    assert ids == TIER_IDS
    assert ids == all_kinds()


def test_enm_04_each_kind_has_a_name_and_a_spawn_function() -> None:
    for kind in ENEMY_KINDS:
        assert kind.name
        assert callable(kind.spawn)


def test_enm_08_a_strafer_from_a_left_entry_starts_just_left_of_the_playfield() -> None:
    """Also ENM-STRAFER-05: the Strafer's side pass."""
    kind = next(k for k in ENEMY_KINDS if k.id == "strafer")
    (strafer,) = kind.spawn(area(width=400, side="left", position=0.3))
    assert isinstance(strafer, Strafer)
    assert strafer.x == pytest.approx(-ENEMY_SPAWN_MARGIN)
    assert strafer.heading == pytest.approx(3.14159265 / 2, rel=1e-6)


def test_enm_08_a_strafer_from_a_right_entry_starts_just_right_of_the_playfield() -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == "strafer")
    (strafer,) = kind.spawn(area(width=400, side="right", position=0.3))
    assert strafer.x == pytest.approx(400 + ENEMY_SPAWN_MARGIN)


def test_enm_08_a_side_pass_follows_the_entry_side_and_height() -> None:
    from_left, y = side_pass(area(width=400, height=600, side="left", position=0.5), 0.2)
    assert from_left is True
    assert y == pytest.approx(300)
    from_right, y = side_pass(area(width=400, height=600, side="right", position=0.5), 0.2)
    assert from_right is False


def test_enm_08_a_side_pass_without_an_entry_takes_its_own_height() -> None:
    _, y = side_pass(area(width=400, height=600), 0.25)
    assert y == pytest.approx(150)


@pytest.mark.parametrize(
    "kind",
    [pytest.param(k, id=k.id) for k in ENEMY_KINDS],
)
@pytest.mark.parametrize("side", [None, "top", "left", "right"])
def test_enm_07_every_kind_spawns_a_group_from_any_wave_entry(kind: Any, side: Any) -> None:
    """Also ENM-08: from any wave entry."""
    group = kind.spawn(area(width=400, height=600, side=side, position=0.4))
    assert group
    for enemy in group:
        assert enemy.health > 0


@pytest.mark.parametrize("kind_id", ["hornet", "wasp"])
@pytest.mark.parametrize("side", ["left", "right"])
def test_enm_08_a_diver_from_a_side_entry_starts_outside_that_side_at_the_entry_height(
    kind_id: str, side: str
) -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == kind_id)
    group = kind.spawn(area(width=400, height=600, side=side, position=0.5))
    assert group
    for enemy in group:
        if side == "left":
            assert enemy.x == pytest.approx(-ENEMY_SPAWN_MARGIN)
        else:
            assert enemy.x == pytest.approx(400 + ENEMY_SPAWN_MARGIN)
        assert 200 < enemy.y < 400


@pytest.mark.parametrize("kind_id", ["hornet", "wasp"])
def test_enm_08_a_diver_from_the_top_still_starts_above_the_playfield(kind_id: str) -> None:
    kind = next(k for k in ENEMY_KINDS if k.id == kind_id)
    for enemy in kind.spawn(area(width=400, height=600, side="top", position=0.5)):
        assert enemy.y > 600
