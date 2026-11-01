# Copyright (c) 2026 Renaud Guillon
"""Invariant checks shared by the tests of `src/game/config/`.

The level ids of the four worlds, and the shape every boss design must have (its parts, its guns and
its stages' volleys cross-reference each other). CPython only: the config records are read as
dict-backed objects here.
"""

from typing import Any

from game.sim.enemy_kinds import ENEMY_KINDS

WORLDS = (1, 2, 3, 4)
LEVELS_PER_WORLD = 5
LEVEL_IDS = [f"{world}-{level}" for world in WORLDS for level in range(1, LEVELS_PER_WORLD + 1)]

SHOT_KINDS = {"aimed", "fan", "ring", "burst", "missiles", "laser"}


def piece_ids(design: Any) -> set[str]:
    """Return the ids a boss's volleys and guns may name: its core and each of its parts."""
    return {"core"} | {part["id"] for part in design.stats["parts"]}


def original_parts(design: Any) -> list[Any]:
    """Return a boss's parts there from the start.

    Not its hidden weapons, revealed as it transforms.
    """
    return [part for part in design.stats["parts"] if part.get("reveal") is None]


def assert_boss_design(design: Any) -> None:
    """Assert that a boss design is well formed.

    It has unique part ids and one stage more than it has original parts (each part destroyed moves
    it on, BOSS-20; its hidden weapons, revealed later, keep it on its last). Its guns and volleys
    name pieces of the boss, and its volleys are of a known kind.
    """
    stats = design.stats
    assert design.id
    assert design.id == stats["model"]
    assert stats["name"]
    assert stats["health"] > 0
    assert stats["radius"] > stats["coreRadius"] > 0
    parts = stats["parts"]
    ids = [part["id"] for part in parts]
    assert len(ids) == len(set(ids))
    assert len(design.stages) == len(original_parts(design)) + 1
    known = piece_ids(design)
    for piece in design.guns:
        assert piece in known, piece
    for stage in design.stages:
        assert stage, "a stage fires nothing"
        for shot in stage:
            assert shot["from"] in known, shot["from"]
            assert shot["every"] > 0
            assert shot["shape"]["kind"] in SHOT_KINDS


def assert_world_bosses(table: Any, bosses: set[str]) -> None:
    """Assert that a world's boss table has one entry per level.

    Each entry names a mini boss and a final boss that are two different bosses of the game
    (`bosses`, the ids of every boss design, BOSS-01), with a non-negative run-out (the levels'
    runouts: LVL-1-1-14, LVL-1-2-14, LVL-1-3-14, LVL-1-4-14, LVL-1-5-14; LVL-2-1-13, LVL-2-2-13,
    LVL-2-3-13, LVL-2-4-13, LVL-2-5-13).
    """
    assert len(table) == LEVELS_PER_WORLD
    for level_id, entry in table.items():
        assert entry["mini"] in bosses, level_id
        assert entry["final"] in bosses, level_id
        assert entry["mini"] != entry["final"], level_id
        assert entry["runout"] >= 0, level_id


def assert_level_difficulty(table: Any) -> None:
    """Enemy factors per level are positive and no higher than twice the base.

    They never go down from one level to the next (ENM-22; per world WLD-1-23, WLD-2-21, WLD-3-17,
    WLD-4-19).
    """
    previous = None
    for level_id in sorted(table.keys()):
        factors = table[level_id]
        assert 0 < factors["bulletSpeed"] <= 2, level_id
        assert 0 < factors["fireRate"] <= 2, level_id
        if previous is not None:
            assert factors["bulletSpeed"] >= previous["bulletSpeed"], level_id
            assert factors["fireRate"] >= previous["fireRate"], level_id
        previous = factors


def assert_scenery_level(level: Any, level_number: str) -> None:
    """Assert that a level's scenery is well formed.

    Its id names it (`world-1-1`), it scrolls at a positive speed, and every terrain section has a
    name and a positive length in seconds.
    """
    assert level.id == "world-" + level_number
    assert level.scrollSpeed > 0
    assert level.sections
    for section in level.sections:
        assert section["name"]
        assert section["seconds"] > 0


SIDES = ("top", "left", "right")


def assert_beats_well_formed(beats: Any, kinds: set[str]) -> None:
    """Assert that a wave script's beats are in time order.

    Each beat (`[seconds, kind, groups, seconds between groups, side, position, spread?]`) names an
    enemy kind of the game, has at least one group, and comes from a side with its position across
    that side.
    """
    times = [beat[0] for beat in beats]
    assert times == sorted(times)
    for beat in beats:
        assert len(beat) in (6, 7), beat
        assert beat[0] >= 0
        assert beat[1] in kinds, beat[1]
        assert isinstance(beat[2], int), beat
        assert beat[2] >= 1, beat
        assert beat[3] >= 0
        assert beat[4] in SIDES, beat[4]
        assert 0 <= beat[5] <= 1, beat


def enemy_kind_ids() -> set[str]:
    """Return the ids of every enemy kind of the game (the sim's list of kinds, ENM-01)."""
    return {kind.id for kind in ENEMY_KINDS}
