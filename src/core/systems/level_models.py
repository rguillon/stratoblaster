"""The enemy models a level needs (P13-R03): those of the enemies its waves and bosses bring, so
a level builds its own models while it loads, not every model of the game.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

from core.entities.enemy import EnemyEntry, EnemyKindDefinition, EnemySpawnArea  # noqa: E402
from core.systems.boss_fights import BossKindDefinition, LevelBoss  # noqa: E402
from core.systems.wave_runner import Wave  # noqa: E402

__pragma__("noskip")


def _add(keys: list[str], key: str) -> None:
    if key not in keys:
        keys.append(key)


def level_model_keys(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    waves: "Sequence[Wave]",
    bosses: "Sequence[LevelBoss]",
    kinds: "Sequence[EnemyKindDefinition]",
    boss_kinds: "Sequence[BossKindDefinition]",
    area_of: "Callable[[EnemyEntry | None], EnemySpawnArea]",
    extra: list[str],
) -> list[str]:
    """The model keys of the enemies `waves` and `bosses` bring, then `extra` (e.g. the enemies
    that others send out), each once, in that order. One group of each kind is spawned (in the
    area `area_of` gives for the wave's entry) to read its models; unknown kinds give none.
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
