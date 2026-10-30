"""The levels of a game as shown on the level select screen"""

import math


class LevelEntry:
    """One level as shown on the level select screen (data only)."""

    def __init__(self, id: str, label: str, world: int, level: int, unlocked: bool) -> None:
        """`id` is a stable identifier, e.g. `1-1`; `label` the text shown on the level select
        screen; `world` the 1-based world number; `level` the 1-based level number inside its
        world; `unlocked` is False for a level that is shown but cannot be started.
        """
        self.id = id
        self.label = label
        self.world = world
        self.level = level
        self.unlocked = unlocked


class LevelCatalog:
    """The levels of a game, laid out as one row per world."""

    def __init__(self, columns: int, levels: list[LevelEntry]) -> None:
        """`columns` is the levels per world, i.e. entries per row of the level select grid;
        `levels` lists World 1 level 1 first, row by row.
        """
        self.columns = columns
        self.levels = levels


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    # Transcrypt's float % is not exact (it computes ((a % b) + b) % b), so compare with floor.
    return value - value == 0 and math.floor(value) == value


def build_level_grid(worlds: int, levels_per_world: int, unlocked_ids: list[str]) -> LevelCatalog:
    """Builds a catalog of `worlds` x `levels_per_world` levels labelled `world-level`."""
    if not _is_integer(worlds) or not _is_integer(levels_per_world):
        raise ValueError("worlds and levels_per_world must be integers")
    if worlds < 1 or levels_per_world < 1:
        raise ValueError("A level grid needs one level")
    worlds = int(worlds)
    levels_per_world = int(levels_per_world)
    levels: list[LevelEntry] = []
    for world in range(1, worlds + 1):
        for level in range(1, levels_per_world + 1):
            level_id = str(world) + "-" + str(level)
            levels.append(LevelEntry(level_id, level_id, world, level, level_id in unlocked_ids))
    return LevelCatalog(levels_per_world, levels)


def first_unlocked_level(catalog: LevelCatalog) -> int:
    """Index of the first unlocked level, or 0 when every level is locked."""
    for index, entry in enumerate(catalog.levels):
        if entry.unlocked:
            return index
    return 0
