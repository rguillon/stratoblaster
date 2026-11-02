# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/level_ground.py`.

The ground generated in two answers (PERF-15), on a level made by hand (ENG-145); the grounds kept
for reuse (PERF-11) and those generated in the background (PERF-14, PERF-18), with a fake
generation; the street surfaces made for the worker.
"""

import json
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.level_builders import flat, make_level, prop_rules, road_rules, section, street_grid
from helpers.sample_level import block_kind, stick_kind

from core.scenery.scenery_level import PropGroupRule
from render.scenery import level_ground
from render.scenery.level_ground import (
    FIRST_Z,
    KEPT,
    GroundSnapshot,
    LevelGround,
    RunoutSnapshot,
    _add_runout_snapshot,
    _chunks_reply,
    _generate,
    _GroundState,
    _Job,
    _remove_job,
    _RoadMaker,
    generate_grounds_with,
    generate_in_two,
    request_level_ground,
    road_source_of,
)
from render.scenery.level_ground import (
    level_ground as ground_of,
)
from render.scenery.road_sources import LocalRoadSource, WorkerRoadSource

# A level of streets, 2000 long, whose last 400 are its runout: its first screens (FIRST_Z), its
# runout's streets and its later chunks of buildings are all there. Its roads go out to X = +-100
# only, so it is quick to generate.
LEVEL = make_level(
    [
        section("a", 10, flat(), streets=street_grid()),
        section("b", 10, flat(), streets=street_grid()),
    ],
    speed=100,
    runout=4,
    roads=road_rules(offscreen_x=100.0),
    props=prop_rules(groups=[PropGroupRule("blocks", 1, [block_kind()])], trees=[stick_kind()]),
)

# The JavaScript-only helpers as the module defines them, taken before the fixture replaces them.
TRUNCATE = level_ground._truncate
LOOK_KEY = level_ground._look_key


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
    assert len(two.ground.placer.buildings) > 0
    assert len(runout_one.roads.roads) > 0
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
    chunks = two.chunks(later)
    assert len(chunks.chunks) > 0
    assert chunks.done
    assert _plain(chunks.chunks) == _plain(_chunks_reply(one, later).chunks)


# -- Kept and background grounds, with a fake generation ------------------------------------------


class FakePlacer:
    """A ground's placer: records the runout laid and the chunks received."""

    def __init__(self, made: GroundSnapshot | None) -> None:
        self.made = made
        self.roads = SimpleNamespace(roads="roads", tiles="tiles")
        self.ask: Any = None
        self.runouts: list[Any] = []
        self.received: list[Any] = []
        self.runout_added = "runout added"

    def lay_runout(self, made: Any) -> None:
        self.runouts.append(made)

    def receive(self, chunks: Any) -> None:
        self.received.append(chunks)


class Generated:
    """The grounds the fake generation made (`made` is what the worker sent, None here)."""

    def __init__(self) -> None:
        self.grounds: list[LevelGround] = []

    def without_runout(self, level: Any, seed: int, made: GroundSnapshot | None) -> LevelGround:
        ground = LevelGround(level, seed, "field", FakePlacer(made))  # type: ignore[arg-type]
        self.grounds.append(ground)
        return ground


class Background:
    """A background generator: records the jobs, answered when the test says.

    With the grounds made here (`generated`) when it is not used.
    """

    def __init__(self, generated: Generated) -> None:
        self.generated = generated
        self.jobs: list[tuple[Any, int, Any]] = []

    def __call__(self, level: Any, seed: int, replies: Any) -> None:
        self.jobs.append((level, seed, replies))


def _level(seed: int = 7) -> Any:
    """Return a level as the kept grounds see it: an object with a seed (told apart by identity)."""
    return SimpleNamespace(seed=seed)


@pytest.fixture
def generated(monkeypatch: pytest.MonkeyPatch) -> Generated:
    made = Generated()
    monkeypatch.setattr(level_ground, "_state", _GroundState())
    # `kept.length = count`.
    monkeypatch.setattr(level_ground, "_truncate", lambda kept, n: kept.__delitem__(slice(n, None)))
    monkeypatch.setattr(level_ground, "_without_runout", made.without_runout)
    return made


@pytest.fixture
def background(generated: Generated) -> Background:
    generator = Background(generated)
    generate_grounds_with(generator)
    return generator


def _kept() -> list[LevelGround]:
    return level_ground._state.kept


def test_the_kept_list_is_truncated_in_javascript_only() -> None:
    """`kept.length = count` is a `__pragma__("js")` body: CPython leaves the list as it is."""
    kept = [1, 2, 3]
    assert TRUNCATE(kept, 1) is None
    assert kept == [1, 2, 3]


def test_the_look_key_is_javascript_only() -> None:
    """`JSON.stringify(look)` is a `__pragma__("js")` body: CPython returns the placeholder ''."""
    assert LOOK_KEY({"lane": 1}) == ""


def test_perf_11_a_ground_asked_for_without_a_background_is_made_now(generated: Generated) -> None:
    level = _level(seed=5)
    assert request_level_ground(level)
    [ground] = generated.grounds
    # The level's own seed by default.
    assert (ground.level, ground.seed) == (level, 5)
    assert _kept() == [ground]


def test_perf_11_a_kept_ground_is_reused(generated: Generated) -> None:
    level = _level()
    first = ground_of(level, 3)
    assert request_level_ground(level, 3)
    assert ground_of(level, 3) is first
    assert len(generated.grounds) == 1


def test_perf_11_a_ground_is_kept_for_its_level_and_seed(generated: Generated) -> None:
    level = _level()
    a = ground_of(level, 1)
    assert ground_of(level, 2) is not a
    # Another level with the same seed: the levels are told apart by identity.
    assert ground_of(_level(), 1) is not a
    assert len(generated.grounds) == 3


@pytest.mark.usefixtures("generated")
def test_perf_11_only_the_last_grounds_used_are_kept() -> None:
    level = _level()
    first = ground_of(level, 0)
    for seed in range(1, KEPT):
        ground_of(level, seed)
    # Using the first again keeps it: the least recently used goes instead.
    assert ground_of(level, 0) is first
    ground_of(level, KEPT)
    assert len(_kept()) == KEPT
    assert first in _kept()
    assert [g.seed for g in _kept()] == [KEPT, 0, KEPT - 1]


def test_perf_14_a_ground_asked_for_with_a_background_is_made_there(
    generated: Generated, background: Background
) -> None:
    level = _level()
    assert not request_level_ground(level, 4)
    # Asked for again while on its way: not asked for twice.
    assert not request_level_ground(level, 4)
    assert [(job[0], job[1]) for job in background.jobs] == [(level, 4)]
    assert generated.grounds == []


def test_perf_14_the_ground_the_background_made_is_kept_with_its_worker_sources(
    generated: Generated, background: Background
) -> None:
    level = _level()
    request_level_ground(level, 4)
    replies = background.jobs[0][2]
    made = GroundSnapshot("roads", "placer")
    replies.ground(made, "ask", "ask roads")
    [ground] = generated.grounds
    assert ground.placer.made is made  # type: ignore[attr-defined]
    assert ground.placer.ask == "ask"
    assert isinstance(ground.roads_source, WorkerRoadSource)
    assert ground.roads_source._ask == "ask roads"
    assert road_source_of(ground) is ground.roads_source
    assert level_ground._state.pending == []
    assert request_level_ground(level, 4)
    assert len(background.jobs) == 1


def test_perf_15_the_runout_and_chunks_from_the_background_go_to_the_kept_ground(
    generated: Generated, background: Background
) -> None:
    request_level_ground(_level(), 4)
    replies = background.jobs[0][2]
    replies.ground(GroundSnapshot("roads", "placer"), "ask", None)
    replies.runout(RunoutSnapshot("runout roads"))
    replies.chunks(["chunk"])
    replies.chunks(None)
    placer = generated.grounds[0].placer
    assert placer.runouts == ["runout roads"]  # type: ignore[attr-defined]
    assert placer.received == [["chunk"]]  # type: ignore[attr-defined]
    assert not level_ground._state.failed


def test_perf_18_a_runout_that_failed_is_laid_here(
    generated: Generated, background: Background
) -> None:
    request_level_ground(_level(), 4)
    replies = background.jobs[0][2]
    replies.ground(GroundSnapshot("roads", "placer"), "ask", None)
    replies.runout(None)
    assert generated.grounds[0].placer.runouts == [None]  # type: ignore[attr-defined]
    assert level_ground._state.failed


def test_perf_18_after_a_failed_background_ground_the_grounds_are_made_here(
    generated: Generated, background: Background
) -> None:
    level = _level()
    request_level_ground(level, 4)
    replies = background.jobs[0][2]
    replies.ground(None, "ask", None)
    assert level_ground._state.failed
    assert generated.grounds == []
    # Nothing came back, so nothing is handed the runout or the chunks.
    replies.runout(None)
    replies.chunks(["chunk"])
    assert request_level_ground(level, 4)
    assert len(generated.grounds) == 1
    assert len(background.jobs) == 1
    # A new generator is tried again.
    generate_grounds_with(background)
    assert not level_ground._state.failed


def test_perf_14_a_ground_made_here_meanwhile_is_kept_over_the_background_one(
    generated: Generated, background: Background
) -> None:
    level = _level()
    request_level_ground(level, 4)
    here = ground_of(level, 4)
    replies = background.jobs[0][2]
    replies.ground(GroundSnapshot("roads", "placer"), "ask", None)
    replies.runout(RunoutSnapshot("runout roads"))
    replies.chunks(["chunk"])
    assert generated.grounds == [here]
    assert here.placer.runouts == []  # type: ignore[attr-defined]
    assert here.placer.received == []  # type: ignore[attr-defined]


def test_perf_14_grounds_on_their_way_come_back_in_any_order(
    generated: Generated, background: Background
) -> None:
    a, b = _level(), _level()
    request_level_ground(a, 1)
    request_level_ground(b, 2)
    background.jobs[1][2].ground(GroundSnapshot("roads", "placer"), "ask", None)
    assert [(job.level, job.seed) for job in level_ground._state.pending] == [(a, 1)]
    background.jobs[0][2].ground(GroundSnapshot("roads", "placer"), "ask", None)
    assert level_ground._state.pending == []
    assert [g.level for g in generated.grounds] == [b, a]


@pytest.mark.usefixtures("generated")
def test_removing_a_job_not_pending_changes_nothing() -> None:
    job = _Job(_level(), 1)
    level_ground._state.pending.append(job)
    _remove_job(_Job(_level(), 1))
    assert level_ground._state.pending == [job]


@pytest.mark.usefixtures("generated")
def test_perf_14_without_a_worker_the_street_surfaces_are_made_here_once() -> None:
    ground = ground_of(_level(), 1)
    source = road_source_of(ground)
    assert isinstance(source, LocalRoadSource)
    assert (source._roads, source._tiles, source._ground) == ("roads", "tiles", "field")
    assert road_source_of(ground) is source


# -- The street surfaces made for the worker ------------------------------------------------------


class FakeTileRoads:
    """A `TileRoadChunks`: names its chunks, and says its atlas changed when the test says."""

    def __init__(self, roads: Any, tiles: Any, look: Any, field: Any) -> None:
        self.args = (roads, tiles, look, field)
        self.changed = True
        TILE_ROADS.append(self)

    def chunk(self, index: int, z_min: float, z_max: float, grid: bool) -> Any:
        return (index, z_min, z_max, grid)

    def atlas_changed(self) -> bool:
        return self.changed

    def atlas_pixels(self) -> Any:
        return "atlas of " + str(self.args[2])


# The `TileRoadChunks` made by the test running.
TILE_ROADS: list[FakeTileRoads] = []


@pytest.fixture
def maker(monkeypatch: pytest.MonkeyPatch) -> _RoadMaker:
    TILE_ROADS.clear()
    monkeypatch.setattr(level_ground, "TileRoadChunks", FakeTileRoads)
    monkeypatch.setattr(level_ground, "_look_key", lambda look: json.dumps(look))
    placer = FakePlacer(None)
    return _RoadMaker(LevelGround(_level(), 1, "field", placer))  # type: ignore[arg-type]


def test_perf_14_the_street_surfaces_of_the_spans_asked_for_are_made(maker: _RoadMaker) -> None:
    reply = maker.reply([[2, 0, 100], [3, 100, 200]], {"lane": 1}, True)
    assert reply.chunks == [(2, 0, 100, True), (3, 100, 200, True)]
    assert reply.atlas == "atlas of {'lane': 1}"
    [road] = TILE_ROADS
    assert road.args == ("roads", "tiles", {"lane": 1}, "field")


def test_perf_14_the_street_maker_is_kept_while_the_look_is_the_same(maker: _RoadMaker) -> None:
    maker.reply([[2, 0, 100]], {"lane": 1}, False)
    TILE_ROADS[0].changed = False
    reply = maker.reply([[3, 100, 200]], {"lane": 1}, False)
    # The atlas did not change: its pixels are not sent again.
    assert reply.atlas is None
    assert len(TILE_ROADS) == 1
    maker.reply([[3, 100, 200]], {"lane": 2}, False)
    assert len(TILE_ROADS) == 2
