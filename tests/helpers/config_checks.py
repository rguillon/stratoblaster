# Copyright (c) 2026 Renaud Guillon
"""Invariant checks shared by the tests of `src/game/config/`.

The level ids of the four worlds, and the shape every boss design must have (its parts, its guns and
its stages' volleys cross-reference each other). CPython only: the config records are read as
dict-backed objects here.
"""

from typing import Any

from core.systems.boss_mounts import BossMount
from game.sim.boss_build import mount_specs
from game.sim.enemy_kinds import ENEMY_KINDS

WORLDS = (1, 2, 3, 4)
LEVELS_PER_WORLD = 5
LEVEL_IDS = [f"{world}-{level}" for world in WORLDS for level in range(1, LEVELS_PER_WORLD + 1)]

# The World bosses (a mini and a final boss per level, BOSS-01) come first in `BOSS_DESIGNS`, the
# Lab bosses (specs/bosses/lab/, in the dev viewer only) after them.
WORLD_BOSS_COUNT = 40
LAB_BOSS_COUNT = 50

SHOT_KINDS = {"aimed", "fan", "ring", "burst", "missiles", "laser"}


def piece_ids(design: Any) -> set[str]:
    """Return the ids a boss's volleys and guns may name: its core and each of its parts."""
    return {"core"} | {part["id"] for part in design.stats["parts"]}


def armed_mounts(design: Any) -> dict[str, BossMount]:
    """Return the boss's gun mounts by id, as a world boss arms its volleys from them (BOSS-58)."""
    return {spec.id: BossMount(spec) for spec in mount_specs(design)}


# The bosses whose core fires nothing in any stage, their stages changing only as their parts go:
# their owner's exceptions to BOSS-21 (MB-REEF-WARDEN-08, FB-STORM-PETREL-08).
SILENT_CORES = frozenset({"reef-warden", "storm-petrel"})


def original_parts(design: Any) -> list[Any]:
    """Return a boss's parts there from the start.

    Not its hidden weapons, revealed as it transforms.
    """
    return [part for part in design.stats["parts"] if part.get("reveal") is None]


def assert_boss_design(design: Any) -> None:
    """Assert that a boss design is well formed.

    It has unique part ids and one stage more than it has original parts (each part destroyed moves
    it on, BOSS-20; its hidden weapons, revealed later, keep it on its last), or a single stage when
    its core fires nothing (BOSS-58). Its guns and volleys name pieces of the boss, and its volleys
    are of a known kind.
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
    stage_counts = {len(original_parts(design)) + 1}
    if design.id in SILENT_CORES:
        stage_counts.add(1)
    assert len(design.stages) in stage_counts
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

    Each beat (`[seconds, kind, groups, seconds between groups, side, position, spread?,
    alternate?]`) names an enemy kind of the game, has at least one group, and comes from a side
    with its position across that side.
    """
    times = [beat[0] for beat in beats]
    assert times == sorted(times)
    for beat in beats:
        assert len(beat) in (6, 7, 8), beat
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


# The checks above as lists of what is wrong (empty when well formed): a test asserts once,
# `assert boss_design_problems(design) == []`, and a failure lists every problem.


def boss_design_problems(design: Any) -> list[str]:
    """Return what makes a boss design ill formed (see `assert_boss_design`); empty if none."""
    stats = design.stats
    problems: list[str] = []
    if not design.id:
        problems.append("no id")
    if design.id != stats["model"]:
        problems.append(f"id {design.id!r} is not its model {stats['model']!r}")
    if not stats["name"]:
        problems.append("no name")
    if not stats["health"] > 0:
        problems.append(f"health {stats['health']} is not positive")
    if not stats["radius"] > stats["coreRadius"] > 0:
        problems.append(f"radius {stats['radius']} not above core radius {stats['coreRadius']} > 0")
    ids = [part["id"] for part in stats["parts"]]
    if len(ids) != len(set(ids)):
        problems.append(f"duplicate part ids {ids}")
    return problems + _boss_volley_problems(design)


def _boss_volley_problems(design: Any) -> list[str]:
    """Return what is wrong with a boss's stages, guns and volleys; empty if none."""
    problems: list[str] = []
    if len(design.stages) != len(original_parts(design)) + 1:
        problems.append(
            f"{len(design.stages)} stages for {len(original_parts(design))} original parts"
        )
    known = piece_ids(design)
    problems.extend(
        f"gun on unknown piece {piece!r}" for piece in design.guns if piece not in known
    )
    for number, stage in enumerate(design.stages):
        if not stage:
            problems.append(f"stage {number} fires nothing")
        for shot in stage:
            if shot["from"] not in known:
                problems.append(f"stage {number}: volley from unknown piece {shot['from']!r}")
            if not shot["every"] > 0:
                problems.append(f"stage {number}: volley every {shot['every']}")
            if shot["shape"]["kind"] not in SHOT_KINDS:
                problems.append(f"stage {number}: unknown volley kind {shot['shape']['kind']!r}")
    return problems


def world_bosses_problems(table: Any, bosses: set[str]) -> list[str]:
    """Return what is wrong with a world's boss table (see `assert_world_bosses`); empty if none."""
    problems: list[str] = []
    if len(table) != LEVELS_PER_WORLD:
        problems.append(f"{len(table)} levels, not {LEVELS_PER_WORLD}")
    for level_id, entry in table.items():
        if entry["mini"] not in bosses:
            problems.append(f"{level_id}: unknown mini boss {entry['mini']!r}")
        if entry["final"] not in bosses:
            problems.append(f"{level_id}: unknown final boss {entry['final']!r}")
        if entry["mini"] == entry["final"]:
            problems.append(f"{level_id}: the mini boss is the final boss")
        if not entry["runout"] >= 0:
            problems.append(f"{level_id}: negative run-out {entry['runout']}")
    return problems


def scenery_level_problems(level: Any, level_number: str) -> list[str]:
    """Return what is wrong with a level's scenery (see `assert_scenery_level`); empty if none."""
    problems: list[str] = []
    if level.id != "world-" + level_number:
        problems.append(f"id {level.id!r} is not 'world-{level_number}'")
    if not level.scrollSpeed > 0:
        problems.append(f"scroll speed {level.scrollSpeed} is not positive")
    if not level.sections:
        problems.append("no terrain section")
    for number, section in enumerate(level.sections):
        if not section["name"]:
            problems.append(f"section {number} has no name")
        if not section["seconds"] > 0:
            problems.append(f"section {number} lasts {section['seconds']} s")
    return problems


def beats_problems(beats: Any, kinds: set[str]) -> list[str]:
    """Return what is wrong with a wave script's beats (see `assert_beats_well_formed`)."""
    problems: list[str] = []
    times = [beat[0] for beat in beats]
    if times != sorted(times):
        problems.append("beats out of time order")
    for beat in beats:
        if len(beat) not in (6, 7):
            problems.append(f"{beat}: {len(beat)} fields")
            continue
        if not beat[0] >= 0:
            problems.append(f"{beat}: negative time")
        if beat[1] not in kinds:
            problems.append(f"{beat}: unknown enemy kind")
        if not isinstance(beat[2], int) or beat[2] < 1:
            problems.append(f"{beat}: groups must be a whole number, at least 1")
        if not beat[3] >= 0:
            problems.append(f"{beat}: negative time between groups")
        if beat[4] not in SIDES:
            problems.append(f"{beat}: unknown side")
        if not 0 <= beat[5] <= 1:
            problems.append(f"{beat}: position outside [0, 1]")
    return problems
