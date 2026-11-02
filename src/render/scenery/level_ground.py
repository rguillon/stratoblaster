# Copyright (c) 2026 Renaud Guillon
"""A level's generated ground (PERF-11, PERF-14): its height field.

Its props' placer (with the roads), generated here or in the background worker, kept for reuse (the
level being played, Retry, and those prefetched).
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.height_field import HeightField
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import RoadNetworkOptions, level_roads
from core.scenery.scenery_level import SceneryLevel, runout_start
from render.scenery.road_chunks import TileRoadChunks
from render.scenery.road_sources import LocalRoadSource, WorkerRoadSource

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

# __pragma__ ("noskip")


class LevelGround:
    """A level's generated ground: its height field and its props' placer (with the roads)."""

    def __init__(
        self, level: SceneryLevel, seed: int, field: HeightField, placer: PropPlacer
    ) -> None:
        self.level = level
        self.seed = seed
        self.field = field
        self.placer = placer
        # Where the street surfaces come from: the worker's, or made here when first asked for.
        self.roads_source: Any = None


class GroundSnapshot:
    """What generating a level's ground made, as plain data (sent back by a worker, PERF-14)."""

    def __init__(self, roads: Any, placer: Any) -> None:
        self.roads = roads
        self.placer = placer


class RunoutSnapshot:
    """What laying the runout's streets of a level's ground added.

    As plain data (the worker sends it after the rest of the ground). Its buildings are placed
    later, chunk by chunk.
    """

    def __init__(self, roads: Any) -> None:
        self.roads = roads


class ChunksReply:
    """Chunks of buildings placed in the worker, as plain data.

    `chunks` in order, `done` when the level has no chunk left.
    """

    def __init__(self, chunks: Sequence[Any], done: bool) -> None:
        self.chunks = chunks
        self.done = done


class RoadsReply:
    """The street surfaces of some chunks (`road_chunks`), and the road atlas's pixels.

    The road atlas's pixels only when they changed (else None).
    """

    def __init__(self, chunks: Sequence[Any], atlas: Any) -> None:
        self.chunks = chunks
        self.atlas = atlas


class _RoadMaker:
    """Makes the street surfaces of a ground's chunks, for the worker's `roads` requests.

    One `TileRoadChunks` (with its atlas) per road look, kept while the look is the same.
    """

    def __init__(self, ground: LevelGround) -> None:
        self.ground = ground
        self.key = ""
        self.road: TileRoadChunks | None = None

    def reply(self, spans: Sequence[Any], look: Any, grid: bool) -> RoadsReply:
        key = _look_key(look)
        if self.road is None or key != self.key:
            roads = self.ground.placer.roads
            self.road = TileRoadChunks(roads.roads, roads.tiles, look, self.ground.field)
            self.key = key
        road = self.road
        chunks: list[Any] = [road.chunk(span[0], span[1], span[2], grid) for span in spans]
        atlas = road.atlas_pixels() if road.atlas_changed() else None
        return RoadsReply(chunks, atlas)


def _look_key(look: Any) -> str:
    """Return the look as a string (its JSON), to tell the looks apart."""
    __pragma__("js", "{}", "return JSON.stringify(look);")
    return ""


class GeneratedInTwo:
    """The ground of a level as plain data, and the calls for the rest of it.

    `ground`, with its first chunks of buildings; `runout()` for the rest of it, `chunks(z)` for the
    chunks up to `z`, asked for as the level scrolls, and `roads(spans, look, grid)` for the street
    surfaces of chunks (`road_chunks`).
    """

    def __init__(
        self,
        ground: GroundSnapshot,
        runout: Callable[[], RunoutSnapshot],
        chunks: Callable[[float], ChunksReply],
        roads: Callable[[Sequence[Any], Any, bool], RoadsReply],
    ) -> None:
        self.ground = ground
        self.runout = runout
        self.chunks = chunks
        self.roads = roads


# The chunks up to this Z are placed before the ground is sent: the level's first screens
# (PERF-16).
FIRST_Z = 1600


def generate_in_two(level: SceneryLevel, seed: int) -> GeneratedInTwo:
    """Generate the ground of `level` from `seed` as plain data, its runout.

    Its chunks of buildings apart (PERF-15): what the worker runs. The roads first (before anything
    is laid), then the first chunks, then `runout()` and `chunks(z)` as they are asked for.
    """
    made = _without_runout(level, seed, None)
    placer = made.placer
    roads = placer.roads.snapshot()
    placer.ensure_placed(FIRST_Z)
    maker = _RoadMaker(made)
    return GeneratedInTwo(
        GroundSnapshot(roads, placer.snapshot()),
        lambda: _add_runout_snapshot(made),
        lambda z: _chunks_reply(made, z),
        maker.reply,
    )


def _chunks_reply(ground: LevelGround, z: float) -> ChunksReply:
    """Return the chunks of `ground` up to `z`, placed now.

    See `PropPlacer.ensure_placed_chunks`.
    """
    placer = ground.placer
    chunks = placer.ensure_placed_chunks(z)
    return ChunksReply(chunks, placer.chunks_done)


def _without_runout(level: SceneryLevel, seed: int, made: GroundSnapshot | None) -> LevelGround:
    """Return the ground of `level` up to its runout: generated, or from what was made before."""
    field = HeightField(level, seed)
    options = RoadNetworkOptions(
        made.roads if made is not None else None,
        runout_start(level),
        None,
    )
    roads = level_roads(field, level.roads, seed, options)
    props = level.props
    sea = level.sea
    placer = PropPlacer(
        field,
        props,
        seed,
        roads,
        sea.level if sea is not None else None,
        made.placer if made is not None else None,
    )
    return LevelGround(level, seed, field, placer)


def _add_runout_snapshot(ground: LevelGround, made: RunoutSnapshot | None = None) -> RunoutSnapshot:
    """Lays the runout's streets of `ground`.

    What they are: generated, or what was made before (the first lay's, even when laid before by the
    placer for its chunks).
    """
    placer = ground.placer
    placer.lay_runout(made.roads if made is not None else None)
    return RunoutSnapshot(placer.runout_added)


def _generate(level: SceneryLevel, seed: int) -> LevelGround:
    """Return the ground of `level` generated here, up to its runout.

    The runout is laid when its chunks need them.
    """
    return _without_runout(level, seed, None)


# Grounds kept for reuse (PERF-11): the level being played, Retry, and those prefetched.
KEPT = 3


class _GroundState:
    """The module state: the kept grounds, the background generator, the failure flag.

    The grounds being generated in the background.
    """

    def __init__(self) -> None:
        self.kept: list[LevelGround] = []
        self.background: Any = None
        self.failed = False
        self.pending: list[Any] = []


_state = _GroundState()


def _truncate(kept: list[Any], count: int) -> None:
    """`kept.length = count` (Transcrypt renames the `length` attribute, so it is raw, ENG-156).

    The parameter keeps its name in the JavaScript: `values` would be renamed `py_values`).
    """
    __pragma__("js", "{}", "kept.length = count;")


def _keep(ground: LevelGround) -> LevelGround:
    _state.kept.insert(0, ground)
    _truncate(_state.kept, min(len(_state.kept), KEPT))
    return ground


def _find(level: SceneryLevel, seed: int) -> LevelGround | None:
    index = -1
    for i in range(len(_state.kept)):
        g = _state.kept[i]
        if g.level is level and g.seed == seed:
            index = i
            break
    if index < 0:
        return None
    ground = _state.kept.pop(index)
    return _keep(ground)


class GroundReplies:
    """What a background generation sends back for a level.

    `ground(made, ask)`, the ground up to the runout (None when the generation failed; `ask(z)` asks
    for the chunks up to `z`), then `runout(made)`, the runout (None when it failed after the
    ground), and `chunks(chunks)` as they come back.
    """

    def __init__(
        self,
        ground: Callable[[Any, Any, Any], None],
        runout: Callable[[Any], None],
        chunks: Callable[[Any], None],
    ) -> None:
        self.ground = ground
        self.runout = runout
        self.chunks = chunks


class _Job:
    """A ground asked for in the background: its level and seed."""

    def __init__(self, level: SceneryLevel, seed: int) -> None:
        self.level = level
        self.seed = seed


class _Slot:
    """The ground a background generation made, once its ground part has come back."""

    def __init__(self) -> None:
        self.ground: LevelGround | None = None


def generate_grounds_with(generator: Any) -> None:
    """Generate the grounds in the background from now on, with `generator` (PERF-14); None.

    Generate them here.
    """
    _state.background = generator
    _state.failed = False


def _remove_job(job: _Job) -> None:
    for i in range(len(_state.pending)):
        if _state.pending[i] is job:
            _state.pending.pop(i)
            return


def _is_pending(level: SceneryLevel, seed: int) -> bool:
    return any(p.level is level and p.seed == seed for p in _state.pending)


def request_level_ground(level: SceneryLevel, seed: int | None = None) -> bool:
    """Asks for the ground of `level` (seed `seed`, default the level's): true when it is ready.

    With a background generator it is generated there, if not already on its way (false until it
    comes back, its runout after it); without one, now.
    """
    if seed is None:
        seed = level.seed
    if _find(level, seed) is not None:
        return True
    if _state.background is None or _state.failed:
        _keep(_generate(level, seed))
        return True
    if _is_pending(level, seed):
        return False
    job = _Job(level, seed)
    _state.pending.append(job)
    replies = _JobReplies(job)
    _state.background(
        level,
        seed,
        GroundReplies(
            lambda made, ask, ask_roads: replies.on_ground(made, ask, ask_roads),
            lambda made: replies.on_runout(made),
            lambda made: replies.on_chunks(made),
        ),
    )
    return False


class _JobReplies:
    """What the background generator's replies to `job` do with the ground they bring."""

    def __init__(self, job: _Job) -> None:
        self._job = job
        self._slot = _Slot()

    def on_ground(self, made: GroundSnapshot | None, ask: Any, ask_roads: Any) -> None:
        """Keep the ground made in the background, unless it failed or was made here meanwhile."""
        level, seed = self._job.level, self._job.seed
        _remove_job(self._job)
        # After a failed background generation, the ground is made here when needed (PERF-18).
        # (`made` comes from the worker: undefined when it failed, so the test is by truth.)
        if not made:
            _state.failed = True
        elif _find(level, seed) is None:
            ground = _keep(_without_runout(level, seed, made))
            self._slot.ground = ground
            # The chunks after the first ones come from the worker, as the level asks for them.
            ground.placer.ask = ask
            ground.roads_source = WorkerRoadSource(ask_roads)

    def on_runout(self, made: RunoutSnapshot | None) -> None:
        """Add the runout to the ground kept, or lay it here if it failed."""
        if not made:
            _state.failed = True
        # Adds nothing to a ground that has its runout already (laid here meanwhile); if it failed,
        # the runout is laid here.
        ground = self._slot.ground
        if ground is not None:
            _add_runout_snapshot(ground, made)

    def on_chunks(self, made: Any) -> None:
        """Hand the chunks the worker placed to the ground kept."""
        ground = self._slot.ground
        if ground is not None and made:
            ground.placer.receive(made)


def road_source_of(ground: LevelGround) -> Any:
    """Where the street surfaces of `ground` come from (see `road_sources`): the worker's.

    When it made the ground, else made here.
    """
    if ground.roads_source is None:
        roads = ground.placer.roads
        ground.roads_source = LocalRoadSource(roads.roads, roads.tiles, ground.field)
    return ground.roads_source


def level_ground(level: SceneryLevel, seed: int) -> LevelGround:
    """Return the ground of `level` from `seed`: kept, or generated now."""
    found = _find(level, seed)
    if found is not None:
        return found
    return _keep(_generate(level, seed))
