"""The veteran enemy kinds (P05-R14 to P05-R18)"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyKindDefinition
from core.math.rng import random_in
from game.config.enemies import ENEMY_SPAWN_MARGIN as MARGIN
from game.config.enemies_veteran import VETERAN_CONFIG as C
from game.sim.enemies.enemy_helpers import clamp_entry, coin, pick_x, top_bounds, top_x
from game.sim.enemies.mantis import Mantis
from game.sim.enemies.minelayer import Minelayer
from game.sim.enemies.mortar import Mortar
from game.sim.enemies.phantom import Phantom
from game.sim.enemies.wasp import Wasp

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.enemy import Enemy, EnemySpawnArea  # noqa: E402

__pragma__("noskip")

# Where the veteran kinds come in, as the first kinds do (`enemy_kinds.py`): kept here, not
# imported from there, as `enemy_kinds.py` imports this file.


def _top(area: EnemySpawnArea) -> float:
    """Just above the top edge."""
    return area.height + MARGIN


def _entry_x(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """X where a kind comes in from the top: the wave's entry (P06-R07), or random in `range_`."""
    entry = area.entry
    if entry is not None and entry.side == "top":
        return top_x(area, clamp_entry(entry.position))
    return pick_x(area.random, range_, area)


def _side_pass(area: EnemySpawnArea, height_fraction: float) -> tuple[bool, float]:
    """A side pass comes from the entry's side, at its height; at random otherwise."""
    entry = area.entry
    if entry is not None and entry.side != "top":
        return (entry.side == "left", clamp_entry(entry.position) * area.height)
    return (coin(area.random), height_fraction * area.height)


def _wasp_group(area: EnemySpawnArea) -> list[Enemy]:
    """A group of Wasps side by side, kept inside the range coming in from the top."""
    group_size = C.wasp.groupSize
    group_spacing = C.wasp.groupSpacing
    stop_y = C.wasp.stopFraction * area.height
    low, high = top_bounds(area)
    half = ((group_size - 1) * group_spacing) / 2
    middle = min(high - half, max(low + half, _entry_x(area, C.wasp.xRange)))
    return [Wasp(middle - half + i * group_spacing, _top(area), stop_y) for i in range(group_size)]


def _spawn_mortar(area: EnemySpawnArea) -> list[Enemy]:
    return [Mortar(_entry_x(area, C.mortar.xRange), _top(area))]


def _spawn_mantis(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = random_in(area.random, C.mantis.stopRange[0], C.mantis.stopRange[1]) * area.height
    return [Mantis(_entry_x(area, C.mantis.xRange), _top(area), stop_y)]


def _spawn_phantom(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = random_in(area.random, C.phantom.placeY[0], C.phantom.placeY[1]) * area.height
    return [Phantom(_entry_x(area, C.phantom.xRange), _top(area), stop_y)]


def _spawn_minelayer(area: EnemySpawnArea) -> list[Enemy]:
    left, y = _side_pass(area, C.minelayer.heightFraction)
    x = -MARGIN if left else area.width + MARGIN
    # Always in the top half, whatever the entry.
    high = max(y, C.minelayer.lowestFraction * area.height)
    return [Minelayer(x, high, "left" if left else "right")]


def _all_kinds() -> list[EnemyKindDefinition]:
    """The five veteran kinds (P05-R14 to P05-R18), in the order of the spec."""
    return [
        EnemyKindDefinition("wasp", "Wasp", _wasp_group),
        EnemyKindDefinition("mortar", "Mortar", _spawn_mortar),
        EnemyKindDefinition("mantis", "Mantis", _spawn_mantis),
        EnemyKindDefinition("phantom", "Phantom", _spawn_phantom),
        EnemyKindDefinition("minelayer", "Minelayer", _spawn_minelayer),
    ]


VETERAN_KINDS = _all_kinds()
