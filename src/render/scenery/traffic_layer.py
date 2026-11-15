# Copyright (c) 2026 Renaud Guillon
"""The moving cars of a level (phase 4 review, GFX-CAR-08).

The cars in view are placed again every frame, as thin instances of their own meshes, apart from the
props that stay put.

D-211: where the kit has imposters, a car's body is a picture of it baked from its detailed model
(`imposters.py`), one quad facing the camera; only its lights are real geometry (GFX-CAR-05).
"""

import math

from core.scenery.traffic import CAR_VALUES, CarsInView, Traffic
from render.babylon import float32_array
from render.scenery.imposter_kinds import ImposterKinds, imposter_kinds
from render.scenery.imposters import frame_of
from render.scenery.prop_field import MATRIX_FLOATS, PropField, PropMaterials

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Matrices a batch has room for when made (it doubles when full).
FIRST_ROOM = 16


class InstanceBatch:
    """The instance matrices of one mesh's cars this frame (D-422): its buffer is kept, and grown.

    `floats`: 16 numbers per matrix, the first `count` matrices this frame's. `shown`: whether the
    mesh drew any car the frame before (so it is hidden once, when its last car leaves).
    """

    def __init__(self) -> None:
        self.floats: Any = float32_array(FIRST_ROOM * MATRIX_FLOATS)
        self.count = 0
        self.shown = False


def _room(batch: InstanceBatch) -> int:
    """Return where the next matrix of `batch` goes (its float), making room for it if full."""
    at = batch.count * MATRIX_FLOATS
    if at >= len(batch.floats):
        grown = float32_array(2 * len(batch.floats))
        grown.set(batch.floats, 0)
        batch.floats = grown
    batch.count += 1
    return at


def turned_matrix(floats: Any, at: int, values: list[Any], car: int, scale: float) -> None:
    """Write at float `at` of `floats` the world matrix of the car at `car` of `values`.

    Scaled, turned around Y and moved: the numbers `instance_matrices` gets from Babylon's
    quaternion (`RotationYawPitchRollToRef`) and `Matrix.ComposeToRef`, worked out the same way so
    they are the same to the last bit, without the vectors, the quaternion and the matrix.
    """
    half = values[car + 4] * 0.5
    y = math.sin(half)
    y2 = y + y
    yy = y * y2
    wy = math.cos(half) * y2
    floats[at] = (1 - yy) * scale
    floats[at + 1] = 0
    floats[at + 2] = (0 - wy) * scale
    floats[at + 3] = 0
    floats[at + 4] = 0
    floats[at + 5] = scale
    floats[at + 6] = 0
    floats[at + 7] = 0
    floats[at + 8] = wy * scale
    floats[at + 9] = 0
    floats[at + 10] = (1 - yy) * scale
    floats[at + 11] = 0
    floats[at + 12] = values[car + 1]
    floats[at + 13] = values[car + 2]
    floats[at + 14] = values[car + 3]
    floats[at + 15] = 1


def upright_matrix(floats: Any, at: int, values: list[Any], car: int, scale: float) -> None:
    """Write at float `at` of `floats` the matrix of the imposter of the car at `car` of `values`.

    Scaled and moved, not turned (as `imposter_field.placement_matrix`).
    """
    floats[at] = scale
    floats[at + 1] = 0
    floats[at + 2] = 0
    floats[at + 3] = 0
    floats[at + 4] = 0
    floats[at + 5] = scale
    floats[at + 6] = 0
    floats[at + 7] = 0
    floats[at + 8] = 0
    floats[at + 9] = 0
    floats[at + 10] = scale
    floats[at + 11] = 0
    floats[at + 12] = values[car + 1]
    floats[at + 13] = values[car + 2]
    floats[at + 14] = values[car + 3]
    floats[at + 15] = 1


def _used(batch: InstanceBatch) -> Any:
    """Return the matrices of `batch` this frame (a view of its buffer, none copied)."""
    return batch.floats.subarray(0, batch.count * MATRIX_FLOATS)


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
    for i in range(len(before)):
        if roads[i] is not before[i]:
            return False
    return True


class TrafficLayer:
    """The cars of a level, drawn as thin instances of their models, or of their imposters."""

    def __init__(
        self,
        scene: Any,
        models: Any,
        materials: PropMaterials,
        rules: Any,
        imposter_atlas: Any = None,
        tilt: float = 0,
    ) -> None:
        """`models`: the prop models (only those of the cars' kinds are used).

        `rules`: the cars' rules, or None for a level without cars. `imposter_atlas(kinds)`: an
        `ImposterAtlas` for that many kinds, or None (D-211; the camera tilted by `tilt`).
        """
        self._rules = rules
        self._traffic: Traffic | None = None
        self._roads: list[Any] | None = None
        kinds: list[str] = rules.kinds if rules is not None else []
        self._kinds = kinds
        # The cars in view (D-422): one list kept, and one batch of matrices per kind.
        self._cars = CarsInView()
        self._batches = [InstanceBatch() for _ in kinds]
        cars = {k: v for k, v in models.items() if k in kinds}
        self._imposters: ImposterKinds | None = imposter_kinds(
            scene, cars, kinds, imposter_atlas, tilt
        )
        drawn = self._imposters.models if self._imposters is not None else cars
        self._field = PropField(scene, drawn, materials, None, None)
        # One batch per kind and heading pictured (kind after kind), where the cars are imposters.
        self._headings = self._imposters.headings if self._imposters is not None else 0
        self._frames = [InstanceBatch() for _ in range(len(kinds) * self._headings)]

    @property
    def light_meshes(self) -> list[Any]:
        """Meshes of the headlights and tail lights (e.g. for a glow layer)."""
        return self._field.light_meshes

    @property
    def structure_meshes(self) -> list[Any]:
        """Meshes of the car bodies (e.g. to hide lights behind them in a glow layer).

        Not their imposters: a car's quad stands in front of its far half, and would hide its own
        lights.
        """
        return self._field.structure_meshes

    @property
    def count(self) -> int:
        """Number of cars in view."""
        return self._cars.count

    def update(self, time: float, area: Any, source: TrafficSource) -> None:
        """Places the cars in `area` at `time`.

        New roads (a new seed) get new traffic; roads that go on from the ones before (the runout's,
        reviewer 2026-10-28) only add theirs.
        """
        if self._rules is None:
            return
        self._traffic_of(source).fill(time, area, self._cars)
        if self._imposters is not None:
            # On the first update, not when made: the bake's mesh must not hang from the ground.
            self._imposters.bake_once()
        self._write()
        self._draw()

    def _traffic_of(self, source: TrafficSource) -> Traffic:
        """Return the traffic of the roads of `source`: kept, added to, or made anew."""
        before = self._roads
        traffic = self._traffic
        if traffic is None or source.roads is not before:
            self._roads = source.roads
            if traffic is not None and before is not None and _goes_on(before, source.roads):
                traffic.add(source.roads[len(before) :])
            else:
                traffic = Traffic(source.roads, source.height, self._rules, source.seed)
                self._traffic = traffic
        return traffic

    def _write(self) -> None:
        """Write the matrices of the cars in view into the batches of their kinds (D-422).

        In road order within each kind, and within each of its headings: the order they were
        drawn in when each was a placement, grouped by kind then by heading.
        """
        for batch in self._batches:
            batch.count = 0
        for batch in self._frames:
            batch.count = 0
        values = self._cars.values
        scale: float = self._rules.scale
        headings = self._headings
        batches = self._batches
        frames = self._frames
        for n in range(self._cars.count):
            car = n * CAR_VALUES
            kind = values[car]
            batch = batches[kind]
            # The room first: it may give the batch a larger buffer.
            at = _room(batch)
            turned_matrix(batch.floats, at, values, car, scale)
            if headings > 0:
                batch = frames[kind * headings + frame_of(values[car + 4], headings)]
                at = _room(batch)
                upright_matrix(batch.floats, at, values, car, scale)

    def _draw(self) -> None:
        """Upload the batches that have cars, and hide those that had some the frame before."""
        kinds = self._kinds
        for k in range(len(kinds)):
            batch = self._batches[k]
            if batch.count > 0 or batch.shown:
                self._field.draw_kind(kinds[k], _used(batch))
                batch.shown = batch.count > 0
        if self._imposters is not None:
            self._draw_frames(self._imposters.field)

    def _draw_frames(self, field: Any) -> None:
        """Do the same for the imposters: one batch per kind and heading."""
        kinds = self._kinds
        headings = self._headings
        for i in range(len(self._frames)):
            batch = self._frames[i]
            if batch.count > 0 or batch.shown:
                field.draw_frame(kinds[i // headings], i % headings, _used(batch))
                batch.shown = batch.count > 0
