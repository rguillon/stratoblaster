# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/level_ground.py`.

The ground generated in two answers (PERF-15).
"""

from typing import Any

from game.config.world_1.scenery_coast import LEVEL_1_1
from game.sim.scenery_build import scenery_level
from render.scenery.level_ground import (
    FIRST_Z,
    _add_runout_snapshot,
    _chunks_reply,
    _generate,
    generate_in_two,
)

# The level as the core reads it (`SceneryLevel`), built from its config record.
LEVEL = scenery_level(LEVEL_1_1)


def _plain(value: Any) -> Any:
    """Return the data of a snapshot as plain Python: its attributes, recursively, in order."""
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _plain(item) for key, item in vars(value).items()}
    return value


def test_perf_15_the_ground_made_in_two_answers_is_the_ground_generated_in_one() -> None:
    """The first answer (the roads, the first chunks of buildings) equals the one-shot ground.

    Before its runout; the second (the runout's streets) equals the one-shot runout laid after the
    rest (PERF-15, D-141).
    """
    seed = 7
    two = generate_in_two(LEVEL, seed)

    one = _generate(LEVEL, seed)
    roads_one = one.placer.roads.snapshot()
    one.placer.ensure_placed(FIRST_Z)
    placer_one = one.placer.snapshot()
    runout_one = _add_runout_snapshot(one)

    # The snapshots are not empty, so the equalities below compare real ground.
    assert _plain(two.ground.placer)
    assert _plain(runout_one.roads)
    assert _plain(two.ground.roads) == _plain(roads_one)
    assert _plain(two.ground.placer) == _plain(placer_one)
    assert _plain(two.runout().roads) == _plain(runout_one.roads)


def test_perf_15_the_chunks_asked_for_later_match_the_one_shot_chunks() -> None:
    """The buildings beyond the first chunks are the same as the ones placed in one go.

    They are asked for as the level scrolls.
    """
    seed = 7
    two = generate_in_two(LEVEL, seed)
    one = _generate(LEVEL, seed)
    one.placer.ensure_placed(FIRST_Z)
    _add_runout_snapshot(one)
    later = 4000
    assert _plain(two.chunks(later).chunks) == _plain(_chunks_reply(one, later).chunks)
