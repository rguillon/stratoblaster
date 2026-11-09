# Copyright (c) 2026 Renaud Guillon
"""The veteran enemy kinds (ENM-01)."""

from core.entities.enemy import EnemyKindDefinition
from game.config.enemies import ENEMY_SPAWN_MARGIN as MARGIN
from game.config.enemies_veteran import VETERAN_CONFIG as C
from game.sim.enemies.enemy_helpers import (
    SIDE_MIN_HEIGHT,
    clamp_entry,
    pick_x,
    side_dive_stop_x,
    side_height,
    stop_height,
    top_bounds,
    top_x,
)
from game.sim.enemies.mortar import Mortar
from game.sim.enemies.phantom import Phantom
from game.sim.enemies.wasp import Wasp

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from core.entities.enemy import Enemy, EnemySpawnArea

# __pragma__ ("noskip")


def _top(area: EnemySpawnArea) -> float:
    """Just above the top edge."""
    return area.height + MARGIN


def _entry_x(area: EnemySpawnArea, range_: tuple[float, float]) -> float:
    """X where a kind comes in from the top: the wave's entry (ENM-08), or random in `range_`."""
    entry = area.entry
    if entry is not None and entry.side == "top":
        return top_x(area, clamp_entry(entry.position))
    return pick_x(area.random, range_, area)


def _wasp_group(area: EnemySpawnArea) -> list[Enemy]:
    """Return a group of Wasps side by side (ENM-WASP-07).

    They are kept inside the range coming in from the top (ENM-09).
    """
    group_size = C.wasp.groupSize
    group_spacing = C.wasp.groupSpacing
    entry = area.entry
    if entry is not None and entry.side != "top":
        # From a side (ENM-WASP-11): the group enters in a column, flying in level to a stop.
        left = entry.side == "left"
        spread = (group_size - 1) * group_spacing / 2
        # The whole column stays out of the bottom third.
        y = max(side_height(entry.position) * area.height, SIDE_MIN_HEIGHT * area.height + spread)
        stop_x = side_dive_stop_x(area, left)
        x = -MARGIN if left else area.width + MARGIN
        heights = [y + (i - (group_size - 1) / 2) * group_spacing for i in range(group_size)]
        return [Wasp(x, height, height, stop_x) for height in heights]
    stop_y = stop_height(area, C.wasp.stopRange)
    low, high = top_bounds(area)
    half = ((group_size - 1) * group_spacing) / 2
    middle = min(high - half, max(low + half, _entry_x(area, C.wasp.xRange)))
    return [Wasp(middle - half + i * group_spacing, _top(area), stop_y) for i in range(group_size)]


def _spawn_mortar(area: EnemySpawnArea) -> list[Enemy]:
    return [Mortar(_entry_x(area, C.mortar.xRange), _top(area))]


def _spawn_phantom(area: EnemySpawnArea) -> list[Enemy]:
    stop_y = stop_height(area, C.phantom.placeY)
    return [Phantom(_entry_x(area, C.phantom.xRange), _top(area), stop_y)]


def _all_kinds() -> list[EnemyKindDefinition]:
    """Return the five veteran kinds (ENM-01), in the order of the spec."""
    return [
        EnemyKindDefinition("wasp", "Wasp", _wasp_group),
        EnemyKindDefinition("mortar", "Mortar", _spawn_mortar),
        EnemyKindDefinition("phantom", "Phantom", _spawn_phantom),
    ]


VETERAN_KINDS = _all_kinds()
