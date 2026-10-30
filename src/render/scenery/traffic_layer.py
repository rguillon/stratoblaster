"""The moving cars of a level (phase 4 review): the cars in view are placed again every frame, as
thin instances of their own meshes, apart from the props that stay put.

Ported from `render/scenery/traffic-layer.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.traffic import Traffic
from render.scenery.prop_field import PropField, PropMaterials

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class TrafficSource:
    """The roads the cars drive on, the ground under them, and the seed of the level."""

    def __init__(self, roads: list[Any], height: Any, seed: int) -> None:
        self.roads = roads
        self.height = height
        """`height(x, z)`: the ground under the roads."""
        self.seed = seed


def _goes_on(before: list[Any], roads: list[Any]) -> bool:
    """Whether `roads` starts with `before` (the same roads, more after them)."""
    if len(roads) < len(before):
        return False
    for i in range(len(before)):  # noqa: SIM110
        if roads[i] is not before[i]:
            return False
    return True


class TrafficLayer:
    """The cars of a level, drawn as thin instances of their models."""

    def __init__(self, scene: Any, models: Any, materials: PropMaterials, rules: Any) -> None:
        """`models`: the prop models (only those of the cars' kinds are used). `rules`: the cars'
        rules, or None for a level without cars."""
        self._rules = rules
        self._traffic: Traffic | None = None
        self._roads: list[Any] | None = None
        kinds = rules.kinds if rules is not None else []
        cars = {k: v for k, v in models.items() if k in kinds}
        self._field = PropField(scene, cars, materials, None, None)

    @property
    def light_meshes(self) -> list[Any]:
        """Meshes of the headlights and tail lights (e.g. for a glow layer)."""
        return self._field.light_meshes

    @property
    def structure_meshes(self) -> list[Any]:
        """Meshes of the car bodies (e.g. to hide lights behind them in a glow layer)."""
        return self._field.structure_meshes

    @property
    def count(self) -> int:
        """Number of cars in view."""
        return self._field.count

    def update(self, time: float, area: Any, source: TrafficSource) -> None:
        """Places the cars in `area` at `time`. New roads (a new seed) get new traffic; roads
        that go on from the ones before (the runout's, reviewer 2026-10-28) only add theirs."""
        if self._rules is None:
            return
        before = self._roads
        if source.roads is not before:
            self._roads = source.roads
            if self._traffic is not None and before is not None and _goes_on(before, source.roads):
                self._traffic.add(source.roads[len(before) :])
            else:
                self._traffic = Traffic(source.roads, source.height, self._rules, source.seed)
        cars = self._traffic.at(time, area) if self._traffic is not None else []
        self._field.set_chunk(0, cars)
        self._field.sync()
