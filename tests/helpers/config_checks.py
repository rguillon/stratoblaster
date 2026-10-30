"""Invariant checks shared by the tests of `src/game/config/`: the level ids of the four worlds, and
the shape every boss design must have (its parts, its guns and its stages' volleys cross-reference
each other). CPython only: the config records are read as dict-backed objects here."""

from typing import Any

from game.sim.enemy_kinds import ENEMY_KINDS

WORLDS = (1, 2, 3, 4)
LEVELS_PER_WORLD = 5
LEVEL_IDS = [f"{world}-{level}" for world in WORLDS for level in range(1, LEVELS_PER_WORLD + 1)]

SHOT_KINDS = {"aimed", "fan", "ring", "burst", "missiles", "laser"}


def piece_ids(design: Any) -> set[str]:
    """The ids a boss's volleys and guns may name: its core and each of its parts."""
    return {"core"} | {part["id"] for part in design.stats["parts"]}


def assert_boss_design(design: Any) -> None:
    """A boss design is well formed: unique part ids, one stage more than it has parts (each part
    destroyed moves it on, P07-R04), guns and volleys that name pieces of the boss, and volleys of
    a known kind."""
    stats = design.stats
    assert design.id and design.id == stats["model"]
    assert stats["name"]
    assert stats["health"] > 0
    assert stats["radius"] > stats["coreRadius"] > 0
    parts = stats["parts"]
    ids = [part["id"] for part in parts]
    assert len(ids) == len(set(ids))
    assert len(design.stages) == len(parts) + 1
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
    """A world's boss table: one entry per level, each naming a mini boss and a final boss that
    are two different bosses of the game (`bosses`, the ids of every boss design), with a
    non-negative run-out."""
    assert len(table) == LEVELS_PER_WORLD
    for level_id, entry in table.items():
        assert entry["mini"] in bosses, level_id
        assert entry["final"] in bosses, level_id
        assert entry["mini"] != entry["final"], level_id
        assert entry["runout"] >= 0, level_id


def assert_level_difficulty(table: Any) -> None:
    """Enemy factors per level: positive, no higher than twice the base, and never going down
    from one level to the next (P06-R08)."""
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
    """A level's scenery: its id names it (`world-1-1`), it scrolls at a positive speed, and every
    terrain section has a name and a positive length in seconds."""
    assert level.id == "world-" + level_number
    assert level.scrollSpeed > 0
    assert level.sections
    for section in level.sections:
        assert section["name"]
        assert section["seconds"] > 0


SIDES = ("top", "left", "right")


def assert_beats_well_formed(beats: Any, kinds: set[str]) -> None:
    """A wave script's beats (`[seconds, kind, groups, seconds between groups, side, position,
    spread?]`), in time order: each names an enemy kind of the game, has at least one group, and
    comes from a side with its position across that side."""
    times = [beat[0] for beat in beats]
    assert times == sorted(times)
    for beat in beats:
        assert len(beat) in (6, 7), beat
        assert beat[0] >= 0
        assert beat[1] in kinds, beat[1]
        assert isinstance(beat[2], int) and beat[2] >= 1, beat
        assert beat[3] >= 0
        assert beat[4] in SIDES, beat[4]
        assert 0 <= beat[5] <= 1, beat


def enemy_kind_ids() -> set[str]:
    """The ids of every enemy kind of the game (the sim's list of kinds, P05-R24)."""
    return {kind.id for kind in ENEMY_KINDS}
