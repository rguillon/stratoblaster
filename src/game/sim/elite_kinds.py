"""The elite enemy kinds (P05-R19 to P05-R23)"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyKindDefinition
from core.math.rng import random_in
from game.config.enemies import ENEMY_SPAWN_MARGIN as MARGIN
from game.config.enemies_elite import ELITE_CONFIG as C
from game.sim.enemies.enemy_helpers import clamp_entry, pick_x, top_x
from game.sim.enemies.hive import Hive
from game.sim.enemies.hydra import Hydra
from game.sim.enemies.juggernaut import Juggernaut
from game.sim.enemies.orbiter import Orbiter
from game.sim.enemies.scissor import Scissor

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.enemy import Enemy, EnemySpawnArea  # noqa: E402

__pragma__("noskip")


def _top(area: EnemySpawnArea) -> float:
    """Just above the top edge."""
    return area.height + MARGIN


def _entry_x(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range_`,
    both taken across the area's `top_range` (as in `enemy_kinds.py`).
    """
    entry = area.entry
    if entry is not None and entry.side == "top":
        return top_x(area, clamp_entry(entry.position))
    return pick_x(area.random, range_, area)


def _spawn_hydra(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.hydra.xRange)
    return [Hydra(x, _top(area), C.hydra.stopFraction * area.height)]


def _spawn_orbiter(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = random_in(area.random, C.orbiter.stopRange[0], C.orbiter.stopRange[1]) * area.height
    return [Orbiter(_entry_x(area, C.orbiter.xRange), _top(area), stop_y)]


def _spawn_scissor(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.scissor.xRange)
    return [Scissor(x, _top(area), C.scissor.stopFraction * area.height)]


def _spawn_juggernaut(area: EnemySpawnArea) -> list[Enemy]:
    x = _entry_x(area, C.juggernaut.xRange)
    return [Juggernaut(x, _top(area), C.juggernaut.stopFraction * area.height)]


def _spawn_hive(area: EnemySpawnArea) -> list[Enemy]:
    return [Hive(_entry_x(area, C.hive.xRange), _top(area))]


def _all_kinds() -> list[EnemyKindDefinition]:
    """The five elite kinds (P05-R19 to P05-R23), in the order of the spec."""
    return [
        EnemyKindDefinition("hydra", "Hydra", _spawn_hydra),
        EnemyKindDefinition("orbiter", "Orbiter", _spawn_orbiter),
        EnemyKindDefinition("scissor", "Scissor", _spawn_scissor),
        EnemyKindDefinition("juggernaut", "Juggernaut", _spawn_juggernaut),
        EnemyKindDefinition("hive", "Hive", _spawn_hive),
    ]


ELITE_KINDS = _all_kinds()
