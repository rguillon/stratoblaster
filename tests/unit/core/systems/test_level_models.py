"""Unit tests of `src/core/systems/level_models.py`."""

from types import SimpleNamespace
from typing import Any

from core.entities.enemy import EnemyEntry, EnemyKindDefinition
from core.systems.boss_fights import LevelBoss
from core.systems.level_models import level_model_keys
from core.systems.wave_runner import Wave

TOP = EnemyEntry("top", 0.5)


def _kind(id: str, models: list[str]) -> EnemyKindDefinition:
    return EnemyKindDefinition(id, id, lambda area: [SimpleNamespace(model=m) for m in models])


def _boss(id: str, model: str) -> Any:
    return SimpleNamespace(id=id, name=id, spawn=lambda area: SimpleNamespace(model=model))


def _area(entry: EnemyEntry | None) -> Any:
    return SimpleNamespace(entry=entry)


KINDS = [_kind("scout", ["scout"]), _kind("swarm", ["gnat", "gnat"]), _kind("tank", ["tank"])]
BOSSES = [_boss("dreadnought", "dreadnought-model"), _boss("other", "other")]


def test_p13_r03_the_models_of_a_level_are_those_of_its_waves_bosses_and_extras_once_each() -> None:
    waves = [
        Wave(0, "swarm", 2, 1, TOP),
        Wave(10, "scout", 1, 0, TOP),
        Wave(20, "swarm", 1, 0, TOP),
    ]
    bosses = [LevelBoss("dreadnought", "final", 100)]
    keys = level_model_keys(waves, bosses, KINDS, BOSSES, _area, ["pod", "gnat"])
    assert keys == ["gnat", "scout", "dreadnought-model", "pod"]


def test_p13_r03_unknown_kinds_and_bosses_give_no_model() -> None:
    keys = level_model_keys(
        [Wave(0, "ghost", 1, 0, TOP)], [LevelBoss("x", "mini", 1)], KINDS, BOSSES, _area, []
    )
    assert keys == []
