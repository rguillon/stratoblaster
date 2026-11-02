# Copyright (c) 2026 Renaud Guillon
"""The enemy models a level needs (PERF-21).

Those of the enemies its waves and bosses bring, so a level builds its own models while it loads,
not every model of the game.
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from core.entities.enemy import EnemyEntry, EnemyKindDefinition, EnemySpawnArea
    from core.systems.boss_fights import BossKindDefinition, LevelBoss
    from core.systems.wave_runner import Wave
# __pragma__ ("noskip")


def _add(keys: list[str], key: str) -> None:
    if key not in keys:
        keys.append(key)


def level_model_keys(
    waves: "Sequence[Wave]",
    bosses: "Sequence[LevelBoss]",
    kinds: "Sequence[EnemyKindDefinition]",
    boss_kinds: "Sequence[BossKindDefinition]",
    area_of: "Callable[[EnemyEntry | None], EnemySpawnArea]",
    extra: list[str],
) -> list[str]:
    """Return the model keys of the enemies `waves` and `bosses` bring.

    Then `extra` (e.g. the enemies that others send out), each once, in that order. One group of
    each kind is spawned (in the area `area_of` gives for the wave's entry) to read its models;
    unknown kinds give none.
    """
    keys: list[str] = []
    seen: list[str] = []
    for wave in waves:
        if wave.kind in seen:
            continue
        seen.append(wave.kind)
        for kind in kinds:
            if kind.id == wave.kind:
                group: list[Any] = kind.spawn(area_of(wave.entry))
                for enemy in group:
                    _add(keys, enemy.model)
                break
    for boss in bosses:
        for boss_kind in boss_kinds:
            if boss_kind.id == boss.kind:
                _add(keys, boss_kind.spawn(area_of(None)).model)
                break
    for key in extra:
        _add(keys, key)
    return keys
