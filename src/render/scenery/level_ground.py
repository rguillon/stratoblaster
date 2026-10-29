"""A level's generated ground (P13-R03), ported from `render/scenery/level-ground.ts`: its height
field and its props' placer (with the roads), generated here or in the background worker, kept for
reuse (the level being played, Retry, and those prefetched).
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.height_field import HeightField
from core.scenery.prop_placement import PropPlacer
from core.scenery.road_network import RoadNetworkOptions, level_roads
from core.scenery.scenery_level import SceneryLevel, runout_start

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


class LevelGround:
    """A level's generated ground: its height field and its props' placer (with the roads)."""

    def __init__(
        self, level: SceneryLevel, seed: int, field: HeightField, placer: PropPlacer
    ) -> None:
        self.level = level
        self.seed = seed
        self.field = field
        self.placer = placer


class GroundSnapshot:
    """What generating a level's ground made, as plain data (sent back by a worker, P13-R03)."""

    def __init__(self, roads: Any, placer: Any) -> None:
        self.roads = roads
        self.placer = placer


class RunoutSnapshot:
    """What generating the runout of a level's ground added, as plain data (the worker sends it
    after the rest of the ground)."""

    def __init__(self, roads: Sequence[Any], buildings: Sequence[Any]) -> None:
        self.roads = roads
        self.buildings = buildings


class GeneratedInTwo:
    """The ground of a level as plain data (`ground`), and `runout()` for the rest of it."""

    def __init__(self, ground: GroundSnapshot, runout: Callable[[], RunoutSnapshot]) -> None:
        self.ground = ground
        self.runout = runout


def generate_in_two(level: SceneryLevel, seed: int) -> GeneratedInTwo:
    """Generates the ground of `level` from `seed` as plain data, its runout apart: what the worker
    runs. The ground first, then `runout()` for the rest."""
    made = _without_runout(level, seed, None)
    placer = made.placer
    return GeneratedInTwo(
        GroundSnapshot(placer.roads.snapshot(), placer.snapshot()),
        lambda: _add_runout_snapshot(made),
    )


def _without_runout(level: SceneryLevel, seed: int, made: GroundSnapshot | None) -> LevelGround:
    """The ground of `level` up to its runout: generated, or from what was made before."""
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
    """Adds the runout to `ground`: generated, or what was made before. What it added."""
    placer = ground.placer
    roads = placer.roads.add_runout(made.roads if made is not None else None)
    return RunoutSnapshot(roads, placer.place_runout(made.buildings if made is not None else None))


def _generate(level: SceneryLevel, seed: int) -> LevelGround:
    """The whole ground of `level`, generated here."""
    ground = _without_runout(level, seed, None)
    _add_runout_snapshot(ground)
    return ground


# Grounds kept for reuse (P13-R03): the level being played, Retry, and those prefetched.
KEPT = 3


class _GroundState:
    """The module state: the kept grounds, the background generator, the failure flag and the
    grounds being generated in the background."""

    def __init__(self) -> None:
        self.kept: list[LevelGround] = []
        self.background: Any = None
        self.failed = False
        self.pending: list[Any] = []


_state = _GroundState()


def _truncate(kept: list[Any], count: int) -> None:
    """`kept.length = count` (Transcrypt renames the `length` attribute, so it is raw; the
    parameter keeps its name in the JavaScript: `values` would be renamed `py_values`)."""
    __pragma__("js", "{}", "kept.length = count;")


def _keep(ground: LevelGround) -> LevelGround:
    _state.kept.insert(0, ground)
    _truncate(_state.kept, min(len(_state.kept), KEPT))
    return ground


def _find(level: SceneryLevel, seed: int) -> LevelGround | None:
    index = -1
    for i in range(0, len(_state.kept)):
        g = _state.kept[i]
        if g.level is level and g.seed == seed:
            index = i
            break
    if index < 0:
        return None
    ground = _state.kept.pop(index)
    return _keep(ground)


class GroundReplies:
    """What a background generation sends back for a level: `ground(made)`, the ground up to the
    runout (None when the generation failed), then `runout(made)`, the runout (None when it failed
    after the ground)."""

    def __init__(self, ground: Callable[[Any], None], runout: Callable[[Any], None]) -> None:
        self.ground = ground
        self.runout = runout


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
    """Generates the grounds in the background from now on, with `generator` (P13-R03); None to
    generate them here."""
    _state.background = generator
    _state.failed = False


def _remove_job(job: _Job) -> None:
    for i in range(0, len(_state.pending)):
        if _state.pending[i] is job:
            _state.pending.pop(i)
            return


def _is_pending(level: SceneryLevel, seed: int) -> bool:
    return any(p.level is level and p.seed == seed for p in _state.pending)


def request_level_ground(level: SceneryLevel, seed: int | None = None) -> bool:  # noqa: C901 (the TypeScript flow, kept as is)
    """Asks for the ground of `level` (seed `seed`, default the level's): true when it is ready.
    With a background generator it is generated there, if not already on its way (false until it
    comes back, its runout after it); without one, now."""
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
    slot = _Slot()

    def on_ground(made: GroundSnapshot | None) -> None:
        _remove_job(job)
        # After a failed background generation, the ground is generated here when it is needed.
        # (`made` comes from the worker: undefined when it failed, so the test is by truth.)
        if not made:
            _state.failed = True
        elif _find(level, seed) is None:
            slot.ground = _keep(_without_runout(level, seed, made))

    def on_runout(made: RunoutSnapshot | None) -> None:
        if not made:
            _state.failed = True
        # Adds nothing to a ground that has its runout already (one generated here meanwhile); if
        # it failed, the runout is generated here.
        ground = slot.ground
        if ground is not None:
            # The fallback is made only when the worker sent nothing (`made ?? ...` in the TS).
            if made:
                _add_runout_snapshot(ground, made)
            else:
                _add_runout_snapshot(
                    ground, _add_runout_snapshot(_without_runout(level, seed, None))
                )

    _state.background(level, seed, GroundReplies(on_ground, on_runout))
    return False


def level_ground(level: SceneryLevel, seed: int) -> LevelGround:
    """The ground of `level` from `seed`: kept, or generated now."""
    found = _find(level, seed)
    if found is not None:
        return found
    return _keep(_generate(level, seed))
