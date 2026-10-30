"""Unit tests of `src/game/sim/boss_kinds.py`."""

import pytest
from helpers.config_checks import assert_boss_design
from helpers.enemy_steps import area

from core.entities.boss import Boss
from game.sim.boss_kinds import BOSS_DESIGNS, BOSS_KINDS
from game.sim.bosses.world_boss import WorldBoss


def test_p07_r05_every_boss_design_of_the_game_is_a_kind_once() -> None:
    ids = [kind.id for kind in BOSS_KINDS]
    assert len(ids) == len(BOSS_DESIGNS) == 40
    assert len(ids) == len(set(ids))
    assert ids == [design.id for design in BOSS_DESIGNS]


def test_p07_r05_each_kind_is_named_after_its_design() -> None:
    for kind, design in zip(BOSS_KINDS, BOSS_DESIGNS, strict=True):
        assert kind.name == design.stats["name"]


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=lambda d: d.id)
def test_p07_r05_every_design_is_well_formed(design) -> None:
    assert_boss_design(design)


def test_p07_r05_a_spawned_boss_is_a_world_boss_that_comes_in_from_the_top() -> None:
    kind = BOSS_KINDS[0]
    boss = kind.spawn(area(width=480, height=640))
    assert isinstance(boss, WorldBoss)
    assert isinstance(boss, Boss)
    assert boss.y > 640
