# Copyright (c) 2026 Renaud Guillon
"""The levels of a game as shown on the level select screen."""

import math


class LevelEntry:
    """One level as shown on the level select screen (data only)."""

    def __init__(self, id_: str, label: str, world: int, level: int, unlocked: bool) -> None:
        """Keep the level's id, label, world and level numbers, and whether it is unlocked.

        `id` is a stable identifier, e.g. `1-1`; `label` the text shown on the level select screen;
        `world` the 1-based world number; `level` the 1-based level number inside its world;
        `unlocked` is False for a level that is shown but cannot be started.
        """
        self.id = id_
        self.label = label
        self.world = world
        self.level = level
        self.unlocked = unlocked


class LevelCatalog:
    """The levels of a game, laid out as one row per world (the game's data, UI-LEVEL-02)."""

    def __init__(self, columns: int, levels: list[LevelEntry]) -> None:
        """`columns` is the levels per world, i.e. entries per row of the level select grid.

        `levels` lists World 1 level 1 first, row by row.
        """
        self.columns = columns
        self.levels = levels


def _is_integer(value: float) -> bool:
    """Number.isInteger: false for fractions, infinities and NaN."""
    # Transcrypt's float % is not exact (it computes ((a % b) + b) % b), so compare with floor.
    return value - value == 0 and math.floor(value) == value


def build_level_grid(worlds: int, levels_per_world: int, unlocked_ids: list[str]) -> LevelCatalog:
    """Build a catalog of `worlds` x `levels_per_world` levels (UI-LEVEL-01).

    Each level is labelled `world-level`.
    """
    if not _is_integer(worlds) or not _is_integer(levels_per_world):
        msg = "worlds and levels_per_world must be integers"
        raise ValueError(msg)
    if worlds < 1 or levels_per_world < 1:
        msg = "A level grid needs one level"
        raise ValueError(msg)
    worlds = int(worlds)
    levels_per_world = int(levels_per_world)
    levels: list[LevelEntry] = []
    for world in range(1, worlds + 1):
        for level in range(1, levels_per_world + 1):
            level_id = str(world) + "-" + str(level)
            levels.append(LevelEntry(level_id, level_id, world, level, level_id in unlocked_ids))
    return LevelCatalog(levels_per_world, levels)


def first_unlocked_level(catalog: LevelCatalog) -> int:
    """Index of the first unlocked level, or 0 when every level is locked (UI-LEVEL-06)."""
    for index, entry in enumerate(catalog.levels):
        if entry.unlocked:
            return index
    return 0
